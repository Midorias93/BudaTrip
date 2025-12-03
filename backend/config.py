import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "romain")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "1234")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "bt_db")