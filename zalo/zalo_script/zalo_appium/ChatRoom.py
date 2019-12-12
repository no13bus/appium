# -*- coding: utf-8 -*-
__author__ = 'Luke'

from zalo_appium.StratAppium import BaseAppium
from selenium.webdriver.common.by import By
# from common.log import LogRecord
import random
import time
import os


class Operation(BaseAppium):
    """ 进入群聊分类发消息 """

    def __init__(self, Appium_ip, udid, sysport, call_content_list, group_room_index, group_room_sleep):
        BaseAppium.__init__(self, Appium_ip, udid, sysport)
        self.room_calss = group_room_index
        self.room_name_list = []
        self.call_content_list = call_content_list
        self.sleep = group_room_sleep

    def init_room(self):
        self.cut_zalo()
        self.Choice_index(4)
        self.driver.find_element_by_id("com.zing.zalo:id/layout_room_container").click()

    def init_find_index(self):
        room_class_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/contact_row")
        if self.room_calss >= len(room_class_list):
            self.room_calss = len(room_class_list) - 1
        room_class_list[self.room_calss].click()
        _end = None
        while True:
            room_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/name")
            end_name = room_list[-1].text
            self.send_chat_room(len(room_list))
            if _end == end_name:
                return
            _end = end_name
            self.Swipe_down(0.9, 0.1)

    def send_msg(self):
        call = self.driver.find_element_by_id("com.zing.zalo:id/chatinput_text")
        call.send_keys(random.choice(self.call_content_list))
        self.driver.find_element_by_id("com.zing.zalo:id/new_chat_input_btn_chat_send").click()
        self.driver.find_element_by_id("com.zing.zalo:id/home").click()
        self.driver.find_element_by_id("com.zing.zalo:id/home").click()
        self.driver.find_element_by_id("com.zing.zalo:id/button2").click()

    def send_chat_room(self, room_range):
        for room in range(room_range):
            _room_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/name")
            room_name = _room_list[room].text
            if "(" in room_name or ")" in room_name:
                if room_name not in self.room_name_list:
                    _room_list[room].click()
                    if not self.Search_label_id("com.zing.zalo:id/tv_join_room", True):
                        self.driver.find_element_by_id("com.zing.zalo:id/home").click()
                        continue
                    if not self.Search_label_id("com.zing.zalo:id/button2", True):
                        order = r"adb -s {}  shell for i in `seq 1 20`; do dd if=/sdcard/event1 of=/dev/input/event1;sleep 0.1; done".format(self.udid)
                        os.system(order)
                    if self.Search_label_id("com.zing.zalo:id/chatinput_text"):
                        self.send_msg()
                    else:
                        self.driver.find_element_by_id("com.zing.zalo:id/home").click()
                        self.driver.find_element_by_id("com.zing.zalo:id/button2").click()
            self.room_name_list.append(room_name)
            time.sleep(1 + self.sleep)

    def statr_send_room(self):
        error_number = 0
        while error_number < 4:
            try:
                self.init_room()
                if self.Search_label_id("com.zing.zalo:id/btn_refresh"):
                    self.Result["msg"] = "Không tìm thấy PTC. Nếu TK xuất hiện nhiều lần, có thể TK đã bị khóa."
                    self.Result["code"] = 404
                else:
                    self.init_find_index()
                    self.Result["msg"] = "Phân loại gửi tin thành công ({}) PTC. ".format(len(self.room_name_list))
                return self.Result
            except BaseException as b:
                # LogRecord.error(str(b))
                error_number += 1
        self.Result["code"] = 500
        self.Result["msg"] = "Thất bại nhiều lần, bắt buộc đăng xuất."
        return self.Result
