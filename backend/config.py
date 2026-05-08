import os
from dotenv import load_dotenv

load_dotenv()

USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"

if USE_SQLITE:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./ai_agent.db"
    )
    DATABASE_URL_SYNC = os.getenv(
        "DATABASE_URL_SYNC",
        "sqlite:///./ai_agent.db"
    )
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://aiagent:aiagent123@localhost:5432/ai_agent_platform"
    )
    DATABASE_URL_SYNC = os.getenv(
        "DATABASE_URL_SYNC",
        "postgresql+psycopg2://aiagent:aiagent123@localhost:5432/ai_agent_platform"
    )

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7

CRAWL_INTERVAL_HOURS = int(os.getenv("CRAWL_INTERVAL_HOURS", "6"))
CRAWL_RETRY_DELAY_MINUTES = 30
CRAWL_MAX_RETRIES = 3
CRAWL_REQUEST_DELAY_SECONDS = 3
