from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


DEFAULT_DATA_BACKEND = "local"

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None
_engine_url: str | None = None


def get_data_backend() -> str:
    return os.getenv("APP_DATA_BACKEND", DEFAULT_DATA_BACKEND).strip().lower()


def get_database_url() -> str | None:
    return os.getenv("DATABASE_URL")


def get_engine(database_url: str | None = None) -> Engine:
    global _engine, _engine_url

    resolved_url = database_url or get_database_url()
    if not resolved_url:
        raise RuntimeError("DATABASE_URL is required when APP_DATA_BACKEND=postgres")

    if _engine is None or _engine_url != resolved_url:
        _engine = create_engine(resolved_url, pool_pre_ping=True, future=True)
        _engine_url = resolved_url
    return _engine


def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    global _session_factory

    engine = get_engine(database_url)
    if _session_factory is None or _session_factory.kw.get("bind") is not engine:
        _session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return _session_factory


def get_database_session() -> Generator[Session, None, None]:
    session_factory = get_session_factory()
    with session_factory() as session:
        yield session


def reset_engine_state() -> None:
    global _engine, _session_factory, _engine_url

    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
    _engine_url = None
