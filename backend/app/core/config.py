from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "VoltStream API"
    cors_origins: str = "*"
    
    # AWS Bedrock Configuration
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "global.amazon.nova-2-lite-v1:0"

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        # Always include localhost:8080 for frontend access
        if "http://localhost:8080" not in origins:
            origins.append("http://localhost:8080")
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()