"""
pip and npm are slow for when we install a package eg.cors the hard-drive installs the packaege from internet and instead photocopys into project
which takes time 

uv is fast cuase when we uv add cors it checks if we have it in hard-drive if so creates a hard-link (like an exact copy into my project) if not intalls 
in hard-drive and creates a hard-link fast takes 0.001 second so we have same copy in project like in hard-drive
and when we change the cors files the hard-link is destroyed and inorder to restore 

uv is incredibly fast because when it installs a package, it downloads it to a central cache and creates a "hard link" 
(a shortcut that points to the exact same physical spot on the hard drive) to your project folder instead of copying the file.

uv cache clean
uv sync


uv_compile_bytecode=1   
helps copile the pacakages insytalled by uv form .py to .pyc thus reduce cold-start time as no more compiling again (applys to pcakages alone)
uv_link_mode=copy
this helps us just run a copy as uv can't create a hard-link between 2 filesystems docker ccache mount and container 
A Docker cache mount acts like a completely separate USB drive plugged into your container during the build. 
You cannot create a hard link across two different hard drives. When uv tries, it fails, throws a warning, and falls back to copying the files


Docker Cache Mounts: In Docker, you can speed up builds using a feature called a cache mount (e.g., RUN --mount=type=cache,target=/root/.cache/uv). This tells 
Docker to keep a persistent folder of downloaded packages across different builds so you don't have to re-download them every time you change your code.



########we have redis driiver installed so we need to know where redis-server is########### to send command
In Python: The installed redis package has no idea where your database actually lives. Is it on your laptop? Is it in a Docker container? 
Is it hosted in a massive data center in Tokyo? By writing redis.Redis(...), you are explicitly telling the Python driver: 
"Wake up, and open a live network tunnel to the server located at the address redis on port 6379."



day2
so when im running asyn def functions with await it goes to the eventloop 
where theres a single thread shared so here there's concurrency when a async code reaches await it releases the thread as it waits and 
task b enters and same happens... all are in motion so concurrent not parallel

swhen im ruuning a def func synchronous code it goes to thread pool 40 slots are there and 
if its not a cpu bound task when it reaces the blocking code it releases the GIL which is passed to other as its shared by all 40 slots and 
when its back it get the GIL and other ques this hppens so fast that it looks like parra;llelisma
processPollExecutor is mainly for cpu work we ofload to it in our fastapi app  we create a separate worker insisde our app with own GIL, memory and thread pool so when we have cpu bound task we offload to it and it runs in parallel with our main app thread pool





localhost inside a container is the container itself, not your host machine. If you want to access a service running on your host machine from inside a Docker container, 
you can use the special hostname host.docker.internal. This hostname resolves to the internal IP address of the host machine, allowing containers to communicate with services running on the host.
but this host.docker.internal is not available on linux so we need to add extra_hosts in docker-compose.yaml to make it work
the extra_hosts entry maps host.docker.internal to the host-gateway, which is a special IP address that Docker provides to allow containers to access the host machine.
172.17.0.1 also works but cant be used as it may change based on host's network configuration, so host-gateway is more reliable and portable across different environments.

ip addr show docker0 it shows the ip address of docker0 bridge network




To fix this, you strap a magical smart backpack onto him. That smart backpack is the RunnableWithMessageHistory.

Here is what is happening piece by piece:

runnable=executor: This is Robot-O himself. He knows how to use tools and think through problems.

get_session_history=build_memory_from_redis: This is the instruction manual for the backpack telling it how to call the librarian to fetch your personal notebook.

input_messages_key="input" & output_messages_key="output": These are the mail slots. Your question goes into the "input" slot, and Robot-O's final answer comes out of the "output" slot.

history_messages_key="chat_history": This is where the backpack stuffs all the old notes it reads from the notebook so Robot-O can read them before he starts talking.


LangChain separates this out because of runtime flexibility. Everything inside the configurable dictionary is meant for dynamic data that changes on the fly for every single user request—like a user's session_id, or dynamically swapping out an AI model variant.






When the LLM decides which tool to call, it never sees your Python code. It only sees what @tool generates:
{
  "name": "get_weather",
  "description": "Fetch current weather information for a specified location. LOCATION INPUT FORMAT: Pass as 'city name' or 'city name, state code, country code'...",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string"
      }
    },
    "required": ["location"]
  }
}




so when u upload pdf it gets saved into uploads(just to make sure pdf is safely saved)   since a pdf is too big for an AI to read all at once, it would get confused or un out of memory since even my context is 2048 so it splits into chunks like chopping a page at a time of a 500 page book.
noe i have chunks sine comp cant understand human words we turn each chunk into an embedding- a map of meaning long list of gps umbers that tell u exactly where paragraph belons on map of meaning...we save embedding to pg vector
"""



"""
Think of an Embedding as a "Recipe"Imagine you want a computer to understand the flavor of different foods. 
A computer cannot taste food, so you have to give it a list of numbers representing the ingredients.
If you use a simple 3-dimension recipe, you can only track 3 flavors:SweetnessSaltinessSpicinessAn Apple might look like this: [0.9, 0.0, 0.0] (Very sweet, not salty, not spicy).A Potato Chip might look like this: [0.0, 0.8, 0.0] (Not sweet, very salty, not spicy).Because those lists of numbers are different, 
the computer can tell that an apple and a potato chip taste completely different.What is a 768-Dimension Recipe?Human language is much more complicated than basic food flavors. A paragraph of text can talk about politics, coding, emotions, space, history, or medical advice all at once.To capture the exact "flavor" of a paragraph's meaning, a local AI model like nomic-embed-text doesn't just use 3 ingredients. 
It uses a massive recipe with 768 unique ingredients!When you pass a text chunk into the AI model, the AI looks at the words and creates a strict list of 768 precise decimals.
Column 1 measures how much the text relates to technology.Column 20 measures how formal or casual the tone is.Column 500 measures if it talks about money.... and 765 other hidden linguistic traits.When the model finishes looking at a chunk, it hands you a list of 768 numbers. That list is the Embedding.

The Question Gets Its Own 768 NumbersWhen a user types a question like: "What is the company's profit?", that question is also English. 
The computer must immediately convert the question into its own list of 768 numbers using the exact same AI model.


                  Slot 1      Slot 2      Slot 3             Slot 768
Question Vector: [ 0.81   ,  -0.12   ,   0.45   , ... ... ,   0.02   ]
                    ×           ×           ×                    ×
Chunk 1 Vector:  [ 0.79   ,  -0.10   ,   0.41   , ... ... ,   0.03   ]

so we add all slots and get Dot product we do cosine distnace    Distance = 1 - dot product    1-0 = 1 complet opposoiete if 1-1=0 match 
ORDER BY embedding <=> query_embedding LIMIT 2;



How IVFFlat Works: The Neighborhood Analogy 
Imagine you have a giant city with thousands of houses (your text chunks).
 To deliver mail quickly, you divide the city into 100 neighborhoods (which matches your lists = 100 code).
   Each neighborhood gets a center point, like a park.When a query comes in, the database looks at the 100 parks, 
   finds the closest one, and only searches the houses inside that single neighborhood. 
This makes searches incredibly fast because it ignores the other 99 neighborhoods.
To create those 100 neighborhood center points (parks), IVFFlat looks at the data using a math algorithm called K-means clustering.
"""



"""
inold way db.session.create() this session is a helper created   
by now we create a single factory for creating helpers and inject in route so db. create is ok still has session its just that its i njected in route
"""





"""
ENGINE (singleton — created once)
= the pipeline manager
= holds a POOL of 30 connections max
  → 10 always open (pool_size=10)
  → 20 extra when busy (max_overflow=20)
  → 31st request? WAITS until one frees up

SESSION FACTORY (singleton — created once)
= the helper blueprint/stamp
= knows HOW to create helpers (sessions)
= knows which engine/pool to use
= never changes, just stamps out sessions

SESSION (created per request — many exist at once)
= one helper per request
= born when request arrives (Depends(get_db))
= dies when request finishes (async with closes it)
= talks to DB through a pool connection
= 100 users = 100 sessions


100 users hit /files/upload at same time
        ↓
FastAPI spins up 100 async tasks
        ↓
Each task hits Depends(get_db)
        ↓
session factory stamps out 100 sessions
        ↓
100 sessions compete for 30 pool connections

User 1-30   → grab a connection immediately ✓
User 31-100 → wait in queue

But async saves you here:
User 1 grabs connection → starts query → hits await
        ↓
Python says "you're waiting? let me serve User 31"
User 31 grabs freed connection → starts query → hits await
        ↓
Python switches back to User 1 → query done → returns result
        ↓
connection goes back to pool → User 32 grabs it
        ↓
keeps cycling fast — no thread blocking
"""