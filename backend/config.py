from peewee import PostgresqlDatabase

db = PostgresqlDatabase(
    "bt_db",
    user = "romain",
    password = "1234",
    host = "localhost",
    port = "5432"
)

# BKK Futár API Configuration
BKK_API_KEY = "61f16316-3fac-4cd7-a4f0-77feac9976ab"
BKK_API_BASE_URL = "https://futar.bkk.hu"  # Using HTTPS for secure communication