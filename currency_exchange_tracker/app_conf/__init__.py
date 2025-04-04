"""Declare envs for the configuration module."""

from .load_app_config import (
    APP_SECRET_KEY,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_USER,
    PG4ADMIN_EMAIL,
    PG4ADMIN_PORT,
    POSTGRES_DB_PORT,
    REDIS_PORT,
)

__all__ = [
    "APP_SECRET_KEY",
    "POSTGRES_DB_PORT",
    "PG4ADMIN_EMAIL",
    "PG4ADMIN_PORT",
    "REDIS_PORT",
    "DATABASE_NAME",
    "DATABASE_USER",
    "DATABASE_PASSWORD",
    "DATABASE_PORT",
]
