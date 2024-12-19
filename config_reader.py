from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, ValidationError


class Settings(BaseSettings):
    bot_token: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

try:
    config = Settings()
except ValidationError as e:
    print("Ошибка загрузки настроек", e)