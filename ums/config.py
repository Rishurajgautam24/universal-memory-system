
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
        case_sensitive=False, extra="ignore",
    )
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    log_level: str = "INFO"
    database_url: str = "sqlite+aiosqlite://data/ums.db"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    extraction_model: str = "openai/gpt-4o-mini"
    synthesis_model: str = "openai/gpt-4o"
    embedding_model: str = "openai/text-embedding-3-small"
    min_observation_confidence: float = 0.4
    max_observations_per_conversation: int = 50
    candidate_promotion_threshold: float = 0.75
    min_evidence_for_promotion: int = 2
    candidate_expiry_days: int = 30
    semantic_dedup_threshold: float = 0.85
    recall_max_tokens: int = 2000
    recall_min_confidence: float = 0.5
    distillation_batch_size: int = 10
    distillation_interval_hours: int = 4
    admin_api_key: str | None = None
    rate_limit_observe_per_hour: int = 100
    rate_limit_recall_per_hour: int = 500
    rate_limit_search_per_hour: int = 200
    rate_limit_timeline_per_hour: int = 200
    rate_limit_explain_per_hour: int = 100
    rate_limit_reflect_per_hour: int = 10


settings = Settings()
