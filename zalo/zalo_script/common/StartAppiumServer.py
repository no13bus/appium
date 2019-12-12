# -*- coding: utf-8 -*-
__author__ = 'Luke'

from common.redis_conn import *
import json


def CheckAppiumServer(port):
    """ 查看appium服务"""
    order = "netstat -aon| findstr {}".format(port)
    res = os.system(order)
    return res


def KillAppiumServer():
    """ 关闭所有appium """
    order = "taskkill /F /IM node.exe /t"
    os.system(order)


def StartAppiumServer(port):
    """ 启动appium服务 """
    order = "start appium -p {} ".format(port)
    os.popen(order)


def StartAppiumAdb(server_number):
    """ 创建appium分配adb端口 """
    base_port = 4723
    adb_port = 8200
    if server_number > 200:
        server_number = 200
    KillAppiumServer()
    redis_cache.delete(redis_appium_adb)
    while server_number:
        if CheckAppiumServer(base_port):
            server_number -= 1
            adb_port += 1
            StartAppiumServer(base_port)
            redis_cache.sadd(redis_appium_adb, json.dumps({"appium": base_port, "adb": adb_port}))
        base_port += 2


if __name__ == '__main__':
    StartAppiumAdb(1)
    print(redis_cache.sinter(redis_appium_adb))
