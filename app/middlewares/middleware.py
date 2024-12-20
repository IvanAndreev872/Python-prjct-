from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.types import TelegramObject
from aiogram.utils.exceptions import Forbidden

from database import db_utils


class Middleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        if isinstance(event, Message):
            if event.text.lower().strip() in ['консоль админа', 'статистика', 'добавить мастера', 'удалить мастера',
                                              'удалить админа']:
                user_id = event.from_user.id
                if not db_utils.is_admin(user_id):
                    await event.reply("У вас нет прав для доступа к этому ресурсу.")
                    raise Forbidden("Access Denied")
        print('ты крут')
