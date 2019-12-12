# -*- coding: utf-8 -*-
__author__ = 'Luke'

from settings import *
import redis

redis_pool = redis.ConnectionPool(host=REDISHOST, port=REDISPORT)
redis_cache = redis.Redis(connection_pool=redis_pool)
