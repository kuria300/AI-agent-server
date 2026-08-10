-- docker runs this automatically ONCE on first postgres start
-- on subsequent starts this file is ignored (data already exists)

-- activate pgvector extension
-- this is what turns normal postgres into a vector database
CREATE EXTENSION IF NOT EXISTS vector;

-- document to store chunks and their GPS locations embedding
-- 768 is the exact number of data points your AI model uses to describe the meaning of a single text chunk.
-- saltiness, sweetess, colorful  this are 3 dimenssion t describe an apple  converted to embed [0.9, 0.0, 0.0] its sour, its npt sweet and not colorful
-- vector(768) locks your database column size to match your AI model perfectly so the math works seamlessly during searches.
CREATE TABLE IF NOT EXISTS document_chunks (
   id   SERIAL PRIMARY KEY,
   session_id   TEXT NOT NULL,
   filename    TEXT NOT NULL,
   chunk_index INTEGER NOT NULL,
   content     TEXT NOT NULL,
   embedding   vector(768),      -- nomic-embed-text = 768 dimensions
   created_at  TIMESTAMP DEFAULT NOW()
);

-- fast similarity search index
-- HNSW index: Safe for empty tables, automatically grows with your data
-- groups data accordingly into blocks 1 for coding so it comes a req and checks only this block if it about coding 
-- IVFFLAT index works when there is data so that it can check using k-means clustering and group
-- cosine measures according to how text talks abput what we want or is not length
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON document_chunks
    USING hnsw (embedding vector_cosine_ops);  