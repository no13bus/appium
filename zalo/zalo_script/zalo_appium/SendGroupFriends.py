# -*- coding: utf-8 -*-
__author__ = 'Luke'

from zalo_appium.StratAppium import BaseAppium
from selenium.webdriver.common.by import By
# from common.log import LogRecord
import random
import time


class Operation(BaseAppium):
    """ 群发好友 """

    def __init__(self, Appium_ip, udid, sysport, call_content_list, photo_list, time_out):
        BaseAppium.__init__(self, Appium_ip, udid, sysport)
        self.call_content_list = call_content_list
        self.now_succeed_number = 0
        self.photo_list = photo_list
        self.time_out = time_out
        self.now_succeed_number = 0
        self.friend_name_list = []

    def App_init(self):
        self.cut_zalo()
        self.Choice_index(1)

    def Find_start_index(self):
        """ 查找到第一个好友 """
        self.Swipe_down(0.9, 0.1)
        while self.Search_label_id("com.zing.zalo:id/btnRefresh"):
            if self.Search_label_id("com.zing.zalo:id/tv_update_phonebook"):
                return
            self.Swipe_down(0.7, 0.5)
        if self.now_succeed_number:
            index = 0
            if self.now_succeed_number > 6:
                self.Swipe_down(0.9, 0.1)
                index += 6
            else:
                down = index / 6
                self.Swipe_down(down, 0.1)

    def Send_msg(self):
        """ 发送消息 """
        while True:
            friend_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/name")
            for friend in range(len(friend_list)):
                friend_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/name")
                friend_name = friend_list[friend].text
                if friend_name in self.friend_name_list:
                    continue
                friend_list[friend].click()
                self.friend_name_list.append(friend_name)
                time.sleep(self.time_out)
                if self.Send_msg_friend(self.photo_list, random.choice(self.call_content_list)):
                    self.Result["valid_send_msg"] += 1
                self.now_succeed_number += 1
            if self.Search_label_id("com.zing.zalo:id/tv_update_phonebook"):
                self.Result["msg"] = "Gửi tin/ kết bạn PTC hoàn tất."
                return
            self.Swipe_down(0.9, 0.1)

    def send_msg_all_friend(self):
        """ Text all your friends  """
        error_number = 0
        while error_number < 4:
            try:
                self.App_init()
                self.Find_start_index()
                self.Send_msg()
                return self.Result
            except BaseException as b:
                # LogRecord.error(str(b))
                error_number += 1
        self.Result["code"] = 500
        self.Result["msg"] = "Gửi tin/ kết bạn PTC thất bại nhiều lần, đã bị đăng xuất."
        return self.Result
