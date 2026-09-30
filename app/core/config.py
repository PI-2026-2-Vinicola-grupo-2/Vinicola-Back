from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    thingspeak_channel_id: str = "3500405"
    thingspeak_read_api_key: str = ""
    cors_origins: str = "http://localhost:5500"
    db_host: str = ""
    db_port: str = "5432"
    db_name: str = "vinicola"
    db_user: str = ""
    db_password: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()