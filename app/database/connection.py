from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

# Module-level variables – populated on startup via lifespan
client: AsyncIOMotorClient | None = None
db = None


async def connect_db():
    """Called once at app startup via lifespan. Connects to MongoDB."""
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    await client.admin.command("ping")
    print(f"✅  MongoDB connected → {settings.MONGO_DB_NAME}")


async def close_db():
    """Called at app shutdown via lifespan."""
    global client
    if client is not None:
        client.close()
        print("🔌  MongoDB connection closed")


def get_db():
    """Returns the active database. Called by every repository."""
    if db is None:
        raise RuntimeError(
            "Database not initialised. "
            "Make sure connect_db() runs inside the lifespan handler."
        )
    return db
