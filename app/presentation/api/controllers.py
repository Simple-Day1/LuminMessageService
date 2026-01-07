from typing import Annotated, Dict, Any
from uuid import UUID
from litestar import Controller, get, post, patch
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.params import Parameter
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from LuminMessageService.app.domain.models.common.value_objects import MessageText
from LuminMessageService.app.infrastructure.persistance.database import get_dependency_container
from LuminMessageService.app.infrastructure.persistance.message_mapper import MessageMapper
from LuminMessageService.app.infrastructure.persistance.pydantic_models import CreateMessageRequest
from LuminMessageService.app.infrastructure.tasks.taskiq_service import TaskiqService


def get_taskiq_service() -> TaskiqService:
    return TaskiqService()


class MessageController(Controller):
    path = "/api/messages"
    dependencies = {"taskiq_service": Provide(get_taskiq_service)}

    @get(
        "/{message_id:uuid}",
        summary="Get message by ID",
        description="Получить информацию о сообщении по его идентификатору",
    )
    async def get_message_by_id(
        self,
        message_id: Annotated[UUID, Parameter(description="Message ID (UUID)")],
        taskiq_service: TaskiqService
    ) -> Dict[str, Any]:
        try:
            print(f"[taskiq_handlers] Getting message by id: {message_id}")

            result = await taskiq_service.send_get_message_by_id_task(message_id)

            if result is None:
                print("[taskiq_handlers] Taskiq returned None, trying direct approach...")

                container = get_dependency_container()
                message_service = await container.get_message_service()
                message = await message_service.get_message_by_id(message_id)

                if not message:
                    raise HTTPException(
                        detail="Message not found",
                        status_code=HTTP_404_NOT_FOUND
                    )

                return MessageMapper().to_persistence(message)

            print(f"[taskiq_handlers] Taskiq result: {result}")

            if isinstance(result, dict):
                return result
            else:
                return result

        except ValueError as e:
            raise HTTPException(
                detail=str(e),
                status_code=HTTP_404_NOT_FOUND
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"[taskiq_handlers] Error: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                detail=str(e),
                status_code=HTTP_500_INTERNAL_SERVER_ERROR
            )

    @post(
        "/",
        summary="Create new message",
        description="Создать новое сообщение",
    )
    async def create_message(
        self,
        data: CreateMessageRequest,
        taskiq_service: TaskiqService
    ) -> Dict[str, Any]:
        try:
            message_dict = data.dict()

            task_id = await taskiq_service.send_create_user_task(message_dict)
            return {
                "task_id": task_id,
                "status": "queued",
                "message_id": data.message_id
            }
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=HTTP_500_INTERNAL_SERVER_ERROR
            )

    @patch(
        "/{message_id:uuid}/edit_text",
        summary="Edit text",
        description="Изменить текст сообщения",
    )
    async def edit_text(
        self,
        message_id: Annotated[UUID, Parameter(description="User ID (UUID)")],
        new_text: str,
        taskiq_service: TaskiqService
    ) -> Dict[str, Any]:
        try:
            task_id = await taskiq_service.send_edit_message_text_task(message_id, MessageText(new_text))
            return {"task_id": task_id, "status": "queued"}
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=HTTP_500_INTERNAL_SERVER_ERROR
            )

    @patch(
        "/{message_id:uuid}/mark_as_read",
        summary="Mark as read",
        description="Пометить сообщение как прочитанное",
    )
    async def mark_as_read(
        self,
        message_id: Annotated[UUID, Parameter(description="User ID (UUID)")],
        taskiq_service: TaskiqService
    ) -> Dict[str, Any]:
        try:
            task_id = await taskiq_service.send_mark_as_read_task(message_id)
            return {"task_id": task_id, "status": "queued"}
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=HTTP_500_INTERNAL_SERVER_ERROR
            )

    @patch(
        "/{message_id:uuid}/delete",
        summary="Delete message",
        description="Удалить сообщение",
    )
    async def delete_message(
            self,
            message_id: Annotated[UUID, Parameter(description="User ID (UUID)")],
            taskiq_service: TaskiqService
    ) -> Dict[str, Any]:
        try:
            task_id = await taskiq_service.send_delete_message_task(message_id)
            return {
                "task_id": task_id,
                "status": "queued",
                "message_id": message_id
            }
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=HTTP_500_INTERNAL_SERVER_ERROR
            )
