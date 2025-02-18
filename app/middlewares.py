from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from cachetools import TTLCache

def throttled(rate: int, on_throttle: Callable | None = None):
    """Декоратор для ограничения частоты запросов.
    
    Args:
        rate (int): Время ожидания в секундах между запросами.
        on_throttle (Callable, optional): Коллбек при превышении лимита. Defaults to None.
    """
    def decorator(func):
        setattr(func, "rate", rate)
        setattr(func, "on_throttle", on_throttle)
        return func
    return decorator

class ThrottlingMiddleware(BaseMiddleware):
    """
    Миддлварь для ограничения частоты запросов (антиспам).
    Используется как инструмент антиспама.
    1. Инициализируется и добавляется к роутеру/диспетчеру.
    2. Используйте @throttled(rate, on_throttle) перед декоратором роутера.
    """
    def __init__(self):
        self.caches = dict()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # Получаем декорированную функцию и её параметры
        decorated_func = data["handler"].callback
        rate = getattr(decorated_func, "rate", None)
        on_throttle = getattr(decorated_func, "on_throttle", None)

        if rate and isinstance(rate, int) and rate > 0:  # Проверяем, что аргумент rate передан корректно
            if id(decorated_func) not in self.caches:  # Если кеш для функции не существует, создаём новый
                self.caches[id(decorated_func)] = TTLCache(maxsize=10_000, ttl=rate)

            if event.from_user.id in self.caches[id(decorated_func)].keys():  # Если пользователь уже отправлял запрос
                if callable(on_throttle):
                    return await on_throttle(event, data)  # Выполняем коллбек, если он задан
                else:
                    return  # Возвращаем пустой ответ, если нет коллбека
            else:
                self.caches[id(decorated_func)][event.from_user.id] = event.from_user.id  # Добавляем пользователя в кеш
                return await handler(event, data)
        else:
            return await handler(event, data)
