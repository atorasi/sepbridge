import asyncio

from .logger_file import logger

def script_exceptions(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"An error was occured {str(e)}")
            await asyncio.sleep(15)

    return wrapper