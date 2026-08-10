# read_file, calculator, search_news, get_weather
# docstrings are important to ai agents eg langchain
import os
import requests
import asyncio
from langchain.tools import tool
from sympy import sympify, N, SympifyError, sin, cos, tan, sqrt, log, exp, pi, E
from duckduckgo_search import DDGS
from app.services.vector_service import search_document as vector_search
from app.config import settings
from app.db import get_session_factory


@tool
def read_file(filepath: str)-> str:
    """
    Read the contents of a single text file from the local filesystem and return
    its full content along with the file path and line count.

    USE THIS WHEN:
    - The user wants you to read, review, analyze, explain, debug, or fix code
      or text that lives in a specific file on disk.
    - The user gives you a file path directly, or refers to "this file",
      "the file at ...", or a filename they've already told you about.

    DO NOT USE THIS FOR:
    - Documents the user uploaded through the chat interface (PDFs, .txt, .docx,
      etc.) — those are handled by search_documents instead, not read_file.
    - Fetching content from a URL or the web — use search instead.

    INPUT FORMAT:
    A full, absolute file path as a string.
    Examples:
    - '/home/user/project/main.py'
    - '/app/app/services/agent.py'
    - '/home/user/notes/todo.txt'

    LIMITS:
    - Only works on files under 1MB. Larger files will be rejected — ask the
      user to paste the specific section they need help with instead.
    - Only works on plain text files. Binary files (images, executables, etc.)
      will return an error instead of their raw bytes.

    RETURNS:
    A string containing the file path, total line count, and the full file
    content — or a clear error message if the file doesn't exist, isn't
    readable, is a directory, is too large, or isn't valid text.
    """

    try:
        # check file exists
        if not os.path.exists(filepath):
            return f"File not found: '{filepath}'"

        # check it is a file not a folder
        if not os.path.isfile(filepath):
            return f"'{filepath}' is a directory, not a file"

        # limit size — dont dump huge files into LLM context
        size_mb = os.path.getsize(filepath) / 1024 / 1024
        if size_mb > 1:
            return (f"File too large.Please paste the specific section you need help with.")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        line_count = content.count("\n") + 1 # count lines + 1

        return (
            f"File: {filepath}\n"
            f"Lines: {line_count}\n"
            f"{content}"
        )
    except PermissionError:
        return f"Permission denied reading '{filepath}'"
    except UnicodeDecodeError:
        return f"Cannot read '{filepath}' — file appears to be binary not text"
    except Exception as e:
        return f"File read error: {str(e)}"



@tool
def search_documents(query: str) -> str:
    """
       Search content the user has uploaded through the chat (PDFs, .txt, .docx,
    and similar documents) using semantic vector search, and return the most
    relevant matching chunks of text.

    USE THIS WHEN:
    - The user asks a question about a document they uploaded.
    - The user just uploaded a document and you need to describe what it is
      or what it contains.
    - The user refers to "the file I uploaded", "the document", "this PDF",
      or similar, without pasting the content themselves.

    DO NOT USE THIS FOR:
    - Files on the local filesystem the user gives you a path to — use
      read_file instead.
    - General web knowledge or current events — use search instead.

    HOW TO WRITE THE QUERY:
    - Write your own query in your own words, based on what the user actually
      asked. Never copy any example text from this description verbatim —
      the examples below are illustrations of the STYLE of query to write,
      not literal text to reuse.
    - Keep it short and specific to the user's actual question.
    Examples of GOOD queries (write something like these, tailored to the
    real conversation, never copy them word-for-word):
    - "pricing and cost breakdown"
    - "key findings and conclusions"
    - "steps to set up the project"
    - "summarize the contents"

    IF THE USER UPLOADED A DOCUMENT WITHOUT ASKING A SPECIFIC QUESTION:
    - Do not invent a narrow or oddly specific question.
    - Instead, search broadly — something like "summary", "overview", "main
      topic", or "what is this document about" — so you can describe what
      the document is and what it generally contains in your Final Answer.

    AVOID REPEATED CALLS:
    - Do not call this tool more than once with the same or a near-identical
      query. If a call already returned relevant results, use them to write
      your Final Answer instead of searching again.
    - If a search genuinely returns nothing useful, try ONE reformulated
      query — do not repeat the exact same input.

    RETURNS:
    A string with the most relevant chunks of text found in the user's
    uploaded documents, each labeled with its source filename and a rough
    match score — or a message saying nothing relevant was found.

    """
    async def perform_search():
        session_factory = get_session_factory()
        
        # Open the database session safely
        async with session_factory() as db:
            # Call your vector search and pass the db session
            return await vector_search(
                query=query,
                session_id="kingslanding_local",
                db=db
            )
    try:
        result = asyncio.run(perform_search())
        return result
    except Exception as e:
        return f"error {str(e)}"



@tool
def calculator(expression: str) -> str:
    """
        Evaluate a mathematical expression and return the numeric result.

    USE THIS WHEN:
    - The user asks any math question — arithmetic, algebra-style expressions,
      trigonometry, roots, logs, exponents, or constants like pi.
    - The user wants you to compute, calculate, or check a numeric result,
      rather than just explain a math concept in words.

    DO NOT USE THIS FOR:
    - Purely conceptual math questions with no expression to evaluate (e.g.
      "explain what a derivative is") — answer those directly instead.

    SUPPORTED OPERATIONS:
    - Basic arithmetic: +, -, *, /, ** (power)
    - Trig functions: sin, cos, tan (radians)
    - Other functions: sqrt, log, exp
    - Constants: pi, E

    IMPORTANT LOG BEHAVIOR:
    - log(x) with ONE argument defaults to base 10, e.g. log(100) = 2
    - For natural log (base e), pass e explicitly: log(x, e)
    - For a custom base, pass it as the second argument: log(100, 10)

    INPUT FORMAT:
    A single math expression as a plain string, using standard notation.
    Examples:
    - '10 * 5 + 3'
    - 'sqrt(16) + 5'
    - 'log(100, 10)'
    - 'sin(pi / 2)'
    - '2 ** 10'

    RETURNS:
    A string with the computed result, e.g. 'Result: 53' — or a clear error
    message if the expression has invalid syntax or can't be evaluated.
    """
    try:
        local_dict = {
            "sin": sin, "cos": cos, "tan": tan,
            "sqrt": sqrt, "log": log, "exp": exp,
            "pi": pi, "E": E
        }

        # parse the expresssion to format understood log(100) -> sympy.log(Integer(100))
        expr = sympify(expression, locals=local_dict)

        # we change to base 10 if one arg passed log(100)
        expr = expr.replace(
            lambda x : x.is_Log() and len(x.args) == 1,
            lambda x: log(x.args[0], 10) 
        )

        result = N(expr)

        if result.is_integer:
            result = int(result)
            
        return f"Result: {result}"

    except SympifyError:
        return "Error: Invalid math expression. Check syntax."
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def search(query: str, timelimit: str= "m")-> str:
    """
    Search the general web using DuckDuckGo and return a summary of the most
    relevant recent results.

    USE THIS WHEN:
    - The user asks about general topics, technical documentation, tutorials,
      or articles you don't already know confidently.
    - The user wants websites, tools, or deeper research beyond recent headlines.
    - The user asks about current events, breaking news, or "what's happening"
      right now.
    - The user needs the latest updates in fields like:
      Technology (AI, software, hardware, tech news),
      Medicine (new treatments, drug approvals, health studies),
      Law (new regulations, court rulings, legal tech),
      or general news.
    - The user explicitly asks for "recent", "latest", or a specific
      current year's information.
    - The user wants to brainstorm a new idea and would benefit from real
      current material, examples, or real-world pros and cons.

    DO NOT USE THIS FOR:
    - Content the user already uploaded — use search_documents instead.
    - Simple math — use calculator instead.
    - Weather — use get_weather instead.
    - Anything you already know confidently and doesn't need current data —
      just answer directly.

    TIMELIMIT OPTIONS (second argument, optional):
    - 'd' — restrict results to the past day
    - 'w' — restrict results to the past week
    - 'm' — restrict results to the past month (default)
    - 'y' — restrict results to the past year
    - None — no time restriction, search all time

    INPUT FORMAT:
    A concise, specific search query describing the topic and any relevant
    context (do not pass a full sentence/question — pass keywords/phrases).
    Examples:
    - "AI developments in healthcare 2026"
    - "New FDA drug approvals June 2026"
    - "Recent legal changes for AI in Europe"
    - "Latest news on quantum computing"

    RETURNS:
    A string summarizing the top matching articles — titles, short excerpts,
    and source URLs — or a message saying no results were found.
    """

    try:
        results=[]

        with DDGS() as ddgs:
            web_results= ddgs.text(query, max_results=5, timelimit=timelimit)

            for item in web_results:
                results.append(
                    f"• {item.get('title')}\n"
                    f"  {item.get('body', '')[:200]}...\n"
                    f"  URL: {item.get('href', '')}"
                )
        if not results:
            return f"No web results found for '{query}'"
        # print on new line skip a blank line 
        return f"Web results for '{query}' (timelimit={timelimit}):\n\n" + "\n\n".join(results)

    except ImportError:
        return "duckduckgo-search not available"
    except Exception as e:
        return f"Search error: {str(e)}"

@tool
def get_weather(city: str)-> str:
    """
    Fetch current, real-time weather conditions for a specified location.

    USE THIS WHEN:
    - The user asks about the current weather, temperature, or conditions
      in any city or location.
    - The user asks something like "what's it like in ___ right now" or
      "do I need an umbrella in ___".

    DO NOT USE THIS FOR:
    - Historical weather data or long-range forecasts — this tool only
      returns current conditions.
    - General climate questions not tied to a specific place right now.

    LOCATION INPUT FORMAT:
    - City name alone: 'London', 'Nairobi'
    - City name with country code: 'Paris, FR'
    - City name with state and country code (USA locations only): 'Austin, TX, US'

    NOTE: State codes are only supported for locations inside the USA. Do
    not include a state code for cities in other countries.

    RETURNS:
    A string containing the location's country, general weather condition,
    a short description, temperature in °C, humidity percentage, wind speed,
    and visibility — or a clear error message if the city can't be found,
    the request times out, or there's no internet connection.
    """
    try:
        from app.config import settings

        api_key=settings.weather_api_key

        url =f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

        response = requests.get(url=url, timeout=5)
        data= response.json()

        if response.status_code != 200:
            return F"couldn't find weather for {city}- please check if city exists: {data.get('message', 'unknown error')}"

        temp = data["main"]["temp"]
        humidity= data["main"]["humidity"]
        main = data["weather"][0]["main"]
        description = data['weather'][0]["description"]
        wind_speed = data["wind"]["speed"]
        visibility = data['visibility']
        country= data["sys"]["country"]

        return (
            f"weather in {city} : {country}:\n"
            f"main: its {main}"
            F"description: {description}"
            f"Temperature:{temp}°C \n"
            f"Condition:{description}\n"
            f"Humidity:{humidity}%\n"
            f"Wind speed:{wind_speed} m/s"
            f"visibility: {visibility}"
        )
    except requests.Timeout:
        return "please try again, Timeout"
    except requests.ConnectionError:
        return "No internet connection, can't fetch weather, please try again"
    except Exception as e:
        return f"get waether error: {str(e)}"












