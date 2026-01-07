from typing import Dict, Any, Optional
from taskiq import TaskiqResult
from uuid import UUID
from LuminMessageService.app.domain.models.common.value_objects import MessageText
from LuminMessageService.app.application.taskiq.message_commands import (
    get_message_by_id_task,
    create_message_task,
    delete_message_task,
    edit_message_text_task,
    mark_as_read_task
)
from LuminMessageService.app.infrastructure.tasks.taskiq_broker import get_taskiq_broker


class TaskiqService:
    def __init__(self) -> None:
        self.broker = get_taskiq_broker()

    async def send_get_message_by_id_task(self, message_id: UUID) -> Optional[Dict]:
        try:
            print(f"[TaskiqService] Sending send_get_message_by_id_task for {message_id}")

            task = get_message_by_id_task.kiq(str(message_id))
            result: TaskiqResult = await task

            print(f"[TaskiqService] Task sent, task_id: {result.task_id}")

            try:
                task_result = await result.wait_result(timeout=10)
                print("[TaskiqService] Task result received")

                if task_result.is_success:
                    return task_result.return_value
                else:
                    print(f"[TaskiqService] Task failed: {task_result.error}")
                    return None

            except TimeoutError:
                print(f"[TaskiqService] Task timeout for task_id: {result.task_id}")
                return None

        except Exception as e:
            print(f"[TaskiqService] Error in send_get_user_by_id_task: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def send_create_user_task(self, message_data: Dict[str, Any]) -> str:
        task = await create_message_task.kiq(message_data)
        return task.task_id

    async def send_mark_as_read_task(self, message_id: UUID) -> str:
        task = await mark_as_read_task.kiq(str(message_id))
        return task.task_id

    async def send_edit_message_text_task(self, message_id: UUID, new_text: MessageText) -> str:
        task = await edit_message_text_task.kiq(str(message_id), new_text)
        return task.task_id

    async def send_delete_message_task(self, message_id: UUID) -> str:
        task = await delete_message_task.kiq(str(message_id))
        return task.task_id
