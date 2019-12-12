# -*- coding: utf-8 -*-
__author__ = 'Luke'

from settings import *
import requests
import os
import time


def uploading(file_path, url, data):
    """ 上传图片 """
    file_name = file_path.split("\\")[-1]
    file = {"picture": (file_name, open(file_path, "rb"), "image/png", {})}
    res = requests.request("POST", url, data=data, files=file)
    return res.json

def UpdatePhoneInfo(data):
    """ 更改设备信息 """
    res = requests.request("PUT", update_phone_info_url, data=data)
    return res.json()

def OperationApi(data):
    """ 添加操作记录 """
    res = requests.request("POST", Operation_url, data=data)
    result = res.json()
    return result["data"]



def ClearPhoto(udid, file_name_list):
    """ 删除手机中的图片 """
    for file_name in map(lambda file: file.split("/")[-1], file_name_list):
        order = "adb -s {} shell rm /sdcard/DCIM/Camera/{}".format(udid, file_name)
        os.system(order)
        order = "adb -s {} shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///sdcard/DCIM/Camera/{}".format(
            udid, file_name)
        os.system(order)
        time.sleep(2)



if __name__ == '__main__':
    import json
    # operation_data = {
    #     "send_msg": 0, "add_friend": 0,
    #     "send_stranger": 0, "accept_request": 0,
    #     "operation": "", "userinfo": 1, "zaloinfo": 1,
    #     "executetime": time.time(), "description": ""
    # }
    # res = OperationApi({"udid": "ads45", "Param": json.dumps(operation_data)})
    # print(res)
    UpdatePhoneInfo({"udid": "92bb2ec", "Param": json.dumps({"is_operation": 0})})