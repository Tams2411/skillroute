"""Configuration via Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    debug: bool = Field(default=True, validation_alias="DEBUG")
    secret_key: str = Field(default="dev-secret-change-in-production", validation_alias="SECRET_KEY")

    # Database
    database_url: str = Field(default="sqlite:///./data/career_coach.db", validation_alias="DATABASE_URL")

    # AI Providers
    openrouter_api_key: Optional[str] = Field(default=None, validation_alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", validation_alias="OPENROUTER_BASE_URL")
    openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    ai_model: str = Field(default="openrouter/auto", validation_alias="AI_MODEL")
    ai_fallback_model: str = Field(default="openrouter/anthropic/claude-3-haiku", validation_alias="AI_FALLBACK_MODEL")

    # PDF Processing
    max_pdf_size_mb: int = Field(default=5, validation_alias="MAX_PDF_SIZE_MB")
    max_pdf_pages: int = Field(default=10, validation_alias="MAX_PDF_PAGES")
    pdf_extraction_timeout_seconds: int = Field(default=30, validation_alias="PDF_EXTRACTION_TIMEOUT_SECONDS")

    # Streamlit
    streamlit_server_port: int = Field(default=8501, validation_alias="STREAMLIT_SERVER_PORT")
    streamlit_server_address: str = Field(default="localhost", validation_alias="STREAMLIT_SERVER_ADDRESS")

    # Scoring Weights (Guide §4.3)
    weight_role_relevance: float = Field(default=1.0, ge=0.0, le=2.0)
    weight_evidence_strength: float = Field(default=1.0, ge=0.0, le=2.0)

    # Evidence Level Weights (Guide §4.3)
    evidence_none: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_mentioned: float = Field(default=0.2, ge=0.0, le=1.0)
    evidence_demonstrated: float = Field(default=0.4, ge=0.0, le=1.0)
    evidence_verified: float = Field(default=0.9, ge=0.0, le=1.0)

    # Skill Matching
    fuzzy_matching_enabled: bool = Field(default=True)
    fuzzy_threshold: float = Field(default=0.85, ge=0.0, le=1.0)

    # Application Limits
    max_jd_length: int = Field(default=10000)
    max_resume_length: int = Field(default=50000)
    max_interview_answer_length: int = Field(default=5000)

    @property
    def evidence_weights(self) -> dict[str, float]:
        """Map EvidenceLevel to numeric weight."""
        from career_coach.domain.schemas import EvidenceLevel
        return {
            EvidenceLevel.NONE: self.evidence_none,
            EvidenceLevel.MENTIONED: self.evidence_mentioned,
            EvidenceLevel.DEMONSTRATED: self.evidence_demonstrated,
            EvidenceLevel.VERIFIED: self.evidence_verified,
        }

    @property
    def has_ai_provider(self) -> bool:
        """Check if any AI provider is configured."""
        return any([
            self.openrouter_api_key,
            self.openai_api_key,
            self.anthropic_api_key,
        ])

    def get_primary_provider(self) -> tuple[str, Optional[str]]:
        """Get primary provider name and API key."""
        if self.openrouter_api_key:
            return "openrouter", self.openrouter_api_key
        if self.openai_api_key:
            return "openai", self.openai_api_key
        if self.anthropic_api_key:
            return "anthropic", self.anthropic_api_key
        return "none", None


# Global settings instance
settings = Settings()