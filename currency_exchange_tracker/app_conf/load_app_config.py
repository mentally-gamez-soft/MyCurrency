"""Configure the application with envs."""

import os

from dotenv import load_dotenv

verif = load_dotenv()
DATABASE_NAME = os.getenv("DATABASE_NAME")
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
POSTGRES_DB_PORT = os.getenv("POSTGRES_DB_PORT")
PG4ADMIN_EMAIL = os.getenv("PG4ADMIN_EMAIL")
PG4ADMIN_PORT = os.getenv("PG4ADMIN_PORT")
REDIS_PORT = os.getenv("REDIS_PORT")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_PORT = os.getenv("DATABASE_PORT")
