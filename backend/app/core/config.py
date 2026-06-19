from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "VoltStream API"
    cors_origins: str = "*"
    
    # AWS Bedrock Configuration
    aws_region: str  # Load from AWS_REGION environment variable
    bedrock_model_id: str  # Load from BEDROCK_MODEL_ID environment variable
    bedrock_for_config: str  # Load from BEDROCK_FOR_CONFIG environment variable
    agentcore_runtime_arn: str

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