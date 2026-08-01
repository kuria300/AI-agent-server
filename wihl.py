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
"""