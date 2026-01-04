from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.celery_app import celery_app
from app.db.session import engine
from app.db.base import Base

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create Tables
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

    # Startup: Check Celery Connection
    try:
        logger.info(f"Checking Celery Broker connection at {settings.CELERY_BROKER_URL}...")
        # Use a short timeout for the check
        with celery_app.connection_or_acquire() as conn:
            conn.ensure_connection(max_retries=3, interval_start=1, interval_step=1)
            logger.info("Successfully connected to Celery Broker (RabbitMQ).")
    except Exception as e:
        logger.error(f"Failed to connect to Celery Broker: {e}")
        logger.warning("Application will continue, but background tasks may fail.")
    
    yield
    # Shutdown logic (if any)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
