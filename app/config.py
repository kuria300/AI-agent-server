from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # has default values with type hints to prevent error if one passes "True" instead of True
    ollama_base_url : str = "http://127.0.0.1:11434"
    ollama_model : str = "llama3.2:3b"
    app_name : str = 'ai-agent'
    debug: bool = False
    api_key: str = "kingslandingkey"

    # must be present in .env
    database_url : str | None=None

    class Config:
        env_file = ".env"


settings= Settings()

