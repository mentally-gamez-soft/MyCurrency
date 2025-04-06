"""Configuration file for the application."""

import os
from io import StringIO
from os import environ as env
from typing import Union, get_type_hints

import dotenv_vault.main as vault
from dotenv import load_dotenv as std_load_dotenv
from dotenv_vault import load_dotenv


class ConfigurationNotFoundException(Exception):
    """Raised when the configuration files of the application is not available."""

    pass


class EnvLoader:
    """Load the environment variables."""

    def __init__(self, env_path: str = ".") -> None:
        """Init the env variables.

        Args:
            env_path (str, optional): the path to the application .env file. Defaults to '.'.
        """
        self.app_env_path = env_path
        self.vault = vault
        self.env = env

    def __check_available_env(self) -> bool:
        return os.path.exists(".env.keys")

    def __load_standard_env(self) -> bool:
        """Load all the environment variables.

        Returns:
            bool: True if the environment variables are loaded, False otherwise
        """
        return std_load_dotenv(os.path.join(self.app_env_path, ".env"))

    def __load_cyphered_env(self) -> bool:
        """Load all the environment keys pass.

        Returns:
            bool: True if the environment variables are loaded, False otherwise
        """
        return self.__check_available_env() and std_load_dotenv(".env.keys")

    def __load_env_key(self) -> str:
        """Load all the encrypted environment variables.

        Returns:
            str: The encrypted env variable
        """
        self.env["DOTENV_KEY"] = self.env.get("DOTENV_KEY_DEVELOPMENT", None)
        return self.env["DOTENV_KEY"]

    def __load_decyphered_env(self):
        if not std_load_dotenv(os.path.join(self.app_env_path, ".env.vault")):
            raise ConfigurationNotFoundException(
                "The .env.vault file does not exists"
            )

        try:
            dot_env_vault = self.env.get("DOTENV_VAULT_DEVELOPMENT", None)

            if dot_env_vault is None:
                raise ConfigurationNotFoundException(
                    "The .env.vault file does not exists"
                )

            stream = self.vault.parse_vault(StringIO(dot_env_vault))
            load_dotenv(stream=stream, override=False)
        finally:
            os.unsetenv("DOTENV_KEY")

    def get_env_config(self):
        """Load the environment variables of the application from a .env file if existing or from a couple .env.keys/.env.vault file."""
        if not self.__load_standard_env():
            if self.__load_cyphered_env():
                self.__load_env_key()
                self.__load_decyphered_env()


class AppConfigError(Exception):
    """Raise an error of this type if the expected env variables are missing."""

    pass


def _parse_bool(val: Union[str, bool]) -> bool:  # pylint: disable=E1136
    return val if type(val) is bool else val.lower() in ["true", "yes", "1"]


# AppConfig class with required fields, default values, type checking, and typecasting for int and bool values
class AppConfig:
    """Control that the environment variables are correctly configured for the application."""

    APP_SECRET_KEY: str
    PG4ADMIN_EMAIL: str
    PG4ADMIN_PORT: int
    REDIS_PORT: int
    DATABASE_NAME: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    def __init__(self, env):
        """
        Map environment variables to class fields according to these rules.

        - Field won't be parsed unless it has a type annotation
        - Field will be skipped if not in all caps
        - Class field and environment variable name are the same
        """
        for field in self.__annotations__:
            if not field.isupper():
                continue

            # Raise AppConfigError if required field not supplied
            default_value = getattr(self, field, None)
            if default_value is None and env.get(field) is None:
                raise AppConfigError("The {} field is required".format(field))

            # Cast env var value to expected type and raise AppConfigError on failure
            try:
                var_type = get_type_hints(AppConfig)[field]
                if var_type == bool:
                    value = _parse_bool(env.get(field, default_value))
                else:
                    value = var_type(env.get(field, default_value))

                self.__setattr__(field, value)
            except ValueError:
                raise AppConfigError(
                    'Unable to cast value of "{}" to type "{}" for "{}" field'
                    .format(env[field], var_type, field)
                )

    def __repr__(self):
        """Give the list of environment variables key with their values.

        Returns:
            dict: The key-value pair of environment variables for the application.
        """
        return str(self.__dict__)

    def get_application_env(self) -> dict:
        """Give the list of environment variables key with their values.

        Returns:
            dict: The key-value pair of environment variables for the application.
        """
        return self.__dict__
