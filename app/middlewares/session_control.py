from aiogram.dispatcher.middlewares.base import BaseMiddleware
import database.db_utils as db_utils
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject

class SessionControlMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        await handler(event, data)
        if db_utils.current_session:
            try:
                db_utils.current_session.commit()
            except Exception as e:
                db_utils.current_session.rollback()
                raise e
            finally:
                db_utils.current_session.close()
                db_utils.current_session = None
