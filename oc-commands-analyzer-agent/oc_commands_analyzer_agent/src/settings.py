"""Settings configuration for the OC Commands Analyzer Agent."""

import json
import os
from typing import Literal, Optional

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from oc_commands_analyzer_agent.utils.pylogger import get_python_logger

# Initialize logger
logger = get_python_logger()

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")


class Settings(BaseSettings):
    """Configuration settings for the OC Commands Analyzer Agent."""

    # Server Configuration
    AGENT_HOST: str = Field(default="0.0.0.0")
    AGENT_PORT: int = Field(default=8082, ge=1024, le=65535)
    PYTHON_LOG_LEVEL: str = Field(default="INFO")

    # LLM Provider Configuration
    LLM_PROVIDER: Literal["ollama", "vertex"] = Field(default="ollama")

    # Ollama Configuration
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="llama3.2")

    # Vertex AI Configuration
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(default=None)
    GOOGLE_APPLICATION_CREDENTIALS_CONTENT: Optional[str] = Field(default=None)
    VERTEX_PROJECT_ID: Optional[str] = Field(default=None)
    VERTEX_LOCATION: str = Field(default="us-central1")
    VERTEX_MODEL: str = Field(default="gemini-2.0-flash-exp")

    # MCP Server Configuration
    MCP_SERVER_URL: str = Field(default="http://localhost:5002/mcp/")
    MCP_SERVER_TRANSPORT: str = Field(default="streamable_http")

    # Checkpointing Configuration
    USE_CHECKPOINTING: bool = Field(default=True)
    SQLITE_DB_PATH: str = Field(default="./data/conversations.db")

    @field_validator("PYTHON_LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    def setup_google_credentials(self) -> None:
        """Set up Google credentials for Vertex AI."""
        if self.LLM_PROVIDER != "vertex":
            return

        # If credentials content is provided, write to temp file
        if self.GOOGLE_APPLICATION_CREDENTIALS_CONTENT:
            try:
                creds_dict = json.loads(self.GOOGLE_APPLICATION_CREDENTIALS_CONTENT)
                temp_creds_path = "/tmp/google-credentials.json"
                with open(temp_creds_path, "w") as f:
                    json.dump(creds_dict, f)
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_creds_path
                logger.info("Google credentials set from content")
            except Exception as e:
                logger.error(f"Failed to parse Google credentials content: {e}")
                raise ValueError("Invalid Google credentials content")
        elif self.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                self.GOOGLE_APPLICATION_CREDENTIALS
            )
            logger.info(
                f"Google credentials set from file: {self.GOOGLE_APPLICATION_CREDENTIALS}"
            )
        else:
            logger.warning(
                "No Google credentials configured for Vertex AI. "
                "Set GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_APPLICATION_CREDENTIALS_CONTENT"
            )


def validate_config(settings: Settings) -> None:
    """Validate configuration settings."""
    # Validate port range
    if not (1024 <= settings.AGENT_PORT <= 65535):
        raise ValueError(
            f"AGENT_PORT must be between 1024 and 65535, got {settings.AGENT_PORT}"
        )

    # Validate LLM provider
    if settings.LLM_PROVIDER not in ["ollama", "vertex"]:
        raise ValueError(
            f"LLM_PROVIDER must be 'ollama' or 'vertex', got {settings.LLM_PROVIDER}"
        )

    # Validate Vertex AI configuration
    if settings.LLM_PROVIDER == "vertex":
        if not settings.VERTEX_PROJECT_ID:
            raise ValueError(
                "VERTEX_PROJECT_ID is required when using Vertex AI provider"
            )

    logger.info("Configuration validation passed")


# Create settings instance
settings = Settings()
