# -*- coding: utf-8 -*-
__author__ = 'Luke'

import os

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# 远程rabbitmq服务的配置信息
USER = 'luke'
PASSWORD = 'luke2019'
RABBITMQ_IP = '127.0.0.1'
RABBITMQ_PORT = 5672

# 本机IP
Local_ip = "127.0.0.1"


"""
服务器地址
"""
SERVER_IP = "http://127.0.0.1:8000/"
update_phone_info_url = SERVER_IP + "api/phoninfo/"
add_screenshot_url = SERVER_IP + "api/uploading/screenshot/"
Operation_url = SERVER_IP + "api/operation/"


"""
Redis配置
"""
REDISHOST = "127.0.0.1"
REDISPORT = "6379"
# 保存时间,秒为单位
save_time = 60 * 60 * 12

"""
安装包,及文件夹配置
"""

ZALO_PATH = os.path.join(BASE_PATH, r"apk_package\Zalo Video Call_v19.01.02.r5.medium_apkpure.com.apk")
ZALO_appPackage = r"com.zing.zalo"
ZALO_appActivity = r"com.zing.zalo.ui.SplashActivity"

OpenVPN = os.path.join(BASE_PATH, "apk_package\OpenVPN for Android_v0.7.8_apkpure.com.apk")
OpenVPN_appPackage = r"de.blinkt.openvpn"
OpenVPN_appActivity = r"de.blinkt.openvpn.activities.MainActivity"

USER_FILE = os.path.join(BASE_PATH, "user_document")
event2_script_path = os.path.join(BASE_PATH, "phone_system", "event1")
ScreenShot_path = os.path.join(BASE_PATH, "phone_screenshot")

"""
appium配置
http://appium.io/docs/en/writing-running-appium/caps/#android-only
"""
redis_appium_adb = "{}_port".format(Local_ip)

# b
appium_caps = {
    "platformName": "Android", 'automationName': 'UiAutomator2', 'autoAcceptAlerts': True,
    "noReset": True, "resetKeyboard": False, "unicodeKeyboard": True,  "newCommandTimeout": 72000,
}

"""
提示内容
"""
# 陌生人拒绝接收陌生人发来的消息
send_msg_gale = "You aren't allowed to message this person because they have disabled messages from strangers"

