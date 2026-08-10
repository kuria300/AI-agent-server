from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # has default values with type hints to prevent error if one passes "True" instead of True
    ollama_base_url : str = "http://127.0.0.1:11434"
    ollama_model : str = "llama3.2:3b"
    app_name : str = 'ai-agent'
    debug: bool = True
    api_key: str = "kingslandingkey"

    # must be present in .env
    database_url : str | None=None

    # redis settings for storing chat history
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = "hello123"
    redis_ttl: int = 604800
    redis_url: str = "redis://:hello123@redis:6379/0"
    weather_api_key: str

    # POSTGRES SETTINGS 
    postgres_host: str ="localhost"
    postgres_user: str = "kingslanding"
    postgres_port: int = 5432
    postgres_password: str = ""
    postgres_db: str ="kingslanding_db"


    class Config:
        env_file = ".env"
        extra = "ignore"  # ignore extra fields in .env file that are not defined in Settings


settings= Settings()

