#!/usr/bin/env python3
'''Request caching and tracking.
'''
import redis
import requests
from functools import wraps
from typing import Callable

redis_store = redis.Redis()

def data_cacher(method: Callable) -> Callable:
    @wraps(method)
    def invoker(url) -> str:
        # Incrementing count should happen before checking cache
        redis_store.incr(f'count:{url}')
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        # Setting count to 0 here seems unnecessary and might reset the count incorrectly
        # Removed the line below
        # redis_store.set(f'count:{url}', 0)
        # Corrected setex to set the result with an expiration time
        redis_store.setex(f'result:{url}', 10, result)
        return result
    return invoker

@data_cacher
def get_page(url: str) -> str:
    return requests.get(url).text
