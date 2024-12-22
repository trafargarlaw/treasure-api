import sys

from redis.asyncio import Redis
from redis.exceptions import AuthenticationError, TimeoutError

from src.common.log import log
from src.core.conf import settings


class RedisCli(Redis):
    def __init__(self):
        super(RedisCli, self).__init__(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DATABASE,
            socket_timeout=settings.REDIS_TIMEOUT,
            decode_responses=True,  # Decode as utf-8
        )

    async def open(self):
        """
        Trigger initialization connection

        :return:
        """
        try:
            await self.ping()
        except TimeoutError:
            log.error("❌ Redis database connection timeout")
            sys.exit()
        except AuthenticationError:
            log.error("❌ Redis database authentication failed")
            sys.exit()
        except Exception as e:
            log.error("❌ Redis database connection error {}", e)
            sys.exit()

    async def delete_prefix(self, prefix: str, exclude: str | list | None = None):
        """
        Delete all keys with specified prefix

        :param prefix:
        :param exclude:
        :return:
        """
        keys = []
        async for key in self.scan_iter(match=f"{prefix}*"):
            if isinstance(exclude, str):
                if key != exclude:
                    keys.append(key)
            elif isinstance(exclude, list):
                if key not in exclude:
                    keys.append(key)
            else:
                keys.append(key)
        if keys:
            await self.delete(*keys)


# Create redis client singleton
redis_client: RedisCli = RedisCli()
