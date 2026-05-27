from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import connect_db, close_db
from app.api.v1.product_router import router as product_router
from app.api.v1.search_router import router as search_router
from app.api.v1.compare_router import router as compare_router
from app.api.v1.wishlist_router import router as wishlist_router
from app.api.v1.alerts_router import router as alerts_router
from app.api.v1.settings_router import router as settings_router
from app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────
    await connect_db()          # connects MongoDB BEFORE any request arrives
    yield
    # ── Shutdown ─────────────────────────────────────────────────────────
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    description="PriceScout – real-time price comparison API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router)
app.include_router(search_router)
app.include_router(compare_router)
app.include_router(wishlist_router)
app.include_router(alerts_router)
app.include_router(settings_router)


@app.get("/", tags=["Health"])
async def root():
    return {"message": "PriceScout Backend is running ✅"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
