"""
ADK IDE Configuration Settings

Manages configuration for different deployment environments with proper validation
and security considerations.
"""

import os
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field, validator
from functools import lru_cache


class Environment(str, Enum):
    """Deployment environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ADKIDESettings(BaseSettings):
    """
    Comprehensive settings for ADK IDE system with environment-specific configurations.
    """
    
    # Environment Configuration
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ADK_IDE_ENV")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Google Cloud Configuration
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    google_cloud_project: str = Field(..., env="GOOGLE_CLOUD_PROJECT")
    google_cloud_region: str = Field(default="us-central1", env="GOOGLE_CLOUD_REGION")
    
    # ADK Configuration
    adk_model: str = Field(default="gemini-2.5-flash", env="ADK_MODEL")
    adk_safety_model: str = Field(default="gemini-2.5-flash", env="ADK_SAFETY_MODEL")
    adk_max_iterations: int = Field(default=5, env="ADK_MAX_ITERATIONS")
    adk_max_llm_calls: int = Field(default=500, env="ADK_MAX_LLM_CALLS")
    
    # Session Management
    session_service_type: str = Field(default="memory", env="SESSION_SERVICE_TYPE")
    session_encryption_key: Optional[str] = Field(default=None, env="SESSION_ENCRYPTION_KEY")
    session_timeout_hours: int = Field(default=24, env="SESSION_TIMEOUT_HOURS")
    
    # Database Configuration
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # Security Configuration
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # VPC Security Configuration
    vpc_sc_perimeter_name: Optional[str] = Field(default=None, env="VPC_SC_PERIMETER_NAME")
    allowed_ip_ranges: str = Field(default="0.0.0.0/0", env="ALLOWED_IP_RANGES")
    
    # Observability Configuration
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    arize_api_key: Optional[str] = Field(default=None, env="ARIZE_API_KEY")
    arize_space_key: Optional[str] = Field(default=None, env="ARIZE_SPACE_KEY")
    phoenix_endpoint: Optional[str] = Field(default=None, env="PHOENIX_ENDPOINT")
    phoenix_api_key: Optional[str] = Field(default=None, env="PHOENIX_API_KEY")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8080, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # Resource Limits
    max_memory_mb: int = Field(default=4096, env="MAX_MEMORY_MB")
    max_cpu_cores: int = Field(default=2, env="MAX_CPU_CORES")
    max_execution_time_seconds: int = Field(default=300, env="MAX_EXECUTION_TIME_SECONDS")
    
    @validator("session_service_type")
    def validate_session_service_type(cls, v, values):
        """Validate session service type based on environment."""
        environment = values.get("environment")
        
        if environment == Environment.PRODUCTION and v == "memory":
            raise ValueError("Production environment cannot use in-memory session service")
        
        valid_types = ["memory", "database", "vertex_ai"]
        if v not in valid_types:
            raise ValueError(f"Session service type must be one of: {valid_types}")
        
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v, values):
        """Validate database URL is provided when needed."""
        session_service_type = values.get("session_service_type")
        environment = values.get("environment")
        
        if session_service_type == "database" and not v:
            raise ValueError("Database URL is required when using database session service")
        
        if environment == Environment.PRODUCTION and not v:
            raise ValueError("Database URL is required in production environment")
        
        return v
    
    @validator("session_encryption_key")
    def validate_encryption_key(cls, v, values):
        """Validate encryption key is provided for production."""
        environment = values.get("environment")
        
        if environment == Environment.PRODUCTION and not v:
            raise ValueError("Session encryption key is required in production")
        
        if v and len(v) < 32:
            raise ValueError("Encryption key must be at least 32 characters long")
        
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def resource_limits(self) -> Dict[str, Any]:
        """Get resource limits configuration."""
        return {
            "memory": f"{self.max_memory_mb}MB",
            "cpu": str(self.max_cpu_cores),
            "execution_time": self.max_execution_time_seconds
        }
    
    @property
    def allowed_ip_list(self) -> list[str]:
        """Get list of allowed IP ranges."""
        return [ip.strip() for ip in self.allowed_ip_ranges.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> ADKIDESettings:
    """
    Get cached settings instance.
    
    Returns:
        ADKIDESettings: Configured settings instance
    """
    return ADKIDESettings()


def get_environment() -> Environment:
    """
    Get current environment.
    
    Returns:
        Environment: Current deployment environment
    """
    return get_settings().environment