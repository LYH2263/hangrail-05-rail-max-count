from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.api.router import api_router
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.services.seed import seed_if_empty


def _ensure_columns() -> None:
    """create_all 不会给已存在的表补列；对老库幂等加上 max_items。"""
    inspector = inspect(engine)
    if "hang_rails" not in inspector.get_table_names():
        return
    columns = {c["name"] for c in inspector.get_columns("hang_rails")}
    if "max_items" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE hang_rails ADD COLUMN max_items INTEGER"))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _ensure_columns()
    if settings.seed_on_empty:
        db = SessionLocal()
        try:
            seed_if_empty(db)
        finally:
            db.close()
    yield


app = FastAPI(title="HangRail", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api")
