# -*- coding: utf-8 -*-
__author__ = 'Luke'

from zalo_appium.StratAppium import BaseAppium
from selenium.webdriver.common.by import By
# from common.log import LogRecord
import time

class Operation(BaseAppium):
    """ 通过好友请求"""

    def __init__(self, Appium_ip, udid, sysport):
        BaseAppium.__init__(self, Appium_ip, udid, sysport)
        self.friend_request_sum = 0

    def init_add_friend(self):
        self.cut_zalo()
        self.Choice_index(1)
        self.driver.find_element_by_id("com.zing.zalo:id/fLayoutfriendsuggest").click()

    def accept(self):
        """ 通过请求"""
        friend_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/info_contact_row")
        friend_add = friend_list[0].find_elements(By.ID, "com.zing.zalo:id/btn_combine_func_1")
        if friend_add:
            friend_add[0].click()
            if self.Search_label_id("com.zing.zalo:id/message"):
                self.driver.find_element_by_id("com.zing.zalo:id/button1").click()
            else:
                self.friend_request_sum += 1
                self.Result["valid_accept_request"] += 1
        friend_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/info_contact_row")
        friend_list[0].find_element_by_id("com.zing.zalo:id/btn_combine_func_3").click()

    def find_friend_request(self):
        """ 找到所有请求"""
        self.Search_label_id("com.zing.zalo:id/tvTitleSeeMore", True)
        while True:
            time.sleep(1)
            friend_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/info_contact_row")
            if friend_list:
                self.accept()
            else:
                return

    def start_accept_friend_request(self):
        error_number = 0
        while error_number < 4:
            try:
                self.init_add_friend()
                self.find_friend_request()
                self.Result["msg"] = "Chấp nhận lời mời kết bạn."
                return self.Result
            except BaseException as b:
                # LogRecord.error(str(b))
                error_number += 1
        self.Result["code"] = 500
        self.Result["valid_accept_request"] = self.friend_request_sum
        self.Result["msg"] = "Thất bại nhiều lần, bắt buộc đăng xuất"
        return self.Result
