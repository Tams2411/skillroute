"""Configuration via Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # PDF Processing
    max_pdf_size_mb: int = Field(default=5, validation_alias="MAX_PDF_SIZE_MB")
    max_pdf_pages: int = Field(default=10, validation_alias="MAX_PDF_PAGES")

    # Evidence Level Weights (Guide §4.3)
    evidence_none: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_mentioned: float = Field(default=0.2, ge=0.0, le=1.0)
    evidence_self_reported: float = Field(default=0.3, ge=0.0, le=1.0)
    evidence_demonstrated: float = Field(default=0.4, ge=0.0, le=1.0)
    evidence_verified: float = Field(default=0.9, ge=0.0, le=1.0)

    # Application Limits
    max_jd_length: int = Field(default=10000)
    max_resume_length: int = Field(default=50000)

    @property
    def evidence_weights(self) -> dict[str, float]:
        """Map EvidenceLevel to numeric weight."""
        from career_coach.domain.schemas import EvidenceLevel
        return {
            EvidenceLevel.NONE: self.evidence_none,
            EvidenceLevel.MENTIONED: self.evidence_mentioned,
            EvidenceLevel.SELF_REPORTED: self.evidence_self_reported,
            EvidenceLevel.DEMONSTRATED: self.evidence_demonstrated,
            EvidenceLevel.VERIFIED: self.evidence_verified,
        }

# Global settings instance
settings = Settings()