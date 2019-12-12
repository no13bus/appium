# -*- coding: utf-8 -*-
__author__ = 'Luke'

from common.rabbitmq import *
from common.redis_conn import *
import platform
import threading


class Windows:

    def __init__(self):
        pass

    def Look_devices(self, content=None):
        res = os.popen("adb devices")
        result = res.read()
        res_dict = {}
        for line in result.splitlines():
            if line == "List of devices attached":
                continue
            if not line:
                continue
            str_list = line.split("\t")
            res_dict[str_list[0]] = str_list[1]
        return {"code": 200, "data": res_dict}


class Linux:

    def __init__(self):
        pass

    def Look_devices(self, content=None):
        res = os.popen("adb devices")
        result = res.read()
        res_dict = {}
        for line in result.splitlines():
            if line == "List of devices attached":
                continue
            if not line:
                continue
            str_list = line.split("\t")
            res_dict[str_list[0]] = str_list[1]
        return {"code": 200, "data": res_dict}

def adb_callback(ch, method, properties, body):
    sys_name = platform.system()
    if sys_name == "Windows":
        system_obj = Windows()
    elif sys_name == "Linux":
        system_obj = Linux()
    body_dict = json.loads(body)
    instruct = body_dict.get("instruct")
    content = body_dict.get("content")
    queue_name = body_dict.get("queue_name")
    redis_key = body_dict.get("redis_key")
    user = body_dict.get("user")
    try:
        res_msg = eval("system_obj.{}(content)".format(instruct))
    except BaseException as b:
        res_msg = {"code": 500, "msg": str(b)}
    if queue_name:
        PushMQ(queue_name, res_msg)
    else:
        if user:
            redis_cache.hset(user, redis_key, json.dumps(res_msg))
        else:
            redis_cache.set(redis_key, json.dumps(res_msg))
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    adb_queue = "{}_adb".format(Local_ip)
    PushMQ(adb_queue, adb_callback)