# -*- coding: utf-8 -*-
__author__ = 'Luke'

from zalo_appium.StratAppium import BaseAppium
# from common.log import LogRecord
import random


class Operation(BaseAppium):
    """ 发送朋友圈"""

    def __init__(self, Appium_ip, udid, sysport, content_list, Photo_number, longitude, latitude):
        BaseAppium.__init__(self, Appium_ip, udid, sysport)
        self.Photo_number = Photo_number
        self.content_list = content_list
        self.longitude = longitude
        self.latitude = latitude

    def send_friend_circle(self):
        '''
        content:Circle of friends to send text content
        Photo_number: Click on the number of photos and sort them strictly according to upload order
        '''
        error_number = 0
        while error_number < 4:
            try:
                self.driver.set_location(self.latitude, self.longitude)
                self.cut_zalo()
                self.Choice_index(3)
                self.driver.find_element_by_id("com.zing.zalo:id/tv_hint").click()
                self.Friend_circle_gps()
                self.Choice_send_Photo(self.Photo_number)
                input_content = self.driver.find_element_by_id("com.zing.zalo:id/etDesc")
                input_content.send_keys(random.choice(self.content_list))
                self.driver.find_element_by_id("com.zing.zalo:id/menu_done").click()
                self.Result["msg"] = "Gửi tin đăng tường thành công."
                return self.Result
            except BaseException as b:
                # LogRecord.error(str(b))
                error_number += 1
        self.Result["code"] = 500
        self.Result["msg"] = "Gửi tin đăng tường thất bại nhiều lần, đã bị đăng xuất."
        return self.Result
