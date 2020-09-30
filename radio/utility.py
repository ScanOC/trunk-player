import redis
import settings

class RedisQueue(object):
    """Simple Queue with Redis Backend"""
    def __init__(self, name, namespace='tp', **redis_kwargs):
       """Defaults to reading REDIS_URL from environ, or channel REDIS URL from settings_local.py"""
       channel_redis_url = settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]
       self.__db= redis.Redis.from_url(channel_redis_url, **redis_kwargs)
       self.key = '%s:%s' %(namespace, name)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    def put(self, item):
        """Put item into the queue."""
        self.__db.rpush(self.key, item)

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue. 

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            item = self.__db.blpop(self.key, timeout=timeout)
        else:
            item = self.__db.lpop(self.key)

        if item:
            item = item[1]
        return item

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)
