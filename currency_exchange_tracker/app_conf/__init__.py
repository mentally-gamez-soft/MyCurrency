"""Declare envs for the configuration module."""

from .config import AppConfig, EnvLoader

__all__ = ["app_env"]

env_loader = EnvLoader()
env_loader.get_env_config()
config = AppConfig(env_loader.env)
app_env = config.get_application_env()
