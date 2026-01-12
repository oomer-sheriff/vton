from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "VTON API"
    API_V1_STR: str = "/api/v1"
    
    # Postgres
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "vton"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Redis / Celery
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    
    # RabbitMQ
    RABBITMQ_HOST: str = "127.0.0.1"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"

    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # Keys based on environment
    GEMINI_API_KEY: Optional[str] = None
    
    # Resource Management
    UNLOAD_PIPELINE_AFTER_TASK: bool = True
    
    # VTON Pipeline Tuning (for color accuracy)
    VTON_IP_ADAPTER_SCALE: float = 1.0          # Lower = less garment style influence (default was 1.0)
    VTON_CONTROLNET_SCALE: float = 1.0        # Lower = less pose rigidity (default was 1.0)
    VTON_INFERENCE_STRENGTH: float = 0.99       # Lower = preserve more of original (default was 0.99)
    VTON_GUIDANCE_SCALE: float = 7.5             # CFG scale for prompt adherence
    VTON_VAE_FULL_PRECISION: bool = False       # Decode VAE in float32 for better colors

    class Config:
        env_file = ".env"

    @model_validator(mode='after')
    def compute_settings(self):
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        if not self.CELERY_BROKER_URL:
             self.CELERY_BROKER_URL = f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return self

settings = Settings()
