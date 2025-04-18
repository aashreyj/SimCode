import os

class Settings:
    DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://synccode_user:strongpassword@localhost/synccode_db"
)
    API_PREFIX = "/api/v1"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
settings = Settings()