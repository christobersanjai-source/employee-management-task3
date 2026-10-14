from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://employee:employee@db:5432/employee_db"
    secret_key: str = "change-this-secret"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
