from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    xai_api_key: str = ""


def get_env_or_die() -> EnvSettings:
    settings = EnvSettings()
    return settings


ENV_SETTINGS = get_env_or_die()
