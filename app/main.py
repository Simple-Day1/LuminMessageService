from contextlib import asynccontextmanager
import logging
from litestar import Litestar
from litestar.logging import LoggingConfig
from litestar.openapi import OpenAPIConfig
from LuminMessageService.app.infrastructure.cache.redis_cache import CacheConfig
from LuminMessageService.app.presentation.api.controllers import MessageController

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: Litestar):
    logger.info("🔄 Starting application lifespan...")

    try:
        redis_config = CacheConfig(
            host="localhost",
            port=6379,
            password=None,
            db=0,
            default_ttl=3600
        )

        app.state.redis_config = redis_config

        from LuminUserService.app.infrastructure.tasks.taskiq_broker import startup_broker
        await startup_broker()
        logger.info("Taskiq stream and broker started")

        from LuminUserService.app.infrastructure.messaging.nats_event_bus import NatsEventBus
        event_bus = NatsEventBus()
        await event_bus.connect()
        logger.info("EventBus connected")

        app.state.event_bus = event_bus

        yield

    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

    finally:
        logger.info("🔄 Shutting down...")
        try:
            from LuminUserService.app.infrastructure.tasks.taskiq_broker import shutdown_broker
            await shutdown_broker()
            logger.info("Taskiq broker shutdown")

            from LuminUserService.app.infrastructure.persistanse.database import get_dependency_container

            container = get_dependency_container()
            if hasattr(container, "_redis_cache") and container._redis_cache:
                await container._redis_cache.disconnect()

                logger.info("Redis connections closed")
        except Exception as e:
            logger.error(f"Shutdown error: {e}")


logging_config = LoggingConfig(
    root={"level": "INFO", "handlers": ["console"]},
    loggers={"your_app": {"level": "DEBUG", "handlers": ["console"], "propagate": False}},
)

openapi_config = OpenAPIConfig(
    title="Message Service API",
    version="1.0.0",
    description="API для управления сообщениями с асинхронной обработкой через Taskiq",
)

app = Litestar(
    route_handlers=[MessageController],
    lifespan=[lifespan],
    logging_config=logging_config,
    openapi_config=openapi_config,
    debug=True
)
