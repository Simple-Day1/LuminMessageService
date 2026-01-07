from uuid import UUID
from psycopg2.extras import RealDictCursor
from LuminMessageService.app.domain.models.aggregates.message import Message
from LuminMessageService.app.domain.repositories.reposiotries import MessageRepository
from LuminMessageService.app.infrastructure.cache.multi_level_cache import MultiLevelCache
from LuminMessageService.app.infrastructure.persistance.identity_map import MessageIdentityMap
from LuminMessageService.app.infrastructure.persistance.message_mapper import MessageMapper


class PostgresSQLMessageRepository(MessageRepository):
    def __init__(self, connection_factory, identity_map: MessageIdentityMap, cache: MultiLevelCache) -> None:
        self.connection_factory = connection_factory
        self.identity_map = identity_map
        self.mapper = MessageMapper()
        self.cache = cache

    def _get_connection(self):
        conn = self.connection_factory()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        return conn, cursor

    async def save(self, message: Message) -> None:
        conn, cursor = self._get_connection()

        try:
            check_sql = "SELECT message_id FROM messages WHERE user_id = %s"
            cursor.execute(check_sql, (str(message.id),))
            existing_user = cursor.fetchone()

            if existing_user:
                update_sql = """
                UPDATE users SET
                    sender_id = %s,
                    recipient_id = %s,
                    chat_id = %s,
                    text = %s,
                    sent_at = %s,
                    read_at = %s,
                    edited_at = %s,
                WHERE message_id = %s
                """

                message_data = (
                    message.sender_id,
                    message.recipient_id,
                    message.chat_id,
                    message.text.value,
                    message.sent_at,
                    message.read_at,
                    message.edited_at,
                    str(message.id)
                )

                cursor.execute(update_sql, message_data)
                print(f"Message updated: {message.id}")

            else:
                insert_sql = """
                INSERT INTO messages (
                    message_id, 
                    sender_id,
                    recipient_id,
                    chat_id,
                    text,
                    sent_at,
                    read_at,
                    edited_at,
                ) VALUES (%s, %s, %s, %s, %s, %s, %s CURRENT_TIMESTAMP)
                """

                user_data = (
                    str(message.id),
                    message.sender_id,
                    message.recipient_id,
                    message.chat_id,
                    message.text.value,
                    message.sent_at,
                    message.read_at,
                    message.edited_at,
                )

                cursor.execute(insert_sql, user_data)
                print(f"Message created: {message.id}")

            conn.commit()

            await self.cache.invalidate_message(message.id)
            message_dict = self.mapper.to_persistence(message)
            await self.cache.set_message(message.id, message_dict)

        except Exception as e:
            conn.rollback()
            await self.cache.invalidate_message(message.id)
            print(f"Error saving message {message.id}: {e}")
            raise

        finally:
            cursor.close()
            conn.close()

        self.identity_map.add(message)
        message.clear_domain_events()

    async def get_by_id(self, message_id: UUID) -> Message | None:
        cached_message = await self.cache.get_message(message_id)

        if cached_message:
            print(f"User {message_id} found in cache")
            return cached_message

        conn, cursor = self._get_connection()

        try:
            select_sql = """
            SELECT 
                    message_id, 
                    sender_id,
                    recipient_id,
                    chat_id,
                    text,
                    sent_at,
                    read_at,
                    edited_at,
            FROM messages 
            WHERE message_id = %s
            """

            cursor.execute(select_sql, (str(message_id),))
            message_data = cursor.fetchone()

            if not message_data:
                return None

            message_dict = dict(message_data)

            print(message_dict)

            message = self.mapper.to_domain(message_dict)
            await self.cache.set_message(message_id, message_dict)
            self.identity_map.add(message)

            return message

        except Exception as e:
            print(f"Error getting user {message_id}: {e}")
            return None

        finally:
            cursor.close()
            conn.close()

    async def delete(self, message_id: UUID) -> None:
        conn, cursor = self._get_connection()

        try:
            delete_sql = "DELETE FROM messages WHERE message_id = %s"
            cursor.execute(delete_sql, (str(message_id),))
            conn.commit()

            await self.cache.invalidate_message(message_id)
            self.identity_map.remove(message_id)

            print(f"Message {message_id} deleted from database and cache")

        except Exception as e:
            conn.rollback()
            print(f"Error deleting message {message_id}: {e}")
            raise

        finally:
            cursor.close()
            conn.close()
