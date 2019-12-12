# -*- coding: utf-8 -*-
__author__ = 'Luke'

from common.manage_data import *
from common.StartAppiumServer import *
# from common.log import LogRecord
import adb_order
import multiprocessing

def Monitor(index):
    appium_queue = "{}_appium".format(Local_ip)
    print("启动监听器%s" % index)
    # PullMQ(appium_queue, callback)
    while True:
        try:
            PullMQ(appium_queue, callback)
        except BaseException as b:
            # LogRecord.info(str(b))
            print(b)


def AdbStart(index):
    adb_queue = "{}_adb".format(Local_ip)
    print("启动ADB%s" % index)
    # PullMQ(appium_queue, callback)
    while True:
        try:
            PullMQ(adb_queue, adb_order.adb_callback)
        except BaseException as b:
            # LogRecord.info(str(b))
            print(b)



if __name__ == '__main__':
    adb_queue = "{}_adb".format(Local_ip)
    # number = sys.argv[1]
    number = 3
    try:
        number = int(number)
    except:
        print("请输入正确的数字类型!")
    StartAppiumAdb(number)
    p = multiprocessing.Process(target=AdbStart, args=(1, ))
    p.start()
    print(redis_cache.sinter(redis_appium_adb))
    # Monitor(1)
    mp_list = []
    for i in range(len(redis_cache.sinter(redis_appium_adb))):
        p = multiprocessing.Process(target=Monitor, args=(i, ))
        p.start()

