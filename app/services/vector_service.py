import os
import uuid
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from app.config import settings
from app.models.document import DocumentChunk


UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# pull the model for embedding to be used 768 dimensions
embeddings_model = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=settings.ollama_base_url
)


async def save_uploaded_document(file_content: bytes, file_name: str)-> str:
    """
    saves raw file to disk
    give it a unique name and save then return file path

    """
    root, ext = os.path.splitext(file_name)
    unique_name = f"{uuid.uuid4()}{ext}"

    filepath = os.path.join(UPLOAD_DIR, unique_name)

    with open(filepath, "wb") as f:
        f.write(file_content)

    return filepath


async def store_document(db: AsyncSession,filepath, filename, session_id) -> int:
    """
    full pipeline - load → split → embed → store in pgvector

    db: AsyncSession is injected bt deoends(get_db)
    return number of chunks stored

    """

    if filepath.endswith(".pdf"):
        loader = PyPDFLoader(filepath)
    else:
        loader = TextLoader(filepath, encoding="utf-8")

    documents = loader.load()
    print(f"Loaded {len(documents)} pages")


      # RecursiveCharacterTextSplitter tries to split on:
    # paragraph breaks first -then newlines -then sentences →-hen words
    splitter= RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = splitter.split_documents(documents=documents)
    print(f'split into {len(chunks)} chunks')

    # we first remove empty chunks unwanted whitespaces then giv to embedding model
    texts = [chunk.page_content.strip() for chunk in chunks if chunk.page_content.strip()]
    print(f"Embedding {len(texts)} chunks...")

    embeddings= embeddings_model.embed_documents(texts)

    # we take a chunk of text and loop througgh words and put its corrsponding embeddings into db and we do that for all chhunks
    chunk_objects =[DocumentChunk(session_id=session_id, filename=filename, chunk_index=i, content=texts[i], embedding=embeddings[i]) for i in range(len(texts))]

    # save and commit to db
    db.add_all(chunk_objects)
    await db.commit()

    stored = len(chunk_objects)
    print(f"Stored {stored} chunks for session: {session_id}")
    return stored


async def search_document(db: AsyncSession, query:str, session_id: str, top_k:int =5) -> str:
    """
    find the most relevant chunks for a query string using cosine similarity

     steps:
    1. embed the query with same model
    2. pgvector compares query embedding to all stored embeddings
    3. returns top_k closest chunks (most semantically similar)
    4. formats them for the LLM to read

    return
    Relevant content from your uploaded documents:

    [Source: rules.pdf | chunk 2 | match: 88.5%]
    Refunds are processed within 3 to 5 business days of request submission...

    ---

    [Source: rules.pdf | chunk 3 | match: 74.1%]
    To submit a return, navigate to settings and click cancel subscription...

    Key Rule of Thumb:Cosine Distance:
    $0$ is closest, $2$ is furthest. (Smaller is better).Cosine Similarity / Dot Product ($S$): $+1$ is closest, $-1$ is furthest. (Larger is better).

    """

    # we embed the query into 768 dimensions of numbers as it uses nomic-embed-text
    query_embedding = embeddings_model.embed_query(query)

    # this stmt queries db and gets filename, content and  chunk then we do cosine distance and lable row similarity and order y best matching to least and limit to 5    
    stmt = (
           select(DocumentChunk.content, DocumentChunk.filename, DocumentChunk.chunk_index, (
          1 - DocumentChunk.embedding.cosine_distance(query_embedding)).label("similarity"),)
          ).where(DocumentChunk.session_id == session_id).order_by(DocumentChunk.embedding.cosine_distance(query_embedding)).limit(top_k)


    result = await db.execute(stmt)
    rows = result.fetchall()

    if not rows:
        return "No relevant content found in your uploaded documents."

    chunks_text = []
    for content, filename, chunk_idx, similarity in rows:
        chunks_text.append( f"[Source: {filename} | chunk {chunk_idx} | match: {similarity:.1%}]\n"f"{content}")

    print(f"Found {len(rows)} relevant chunks")
    return (
        f"Relevant content from your uploaded documents:\n\n"
        + "\n\n---\n\n".join(chunks_text)
    )









