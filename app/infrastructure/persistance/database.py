from typing import Callable
import psycopg2
from sqlalchemy import create_engine, Engine
from LuminMessageService.app.config import settings, db_password
from LuminMessageService.app.infrastructure.dependency_container import DependencyContainer


def connection_factory() -> Callable:
    def create_connection():
        return psycopg2.connect(
            host=settings.db_host,
            database=settings.db_name,
            user=settings.db_user,
            password=db_password
        )
    return create_connection


def get_sync_engine() -> Engine:
    return create_engine(
        f"postgresql://{settings.db_user}:{db_password}@{settings.db_host}/{settings.db_name}",
        pool_pre_ping=True,
        echo=False
    )


def get_dependency_container() -> DependencyContainer:
    return DependencyContainer(connection_factory())
