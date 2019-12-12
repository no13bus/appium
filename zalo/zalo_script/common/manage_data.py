# -*- coding: utf-8 -*-
__author__ = 'Luke'

from contextlib import closing
from common.redis_conn import *
from common.file_handling import *
from common.rabbitmq import *
from zalo_appium import LogIn, AcceptFriendRequest, AddNearbyAndRoom
from zalo_appium import AddPhoneNumber, ChatRoom, SendFriendCircle
from zalo_appium import SendGroupFriends
import requests
import time
import json


class BasicFunction:

    def __init__(self, Appium_ip, udid, sysport, task_name, user):
        self.appium = Appium_ip
        self.udid = udid
        self.sysport = sysport
        self.task_name = task_name
        self.user = user

    def install_app(self, udid, app_path):
        """安装APP"""
        oder = 'adb -s {} install "{}"'.format(udid, app_path)
        res = os.popen(oder)
        result = res.read()

    def save_file(self, file_url):
        """ 保存文件 """
        file_name = file_url.split("/")[-1]
        file_path = os.path.join(USER_FILE, file_name)
        if not os.path.isfile(file_path):
            with closing(requests.get(file_url, stream=True)) as r:
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
        return file_path, file_name

    def dispose_news(self, file_url):
        """ 处理消息内容 txt 文件"""
        file_path, file_name = self.save_file(file_url)
        send_content = []
        with open(file_path, "r", encoding="utf8") as f:
            for s in f.readlines():
                send_content.append(s.strip().replace("$", "\n"))
        return send_content

    def command(self, order):
        time.sleep(1)
        os.system(order)

    def start(self):
        """ 开始处理状态"""
        user_order = "{}_order".format(self.user)
        value_json = redis_cache.hmget(user_order, self.task_name)
        value_dict = json.loads(value_json[0])
        if not value_dict["start_time"]:
            value_dict["start_time"] = time.time()
            value_dict["execute_status"] = 1
        redis_cache.hmset(user_order, {self.task_name: json.dumps(value_dict)})


class Operation(BasicFunction):

    def __init__(self, Appium_ip, task_name, sysport, user, redis_key, user_id,
                 instruct, accomplish, queue_name, data, content):
        BasicFunction.__init__(self, Appium_ip, data["udid"], sysport, task_name, user)
        self.device = data
        self.redis_key = redis_key
        self.content = content
        self.user_id = user_id
        self.instruct = instruct
        self.accomplish = accomplish
        self.queue_name = queue_name

    def check_update_vpn_and_zalo(self, zalo_status, VPN_status, driver):
        """ 查看是否更换zalo账号、vpn"""
        msg = ""
        if zalo_status == 2:
            zalo_res = driver.logout()
            if not zalo_res:
                UpdatePhoneInfo({"udid": self.udid, "Param": json.dumps({"zalo_status": 1})})
                msg += "退出zalo账号成功/"
        if VPN_status == 2:
            vpn_res = driver.UpdateVpn()
            if not vpn_res:
                UpdatePhoneInfo({"udid": self.udid, "Param": json.dumps({"VPN_status": 1})})
                msg += "更改vpn成功/"
        return msg

    def install_allapp(self):
        """ 安装app 及启动vpn"""
        app_install = self.device.get("app_install")
        if not app_install:
            self.install_app(self.udid, ZALO_PATH)
            self.install_app(self.udid, OpenVPN)
            UpdatePhoneInfo({"udid": self.udid, "Param": json.dumps({"app_install": 1})})
            order = r"adb -s {} push {}  /sdcard/event2".format(self.udid, event2_script_path)
            self.command(order)

    def screenshot(self):
        """ 下载手机截图 """
        time.sleep(1)
        order = "adb -s {} shell screencap -p /sdcard/Download/{}.png".format(self.udid, self.udid)
        os.system(order)
        time.sleep(5)
        order = "adb -s {} pull  /sdcard/Download/{}.png  {}".format(self.udid, self.udid, ScreenShot_path)
        os.system(order)
        device_screenshot = os.path.join(ScreenShot_path, "%s.png" % self.udid)
        time.sleep(1)
        order = "adb -s {} shell rm /sdcard/Download/{}.png".format(self.udid, self.udid)
        os.system(order)
        order = "adb -s {} shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///sdcard/Download/{}.png".format(
            self.udid, self.udid)
        os.system(order)
        return device_screenshot

    # ok
    def start_zalo(self):
        """ 登陆 """
        phone = self.device.get("zalo_id")
        password = self.device.get("zalo_pwd")
        user_id = self.device.get("user_id")
        open_vpn_name = self.device.get("open_vpn_name")
        open_vpn_url = self.device.get("open_vpn_url")
        VPN_status = self.device.get("VPN_status")
        zalo_status = self.device.get("zalo_status")
        self.install_allapp()
        appium_obj = LogIn.Operation(self.appium, self.udid, self.sysport, open_vpn_name, phone,
                                     password, user_id, VPN_status)
        if VPN_status == 0 or VPN_status == 2:
            file_path, file_name = self.save_file(open_vpn_url)
            phone_path = "/sdcard/Download/{}".format(file_name)
            appium_obj.Upload_pictures(phone_path, file_path)
        msg = self.check_update_vpn_and_zalo(zalo_status, VPN_status, appium_obj)
        if zalo_status == 0 or zalo_status == 2:
            self.result = appium_obj.Zalo_Login()
            self.result["msg"] += msg
        else:
            self.result = {
                "code": 200, "valid_send_msg": 0, "valid_add_friend": 0,
                "valid_send_gale": 0, "valid_accept_request": 0,
                "data": "", "msg": msg,
            }
        self.end()


    # ok
    def send_circle_of_friends(self):
        """ 发朋友圈"""
        text_content_url = self.content.get("text_content_url")
        photo_url_list = self.content.get("photo_url_list")  # 图片url列表
        longitude = self.content.get("longitude")
        latitude = self.content.get("latitude")
        # 处理消息内容
        content_list = self.dispose_news(text_content_url)
        appium_obj = SendFriendCircle.Operation(self.appium, self.udid, self.sysport, content_list, len(photo_url_list),
                                                longitude, latitude)
        for photo_url in photo_url_list:
            file_path, file_name = self.save_file(photo_url)
            phone_path = "/sdcard/DCIM/Camera/{}".format(file_name)
            appium_obj.Upload_pictures(phone_path, file_path)
        self.result = appium_obj.send_friend_circle()
        time.sleep(5)
        ClearPhoto(self.udid, photo_url_list)
        self.end()


    def Add_people_nearby(self):
        """
        添加附近人，一次最多添加30个
        从第几个开始，
        """
        longitude = self.content.get("longitude")
        latitude = self.content.get("latitude")
        device_number = self.content.get("device_number")
        sex = self.content.get("sex")
        send_count = self.content.get("send_count")
        add_count = self.content.get("add_count")
        photo_url_list = self.content.get("photo_url_list")
        call_url = self.content.get("call_url")
        add_sleep = self.content.get("add_sleep", 0)
        call_content_list = self.dispose_news(call_url)
        start_friend_index = device_number * (send_count + add_count)
        appium_obj = AddNearbyAndRoom.Operation(
            self.appium, self.udid, self.sysport, start_friend_index, send_count,
            add_count, call_content_list, photo_url_list,
            latitude, longitude, sex, add_sleep=add_sleep
        )
        for photo_url in photo_url_list:
            file_path, file_name = self.save_file(photo_url)
            phone_path = "/sdcard/DCIM/Camera/{}".format(file_name)
            appium_obj.Upload_pictures(phone_path, file_path)
        self.result = appium_obj.Add_people_nearby()
        ClearPhoto(self.udid, photo_url_list)
        self.end()


    def Group_send_message(self):
        """ 群发已加好友 """
        text_content_url = self.content.get("text_content_url")
        photo_url_list = self.content.get("photo_url_list")
        time_out = self.content.get("time_out")
        content_list = self.dispose_news(text_content_url)
        appium_obj = SendGroupFriends.Operation(self.appium, self.udid, self.sysport,
                                                content_list, photo_url_list, time_out)
        for photo_url in photo_url_list:
            file_path, file_name = self.save_file(photo_url)
            phone_path = "/sdcard/DCIM/Camera/{}".format(file_name)
            appium_obj.Upload_pictures(phone_path, file_path)
        self.result = appium_obj.send_msg_all_friend()
        ClearPhoto(self.udid, photo_url_list)
        self.end()


    def Add_Chat_Rooms_Friend(self):
        """ 添加聊天室中的人
        选择聊天室然后添加好友或者发送消息。
        room_index: 哪个聊天室分类。
        room_name: 哪个聊天室。
        range_page: 从第几页开始，每页平均七个人。
        add_friend_num：添加多少个好友
        call_list： 招呼列表
        """
        room_index = self.content.get("room_index")
        room_name = self.content.get("room_name")
        device_number = self.content.get("device_number")
        send_count = self.content.get("room_send_count")
        add_count = self.content.get("room_add_count")
        photo_url_list = self.content.get("photo_url_list")
        call_url = self.content.get("call_file_url")
        room_sleep = self.content.get("room_sleep", 0)
        call_content_list = self.dispose_news(call_url)
        start_friend_index = device_number * (send_count + add_count)
        appium_obj = AddNearbyAndRoom.Operation(
            self.appium, self.udid, self.sysport, start_friend_index, send_count,
            add_count, call_content_list, photo_url_list, add_sleep=room_sleep
        )
        for photo_url in photo_url_list:
            file_path, file_name = self.save_file(photo_url)
            phone_path = "/sdcard/DCIM/Camera/{}".format(file_name)
            appium_obj.Upload_pictures(phone_path, file_path)
        self.result = appium_obj.Add_Chat_Rooms(room_index, room_name)
        ClearPhoto(self.udid, photo_url_list)
        self.end()


    def Get_Chat_Rooms_name(self):
        """
        更新聊天室名称
        """
        appium_obj = AddNearbyAndRoom.Operation(self.appium, self.udid, self.sysport, 0, 0, 0, 0, 0)
        Chat_Room_dict = appium_obj.Get_Chat_Rooms()
        redis_key = "chat_rooms_name"
        redis_cache.set(redis_key, json.dumps(Chat_Room_dict), ex=60 * 60 * 24)
        redis_cache.set("update_room", 0)
        redis_cache.expire(redis_key, save_time)
        UpdatePhoneInfo({"udid": self.udid, "Param": json.dumps({"is_operation": 0})})
        self.end()


    def Add_Phone_number_friend(self):
        """ 导入手机号码添加好友 """
        phone_number_file_url = self.content.get("add_phone_number_url")
        phonenumberoperate = self.content.get("phonenumberoperate")
        phonenumber_count = self.content.get("phonenumber_count")
        device_number = self.content.get("device_number")
        call_url = self.content.get("call_url")
        call_content_list = self.dispose_news(call_url)
        file_path, file_name = self.save_file(phone_number_file_url)
        print(file_path, file_name)
        photo_url_list = self.content.get("photo_url_list")
        appium_obj = AddPhoneNumber.Operation(self.appium, self.udid, self.sysport, file_path, call_content_list, photo_url_list, phonenumberoperate, phonenumber_count, device_number)
        if photo_url_list:
            for photo_url in photo_url_list:
                file_path, file_name = self.save_file(photo_url)
                phone_path = "/sdcard/DCIM/Camera/{}".format(file_name)
                appium_obj.Upload_pictures(phone_path, file_path)
        self.result = appium_obj.Add_friend_number()
        self.end()


    def Send_Group_Chat(self):
        """ 按分类进入群聊发送"""
        group_room_text_content_file_url = self.content.get("group_room_text_content_file_url")
        group_room_sleep = self.content.get("group_room_sleep")
        group_room_index = self.content.get("group_room_index")
        call_content_list = self.dispose_news(group_room_text_content_file_url)
        appium_obj = ChatRoom.Operation(self.appium, self.udid, self.sysport,
                                        call_content_list, group_room_index, group_room_sleep)
        self.result = appium_obj.statr_send_room()
        self.end()


    def Friend_Request(self):
        """ 通过好友请求"""
        appium_obj = AcceptFriendRequest.Operation(self.appium, self.udid, self.sysport)
        self.result = appium_obj.start_accept_friend_request()
        self.end()

    def operating_record(self):
        """ 操作记录多进度条 """
        user_redis = "{}_order".format(self.user)
        user_plan = json.loads(redis_cache.hmget(user_redis, self.task_name)[0].decode("utf8"))
        user_plan["succeed_device"][self.udid] = self.result["code"]
        redis_cache.hmset(user_redis, {self.task_name: json.dumps(user_plan)})

    def end(self):
        print("*******{}操作结束".format(self.udid))
        if self.instruct == "Get_Chat_Rooms_name":
            return
        self.zalo_id = self.device.get("id_id")
        self.device_id = self.device.get("id")
        UpdatePhoneInfo({"udid": self.udid, "Param": json.dumps({"is_operation": 0})})
        # 添加操作记录, 以及上传图片保存记录。
        operation_data = {
            "send_msg": self.result["valid_send_msg"], "add_friend": self.result["valid_add_friend"],
            "send_stranger": self.result["valid_send_gale"], "accept_request": self.result["valid_accept_request"],
            "operation": self.instruct, "userinfo": self.user_id, "zaloinfo": self.zalo_id,
            "executetime": time.time(), "description": self.result["msg"]
        }
        Operation_id = OperationApi({"udid": self.udid, "Param": json.dumps(operation_data)})
        photo_path = self.screenshot()
        uploading(photo_path, add_screenshot_url, {"phone_id": self.device_id, "phone_operation_log_id": Operation_id})
        print("更改设备状态，添加记录成功", self.udid)
        # 多进度条
        self.operating_record()
        # 历史记录要改 ---------------------
        self.result["instruct"] = self.instruct
        redis_cache.sadd(self.accomplish, self.udid)
        if self.queue_name:
            PushMQ(self.queue_name, self.result)
        else:
            if self.user:
                redis_cache.hset(self.user, self.redis_key, json.dumps(self.result))
            else:
                redis_cache.set(self.redis_key, json.dumps(self.result))


def callback(ch, method, properties, body):
    body_dict = json.loads(body)
    instruct = body_dict.get("instruct")
    task_name = body_dict.get("task_name")
    queue_name = body_dict.get("queue_name")
    redis_key = body_dict.get("redis_key")
    content = body_dict.get("content")
    data = body_dict.get("data")
    user = body_dict.get("user")
    user_id = body_dict.get("user_id")
    accomplish = "{}_accomplish".format(user_id)
    port_dict = redis_cache.spop(redis_appium_adb)
    if not port_dict:
        return
    appium_and_adb = json.loads(port_dict)
    sysport = appium_and_adb["adb"]
    appium_port = appium_and_adb["appium"]
    print("启动", sysport, appium_port)
    print(body_dict)
    open_obj = Operation("http://127.0.0.1:{}/wd/hub".format(appium_port), task_name, sysport, user, redis_key, user_id,
                         instruct, accomplish, queue_name, data, content)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    if instruct != "Get_Chat_Rooms_name":
        open_obj.start()
    eval("open_obj.{}()".format(instruct))
    redis_cache.sadd(redis_appium_adb, json.dumps(appium_and_adb))
