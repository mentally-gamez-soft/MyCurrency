import unittest

from currency_exchange_tracker.app_conf.config import AppConfig, EnvLoader


class TestDotenvFileParser(unittest.TestCase):
    def test_is_valid_dotenv_configuration(self):
        env_loader = EnvLoader()
        env_loader.get_env_config()

        config = AppConfig(env_loader.env)

        self.assertIsNotNone(
            config,
            "The configuration is not matching between AppConfig and .env"
            " files.",
        )
