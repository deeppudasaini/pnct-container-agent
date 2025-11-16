import asyncio
from typing import Callable, Any, Type
from functools import wraps
from app.shared.utils.logger import get_logger

logger = get_logger(__name__)


def retry_async(
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,)
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Failed after {max_attempts} attempts",
                            function=func.__name__,
                            error=str(e)
                        )
                        raise

                    logger.warning(
                        f"Attempt {attempt} failed, retrying in {current_delay}s",
                        function=func.__name__,
                        error=str(e)
                    )

                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1

        return wrapper

    return decorator
