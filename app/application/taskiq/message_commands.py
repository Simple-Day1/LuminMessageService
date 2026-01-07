import logging
from taskiq import TaskiqDepends
from uuid import UUID
from LuminMessageService.app.application.commands.create import CreateMessageCommand
from LuminMessageService.app.application.commands.delete import DeleteMessageCommand
from LuminMessageService.app.application.commands.edit_text import EditMessageTextCommand
from LuminMessageService.app.application.commands.mark_as_read import MarkMessageAsReadCommand
from LuminMessageService.app.application.queries.get_by_id import GetMessageByIDQuery
from LuminMessageService.app.domain.models.common.value_objects import MessageText
from LuminMessageService.app.infrastructure.dependency_container import DependencyContainer
from LuminMessageService.app.infrastructure.persistance.database import get_dependency_container
from LuminMessageService.app.infrastructure.persistance.message_mapper import MessageMapper
from LuminMessageService.app.infrastructure.tasks.taskiq_broker import get_taskiq_broker

logger = logging.getLogger(__name__)


def get_broker_safe():
    try:
        from LuminMessageService.app.infrastructure.tasks.taskiq_broker import get_taskiq_broker
        broker = get_taskiq_broker()
        if broker is None:
            logger.warning("Broker is None, tasks will not be registered")
            return None
        return broker
    except Exception as error:
        logger.error(f"Failed to get broker: {error}")
        return None


broker = None
try:
    broker = get_broker_safe()
    if broker:
        logger.info("Broker initialized in message_commands.py")
    else:
        logger.warning("Broker not available, tasks will not be registered")
except Exception as e:
    logger.error(f"Failed to initialize broker: {e}")
    broker = None

if broker is not None:
    @broker.task
    async def create_message_task(
            message_data: dict,
            container: DependencyContainer = TaskiqDepends(get_dependency_container)
    ) -> dict:
        try:
            print("=" * 50)
            print("STARTING CREATE_USER_TASK")
            print(f"User data received: {message_data}")

            if not container:
                return {"success": False, "error": "DependencyContainer is None"}

            print("Getting create user handler...")
            create_handler = await container.get_create_message_handler()
            print(f"Create user handler obtained: {create_handler}")

            message_service = await container.get_message_service()
            print(f"Message service: {message_service}")
            print(f"Connection factory: {message_service.connection_factory if message_service else 'None'}")

            command = CreateMessageCommand(
                message_id=message_data["message_id"],
                sender_id=message_data["sender_id"],
                recipient_id=message_data["recipient_id"],
                chat_id=message_data["chat_id"],
                text=message_data["text"],
                sent_at=message_data["sent_at"],
                read_at=message_data["read_at"],
                edited_at=message_data["edited_at"],
            )

            print(f"Finishing create_user_task for user_id: {message_data["user_id"]}")
            result = await create_handler.handle(command)

            return result

        except Exception as e:
            print(f"ERROR in create_user_task: {str(e)}")
            import traceback
            print(f"📋 Traceback:\n{traceback.format_exc()}")
            return {

                "success": False,

                "error": str(e),

                "traceback": traceback.format_exc()

            }


    @broker.task
    async def mark_as_read_task(
            message_id: str,
            container: DependencyContainer = TaskiqDepends(get_dependency_container)
    ) -> dict:
        try:
            print('Start mark_as_read_task')
            handler = await container.get_mark_message_as_read_handler()
            print("Handler created")

            command = MarkMessageAsReadCommand(UUID(message_id))

            result = await handler.handle(command)
            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": "change_bio"
            }


    @broker.task
    async def edit_message_text_task(
            message_id: str,
            new_text: MessageText,
            container: DependencyContainer = TaskiqDepends(get_dependency_container)
    ) -> dict:
        try:
            handler = await container.get_edit_message_text_handler()

            command = EditMessageTextCommand(UUID(message_id), new_text)
            result = await handler.handle(command)
            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": "edit_message_text"
            }


    @broker.task
    async def get_message_by_id_task(
            message_id: str,
            container: DependencyContainer = TaskiqDepends(get_dependency_container)
    ) -> dict:
        try:
            print(f"Starting get_message_by_id_task for message_id: {message_id}")
            handler = await container.get_message_by_id_handler()

            query = GetMessageByIDQuery(UUID(message_id))
            result = await handler.handle(query)

            if result.get("success") and "message" in result:
                message = result["message"]

                print("🔍 Converting Message object to dict...")
                message_dict = MessageMapper().to_persistence(message)
                print(f"✅ Message converted to dict: {message_dict.keys()}")

                return {
                    "success": True,
                    "message": message_dict,
                    "message_id": message_id
                }
            else:
                return {
                    "success": False,
                    "error": result.get("exception", "Unknown error"),
                    "message_id": message_id
                }

        except Exception as error:
            print(f"Error in get_message_by_id_task: {error}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(error),
                "message_id": message_id,
                "task": "get_message_by_id"
            }


    @broker.task
    async def delete_message_task(
            message_id: str,
            container: DependencyContainer = TaskiqDepends(get_dependency_container)
    ) -> dict:
        try:
            handler = await container.get_delete_message_handler()

            command = DeleteMessageCommand(UUID(message_id))

            result = await handler.handle(command)
            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": "change_username"
            }
