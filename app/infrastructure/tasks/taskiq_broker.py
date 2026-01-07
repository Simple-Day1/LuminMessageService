import asyncio
import logging
from taskiq_nats import NatsBroker
import nats
from nats.js.api import StreamConfig, RetentionPolicy, StorageType

logger = logging.getLogger(__name__)

_broker_instance = None
_nats_retry_count = 0
_MAX_RETRIES = 10


async def wait_for_nats():
    global _nats_retry_count

    for attempt in range(_MAX_RETRIES):
        try:
            logger.info(f"Attempting to connect to NATS (attempt {attempt + 1}/{_MAX_RETRIES})")
            nc = await nats.connect(
                "nats://localhost:4222",
                connect_timeout=5,
                max_reconnect_attempts=3,
                reconnect_time_wait=2,
            )

            await nc.close()
            logger.info("✅ NATS is available")
            return True

        except Exception as e:
            logger.warning(f"NATS not available: {e}. Retrying in 2 seconds...")
            await asyncio.sleep(2)

    logger.error(f"❌ Failed to connect to NATS after {_MAX_RETRIES} attempts")
    return False


async def create_taskiq_stream():
    logger.info("Creating Taskiq stream...")

    try:
        # Сначала проверяем доступность NATS
        if not await wait_for_nats():
            raise RuntimeError("NATS server is not available")

        nc = await nats.connect(
            "nats://localhost:4222",
            connect_timeout=10,
            reconnect_time_wait=5,
        )

        js = nc.jetstream()

        stream_config = StreamConfig(
            name="TASKIQ_STREAM",
            subjects=["taskiq.>"],
            retention=RetentionPolicy.WORK_QUEUE,
            max_msgs=100000,
            max_bytes=536870912,
            max_age=24 * 60 * 60,
            storage=StorageType.FILE,
            num_replicas=1,
            duplicate_window=120,
        )

        try:
            stream = await js.add_stream(stream_config)
            logger.info(f"✅ Taskiq stream created: {stream.config.name}")
            logger.info(f"   Subjects: {stream.config.subjects}")

        except Exception as e:
            if "stream name already in use" in str(e):
                logger.info("Taskiq stream already exists")
            else:
                logger.error(f"Failed to create Taskiq stream: {e}")
                # Не падаем, продолжаем без стрима
                logger.warning("Continuing without stream creation")

        await nc.close()

    except Exception as e:
        logger.error(f"Stream creation error: {e}")
        # Не падаем, чтобы приложение могло запуститься
        logger.warning("Continuing without stream, it will be created later if needed")


def get_taskiq_broker() -> NatsBroker:
    global _broker_instance

    if _broker_instance is None:
        logger.info("Initializing Taskiq broker...")

        try:
            # Создаем брокер без немедленного создания стрима
            _broker_instance = NatsBroker(
                servers="nats://localhost:4222",
                queue="message_service",
                connect_timeout=30,
                reconnect_time_wait=5,
                max_reconnect_attempts=-1,
            )

            logger.info("✅ Taskiq broker created")
            logger.info("Queue: user_service")

            # Запускаем создание стрима в фоне
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Запускаем асинхронно без ожидания
                    asyncio.create_task(create_taskiq_stream())
                else:
                    # Запускаем синхронно
                    asyncio.run(create_taskiq_stream())
            except:
                # Если не можем запустить сейчас, стрим создастся позже
                logger.info("Will create stream later")

        except Exception as e:
            logger.error(f"Failed to create Taskiq broker: {e}")
            # Вместо падения возвращаем None
            return None

    return _broker_instance


async def startup_broker():
    """Асинхронный запуск брокера"""
    try:
        await wait_for_nats()
        await create_taskiq_stream()

        broker = get_taskiq_broker()
        if broker:
            await broker.startup()
            logger.info("✅ Broker started successfully")
    except Exception as e:
        logger.error(f"Failed to start broker: {e}")


async def shutdown_broker():
    global _broker_instance

    if _broker_instance is not None:
        try:
            await _broker_instance.shutdown()
            logger.info("Broker shutdown")
        except Exception as e:
            logger.error(f"Error shutting down broker: {e}")
        finally:
            _broker_instance = None
