from peewee import PostgresqlDatabase

db = PostgresqlDatabase(
    "bt_db",
    user = "romain",
    password = "1234",
    host = "localhost",
    port = "5432"
)