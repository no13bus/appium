# -*- coding: utf-8 -*-
__author__ = 'Luke'

from zalo_appium.StratAppium import BaseAppium
# from common.log import LogRecord
import linecache
import random


class Operation(BaseAppium):
    """
    添加手机号
    """

    def __init__(self, Appium_ip, udid, sysport, phone_number_file_path, call, photo_list, is_send, phonenumber_count,
                 device_number):
        BaseAppium.__init__(self, Appium_ip, udid, sysport)
        self.index = 1
        self.error_index = 0
        self.phone_number_file_path = phone_number_file_path
        self.call = call
        self.photo_list = photo_list
        self.is_send = is_send
        self.phonenumber_count = phonenumber_count
        self.StartPosition = phonenumber_count * device_number

    def add_friend_init(self):
        self.cut_zalo()
        self.Choice_index(1)
        xpath = "//*[@resource-id='com.zing.zalo:id/zalo_action_bar']/android.widget.LinearLayout[2]"
        self.driver.find_element_by_xpath(xpath).click()

    def get_file(self):
        phone_number = linecache.getline(self.phone_number_file_path,
                                         (self.StartPosition + self.index + self.error_index)
                                         )
        if phone_number:
            phon_info = phone_number.strip("\n").replace(" ", "").split("|")
            return phon_info[0], phon_info[1]
        return None, None

    def Choice_Search(self, search):
        """ 选择国家 """
        self.driver.find_element_by_id("com.zing.zalo:id/tv_country").click()
        self.driver.find_element_by_id("com.zing.zalo:id/search_src_text").send_keys(search)
        self.driver.find_element_by_id("com.zing.zalo:id/name").click()

    def add_phonenumber(self, btn_function_2):
        """ 添加手机号"""
        if btn_function_2.get_attribute("text") == "UNDO REQUEST":
            self.error_index += 1
        else:
            self.driver.find_element_by_id("com.zing.zalo:id/btn_function_2").click()
            self.driver.find_element_by_id("com.zing.zalo:id/edtInvitationFriend").send_keys(random.choice(self.call))
            self.driver.find_element_by_id("com.zing.zalo:id/btnSendInvitation").click()
            self.Search_label_id("com.zing.zalo:id/button2", True)
            self.Result["valid_add_friend"] += 1

    def sned_phonenumber(self):
        """ 发送消息"""
        self.driver.find_element_by_id("com.zing.zalo:id/btn_function_1").click()
        res = self.Send_msg_friend(self.photo_list, random.choice(self.call))
        if res:
            self.Result["valid_send_msg"] += 1

    def Ipnut_phone_number(self):
        while (self.index + self.error_index) < self.phonenumber_count:
            search, phone_number = self.get_file()
            # print("{}还有".format(self.udid), search, phone_number)
            if not phone_number:
                # print("{}----到底退出了？".format(self.udid))
                self.Result["msg"] = "Đã hoàn tất, Thành công({}) Thất bại({})".format(self.index, self.error_index)
                return
            self.Choice_Search(search)
            self.driver.find_element_by_id("com.zing.zalo:id/edt_phone_number").send_keys(phone_number)
            self.driver.find_element_by_id("com.zing.zalo:id/tv_search").click()
            if self.Search_label_id("com.zing.zalo:id/parentPanel"):
                self.error_index += 1
                if not self.Search_label_id("com.zing.zalo:id/button2", True):
                    self.driver.find_element_by_id("com.zing.zalo:id/button1").click()
            else:
                btn_function_2 = self.Search_label_id("com.zing.zalo:id/btn_function_2")
                if btn_function_2:
                    if self.is_send:
                        self.sned_phonenumber()
                    else:
                        self.add_phonenumber(btn_function_2)
                # print("{}----添加成功了？".format(self.udid))
                self.driver.find_element_by_id("com.zing.zalo:id/home").click()
                self.index += 1
        self.index -= 1
        self.Result["msg"] = "Kết bạn/ Gửi tin theo SĐT đã hoàn tất. Thành công({}) Thất bại({})".format(self.Result["valid_add_friend"], self.error_index)


    def Add_friend_number(self):
        error_number = 0
        while error_number < 4:
            try:
                # print("{}--------开始了".format(self.udid))
                self.add_friend_init()
                self.Ipnut_phone_number()
                # print("{}操作结束了？".format(self.udid))
                return self.Result
            except BaseException as b:
                # LogRecord.error(str(b))
                error_number += 1
        self.Result["code"] = 500
        self.Result["msg"] = "Thất bại nhiều lần, bắt buộc đăng xuất. Thành công({}) Thất bại({})".format(self.Result["valid_add_friend"], self.error_index)
        # print("{}报错退出了？".format(self.udid))
        return self.Result
