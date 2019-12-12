# -*- coding: utf-8 -*-
__author__ = 'Luke'

from zalo_appium.StratAppium import BaseAppium
from selenium.webdriver.common.by import By
# from common.log import LogRecord
import random
import time


class Operation(BaseAppium):
    """
    添加附近人功能 and 聊天室
    """

    def __init__(self, Appium_ip, udid, sysport, start_friend_index,
                 send_count, add_count, call_content_list, photo_list,
                 latitude=None, longitude=None, sex=None, add_sleep=None):
        BaseAppium.__init__(self, Appium_ip, udid, sysport)
        self.start_friend_index = start_friend_index
        self.send_count = send_count
        self.add_sleep = add_sleep
        self.add_count = add_count
        self.sum_count = send_count + add_count
        self.longitude = longitude
        self.latitude = latitude
        self.sex = sex
        self.call_content_list = call_content_list
        self.now_succeed_number = 0
        self.end_element = None
        self.photo_list = photo_list
        self.Chat_Room_dict = {}
        self.friend_name_list = []

    def Condition_settings(self):
        """ Filter nearby conditions """
        try:
            self.driver.find_element_by_id("com.zing.zalo:id/btn_advanced_settings").click()
        except:
            self.driver.find_element_by_id("com.zing.zalo:id/button1").click()
            self.driver.find_element_by_id("com.zing.zalo:id/btn_advanced_settings").click()
        if self.sex == "male":
            self.driver.find_element_by_id("com.zing.zalo:id/rb_search_who_male").click()
        elif self.sex == "female":
            self.driver.find_element_by_id("com.zing.zalo:id/rb_search_who_female").click()
        else:
            self.driver.find_element_by_id("com.zing.zalo:id/rb_search_who_all").click()
        # 年龄选择功能暂时不做.....
        self.driver.find_element_by_id("com.zing.zalo:id/btn_update_nearby_settings").click()

    def Add_people_nearby_init(self):
        self.cut_zalo()
        self.Choice_index(4)
        self.driver.find_element_by_id("com.zing.zalo:id/layout_nearby_container").click()
        self.Condition_settings()

    def Add_people_nearby_request(self, status):
        """
        status:  True   add friend
        status:  False  send message
        """
        if status:
            if not self.Search_label_id("com.zing.zalo:id/btn_function_2"):
                return False
            btn2 = self.driver.find_element_by_id("com.zing.zalo:id/btn_function_2")
            label = btn2.get_attribute("text")
            if label == "UNDO REQUEST":
                return False
            btn2.click()
            call_obj = self.driver.find_element_by_id("com.zing.zalo:id/edtInvitationFriend")
            call_obj.send_keys(random.choice(self.call_content_list))
            self.driver.find_element_by_id("com.zing.zalo:id/btnSendInvitation").click()
            if not self.Search_label_id("com.zing.zalo:id/profile_cover_gradient"):
                self.Result["msg"] = "Đã gửi full lời mời kết bạn trong ngày."
                return True
            self.add_count -= 1
            self.now_succeed_number += 1
            # print("添加成功！！！！！！！")
            self.Result["valid_add_friend"] += 1
            return False
        else:
            if not self.Search_label_id("com.zing.zalo:id/btn_function_1"):
                return False
            btn1 = self.driver.find_element_by_id("com.zing.zalo:id/btn_function_1")
            btn1.click()
            if self.Send_msg_friend(self.photo_list, random.choice(self.call_content_list)):
                # print("发送成功！！！！！！！！！")
                self.Result["valid_send_gale"] += 1
            self.send_count -= 1
            self.now_succeed_number += 1
            return False

    def Find_start_index(self):
        start_index = self.start_friend_index + self.now_succeed_number
        now_index = 0
        while start_index > now_index:
            index = start_index - now_index
            if index > 9:
                self.Swipe_down(0.9, 0.1)
                now_index += 9
            else:
                down = index / 10
                self.Swipe_down(down, 0.1)
                now_index += index

    def Add_or_send_friend(self, friend_list, name_key):
        """
        friend_list: 主要是提供索引，每次都重新获取用户对象，避免报错
        :return:
        """
        for friend in range(friend_list):
            if self.now_succeed_number >= self.sum_count: return
            status = True
            friend_list = self.driver.find_elements(By.ID, name_key)
            friend_name = friend_list[friend].text
            if friend_name in self.friend_name_list:
                continue
            if self.send_count > 0:
                status = False
            friend_list[friend].click()
            if self.Add_people_nearby_request(status):
                # 如果为真则不能继续添加了
                return True
            self.friend_name_list.append(friend_name)
            self.driver.find_element_by_id("com.zing.zalo:id/home").click()
            time.sleep(self.add_sleep)

    def Add_people_nearby_operation(self):
        """
        判断当前是否在最底层
        """
        while self.sum_count > self.now_succeed_number:
            friend_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/tv_name")
            end_friend = friend_list[-1].get_attribute("text")
            if self.end_element == end_friend:
                self.Result["msg"] = "Đã kết bạn/ gửi tin người xung quanh hoàn tất."
                return
            self.end_element = end_friend
            if self.Add_or_send_friend(len(friend_list), "com.zing.zalo:id/tv_name"):
                return
            self.Swipe_down(0.9, 0.1)
        self.Result["msg"] = "Kết bạn/Gửi tin người xung quanh hoàn tất."

    def Add_people_nearby(self):
        """
        进入附近人功能，允许报错四次根据原位置重新执行。
        """
        error_number = 0
        while error_number < 4:
            try:
                self.driver.set_location(self.latitude, self.longitude)
                self.Add_people_nearby_init()
                # 如果附近没有好友
                if self.Search_label_id("com.zing.zalo:id/btn_refresh"):
                    self.Result["code"] = 403
                    self.Result["msg"] = "Không có người xung quanh. Nếu TK xuất hiện nhiều lần, có thể TK đã bị khóa."
                else:
                    self.Find_start_index()
                    self.Add_people_nearby_operation()
                return self.Result
            except BaseException as b:
                # LogRecord.error(str(b))
                error_number += 1
                self.end_element = None
        self.Result["code"] = 500
        self.Result["msg"] = "Thất bại nhiều lần, bắt buộc đăng xuất."
        return self.Result

    # ----------------------------------------聊天室--------------------------------------------------------------
    def Add_Chat_Rooms_init(self):
        self.cut_zalo()
        self.Choice_index(4)
        self.driver.find_element_by_id("com.zing.zalo:id/layout_room_container").click()


    def find_room(self, room_index, room_name):
        class_room = self.driver.find_elements(By.ID, "com.zing.zalo:id/name")
        for room in class_room:
            if room_index in room.text:
                room.click()
                break
        end_room_name = ""
        while True:
            room_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/name")
            _room_name = ""
            for room in room_list:
                _room_name = room.text.split("(")[0].strip()
                if room_name == _room_name:
                    room.click()
                    return True
            if _room_name == end_room_name:
                return False
            end_room_name = _room_name
            self.Swipe_down(0.99, 0.1)


    def Add_Chat_Rooms_operation(self):
        """
        判断当前是否在最底层
        """
        while self.sum_count > self.now_succeed_number:
            friend_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/name")
            end_friend = friend_list[-1].get_attribute("text")
            if self.end_element == end_friend:
                self.Result["msg"] = "Đã kết bạn/gửi tin theo PTC hoàn tất."
                return
            self.end_element = end_friend
            if self.Add_or_send_friend(len(friend_list), "com.zing.zalo:id/name"):
                return
            self.Swipe_down(0.9, 0.1)

    def Add_Chat_Rooms(self, room_index, room_name):
        """
        room_index 聊天室分类
        room_name  聊天室名称
        """
        error_number = 0
        while error_number < 4:
            try:
                self.Add_Chat_Rooms_init()
                if self.Search_label_id("com.zing.zalo:id/btn_refresh"):
                    # self.Result["msg"] = "无法刷新出聊天室，如果出现多次，该账户可能已被封号"
                    self.Result["msg"] = "Không thể làm mới PTC. Nếu TK xuất hiện nhiều lần, có thể TK đã bị khóa."
                    self.Result["code"] = 404
                else:
                    if self.find_room(room_index, room_name):
                        self.Find_start_index()
                        self.Add_Chat_Rooms_operation()
                        # self.Result["msg"] = "添加/发送聊天室好友执行完毕."
                        self.Result["msg"] = "Kết bạn/ Gửi tin vào nhóm bạn bè hoàn tất."
                    else:
                        # self.Result["msg"] = "没有找到对应的聊天室，请重试。"
                        self.Result["msg"] = "Chưa tìm được chính xác phòng trò chuyện, vui lòng thử lại."
                        self.Result["code"] = 404
                return self.Result
            except BaseException as b:
                # LogRecord.error(str(b))
                error_number += 1
                self.end_element = None
        self.Result["code"] = 500
        self.Result["msg"] = "Thất bại nhiều lần, bắt buộc đăng xuất."
        return self.Result

    def get_chat_room_class(self):
        # 进入聊天室分类
        room_name_list = []
        end_element = None
        while True:
            room_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/name")
            for room in range(len(room_list)):
                room_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/name")
                room_name = room_list[room].text
                if "(" in room_name or ")" in room_name:
                    if room_name not in room_name_list:
                        room_name_list.append(room_name)
            self.Swipe_down(0.9, 0.1)
            try:
                if room_list[-1].text == end_element:
                    return room_name_list
                end_element = room_list[-1].text
            except:
                return room_name_list

    def Add_Chat_Room_dict(self):
        """
        获取所有的聊天室分类，以及分类下的所有聊天室。
        """
        self.cut_zalo()
        self.Choice_index(4)
        self.driver.find_element_by_id("com.zing.zalo:id/layout_room_container").click()
        class_room_name = self.driver.find_elements(By.ID, "com.zing.zalo:id/name")
        for c_room in range(len(class_room_name)):
            class_room_name = self.driver.find_elements(By.ID, "com.zing.zalo:id/name")
            class_room_name[self.room_id].click()
            room_key = class_room_name[self.room_id].text
            self.Chat_Room_dict[room_key] = self.get_chat_room_class()
            self.driver.find_element_by_id("com.zing.zalo:id/home").click()
            self.driver.find_element_by_id("com.zing.zalo:id/layout_room_container").click()
            self.room_id += 1

    def Get_Chat_Rooms(self):
        error_number = 0
        self.room_id = 0
        while error_number < 4:
            try:
                self.Add_Chat_Room_dict()
                return self.Chat_Room_dict
            except BaseException as b:
                # LogRecord.error(str(b))
                error_number += 1
                self.end_element = None
        return {}
