# -*- coding: utf-8 -*-
__author__ = 'Luke'

from selenium.webdriver.common.by import By
from appium import webdriver
from settings import *
import random
import time


class BaseAppium:

    def __init__(self, Appium_ip, udid, sysport):
        appium_caps["udid"] = udid
        appium_caps["deviceName"] = udid
        appium_caps["systemPort"] = sysport
        self.udid = udid
        self.driver = webdriver.Remote(Appium_ip, appium_caps)
        self.driver.implicitly_wait(20)  # 隐式等待，每0.5秒查询一次，直到指定时间，结束。单位是秒
        self.screen_x_width = self.driver.get_window_size()["width"]
        self.screen_y_height = self.driver.get_window_size()["height"]
        self.Result = {
            "code": 200, "valid_send_msg": 0, "valid_add_friend": 0,
            "valid_send_gale": 0, "valid_accept_request": 0,
            "data": "", "msg": ""
        }

    def Search_label_id(self, label, click=False):
        """Check that the current page has a corresponding label"""
        label_value = self.driver.find_elements(By.ID, label)
        if label_value:
            if click:
                label_value[0].click()
            return label_value[0]
        return False


    def Permissions_allow(self):
        """ authorization """
        time.sleep(1)
        self.Search_label_id("com.android.packageinstaller:id/permission_allow_button", True)


    def Choice_index(self, index):
        """ Select function page """
        '''
        Function page switching
        index: It's between 0 and 4
        '''
        id_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/frametabsLayout")
        id_list[index].click()

    def Zalo_init(self, ):
        """ Initialization selection """
        if self.Search_label_id("com.zing.zalo:id/btn_next", True):
            self.driver.find_element_by_id('com.zing.zalo:id/btn_next').click()
            self.driver.find_element_by_id('com.zing.zalo:id/btn_next').click()

    def retry(self):
        """ 重试登录 """
        try:
            self.driver.find_element_by_id("com.zing.zalo:id/btnLogin").click()
        except:
            pass

    def error_prompt(self, index=1):
        """ 获取报错信息,如果是提示网络错误则重试 """
        if index < 4:
            if self.Search_label_id("com.zing.zalo:id/btnLogin"):
                hint = self.driver.find_element_by_id('com.zing.zalo:id/tvError')
                hint_content = hint.text
                error_info = hint_content.replace("\n", "")
                error_code = error_info.split("(")[1].split(")")[0]
                if error_code != "502":
                    self.Result["code"] = error_code
                    self.Result["msg"] = error_info
                    return True
                else:
                    self.retry()
                index += 1
                return self.error_prompt(index)
            else:
                return False
        else:
            return True

    def IGNORE(self):
        """ Synchronization of device information is required when logging in """
        try:
            self.driver.find_element_by_id("com.zing.zalo:id/btnIgnoreRestore").click()
            self.driver.find_element_by_id("com.zing.zalo:id/btnConfirmPhoneBookYes").click()
        except:
            self.driver.find_element_by_id("com.zing.zalo:id/button1").click()

    def SKIP(self):
        try:
            self.driver.find_element_by_id("com.zing.zalo:id/btnConfirmPhoneBookNo").click()
        except:
            pass

    def Login_Get_Code(self):
        """  Determines whether the current page needs to enter a captcha"""
        if self.Search_label_id("com.zing.zalo:id/tvHint") and self.Search_label_id("com.zing.zalo:id/btnNext"):
            self.driver.find_element_by_id("com.zing.zalo:id/btnNext").click()
            phone = self.driver.find_element_by_id("com.zing.zalo:id/phoneNumber")
            phone_number = phone.text.replace(")", "").replace("(", "").replace("+", "")
            self.driver.find_element_by_id("com.zing.zalo:id/confirm_btn_yes").click()
            error = self.Search_label_id("com.zing.zalo:id/message")
            if error:
                # error = self.driver.find_element_by_id("com.zing.zalo:id/message")
                error_msg = error.text
                # self.driver.find_element_by_id("com.zing.zalo:id/button2").click()
                self.Result["code"] = 402
                self.Result["msg"] = error_msg.replace("\n", "")
            else:
                self.Result["code"] = 302
                self.Result["data"] = phone_number.replace(" ", "")


    def Verify_friend(self):
        """Determines whether the current page needs to validate friends' profile pictures"""
        if self.Search_label_id("com.zing.zalo:id/btn_next") and self.Search_label_id("com.zing.zalo:id/tv_note"):
            self.driver.find_element_by_id("com.zing.zalo:id/btn_next").click()
            friend_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/pick_friend_checkbox")
            friend_list[1].click()
            time.sleep(1)
            friend_list[4].click()
            self.driver.find_element_by_id("com.zing.zalo:id/btn_answer").click()
            if self.Search_label_id("com.zing.zalo:id/tv_note") and self.Search_label_id("com.zing.zalo:id/btn_next"):
                self.driver.find_element_by_id("com.zing.zalo:id/btn_next").click()
                friend_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/pick_friend_checkbox")
                friend_list[2].click()
                time.sleep(1)
                friend_list[3].click()
                self.driver.find_element_by_id("com.zing.zalo:id/btn_answer").click()
        if self.Search_label_id("com.zing.zalo:id/parenLayout_alert_dlg"):
            self.driver.find_element_by_id("com.zing.zalo:id/button1").click()
            phone = self.driver.find_element_by_id("com.zing.zalo:id/phoneNumber")
            phone_number = phone.text
            self.driver.find_element_by_id("com.zing.zalo:id/confirm_btn_yes").click()
            self.Result["code"] = 302
            self.Result["data"] = phone_number.replace(" ", "")
            return
        self.Result["code"] = 200

    def Upload_pictures(self, phone_file_path, file_path=None, base64=None):
        '''
        Upload local file to mobile phone
        '''
        if file_path:
            self.driver.push_file(phone_file_path, source_path=file_path)
        elif base64:
            self.driver.push_file(phone_file_path, base64)
        else:
            return {"code": 400, "msg": "A file transfer type needs to be specified"}

    def Friend_circle_gps(self):
        """ Send location selection """
        self.driver.find_element_by_id("com.zing.zalo:id/tv_add_location").click()
        # 会拖慢速度
        # if self.Search_label_id("com.zing.zalo:id/button2"):
        #     self.driver.find_element_by_id("com.zing.zalo:id/button2").click()
        # if self.Search_label_id("com.zing.zalo:id/btn_refresh"):
        #     self.driver.find_element_by_id("com.zing.zalo:id/home").click()
        # else:
        time.sleep(1)
        lo_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/location_title")
        if len(lo_list) > 1:
            index = random.randint(1, len(lo_list))
            lo_list[index].click()
        else:
            self.driver.find_element_by_id("com.zing.zalo:id/home").click()

    def Choice_send_Photo(self, Photo_number):
        """ Select photos to send to your circle of friends """
        if isinstance(Photo_number, int):
            photo_list = self.driver.find_elements(By.ID, "com.zing.zalo:id/check_icon")
            if Photo_number > len(photo_list):
                Photo_number = len(photo_list)
            for i in range(0, Photo_number):
                photo_list[i].click()


    def Send_msg_friend(self, photo_list, msg):
        """
        图片提交多少就发送多少
        :param msg: 消息
        :return:
        """
        code = True
        if photo_list:
            self.driver.find_element_by_id("com.zing.zalo:id/new_chat_input_btn_show_gallery").click()
            self.Choice_send_Photo(len(photo_list))
            self.driver.find_element_by_id("com.zing.zalo:id/new_chat_input_btn_send_media").click()
        input_case = self.driver.find_element_by_id("com.zing.zalo:id/chatinput_text")
        input_case.send_keys(msg)
        self.driver.find_element_by_id("com.zing.zalo:id/new_chat_input_btn_chat_send").click()
        # 这里判断下，对方是否拒绝接收自己的消息。
        xpath = "//*[@resource-id='com.zing.zalo:id/chatlinelist']/android.view.View"
        msg_list = self.driver.find_elements_by_xpath(xpath)
        if send_msg_gale in msg_list[-1].text:
            code = False
        self.driver.find_element_by_id("com.zing.zalo:id/home").click()
        return code

    def Swipe_down(self, start_y=0.75, end_y=0.25, duration=3000):
        ''' Hold down the screen to swipe down'''
        time.sleep(2)
        start_x = int(self.screen_x_width * 0.5)
        end_x = int(self.screen_x_width * 0.5)
        s_y = int(self.screen_y_height * start_y)
        e_y = int(self.screen_y_height * end_y)
        self.driver.swipe(start_x, s_y, end_x, e_y, duration)

    def command(self, order):
        time.sleep(1)
        os.system(order)

    def cut_zalo(self):
        # 切换APP到ZALO
        order = "adb -s {} shell am force-stop {}".format(self.udid, ZALO_appPackage)
        self.command(order)
        order = "adb -s {} shell am start {}/{}".format(self.udid, ZALO_appPackage, ZALO_appActivity)
        self.command(order)
        time.sleep(5)
        try:
            self.driver.find_element_by_id("com.zing.zalo:id/btnConfirmPhoneBookNo").click()
        except:
            pass
        button2 = self.Search_label_id("com.zing.zalo:id/button2")
        if button2:
            button2.click()


    def cut_vpn(self):
        order = "adb -s {} shell am force-stop  {}".format(self.udid, OpenVPN_appPackage)
        self.command(order)
        order = "adb -s {} shell am start {}/{}".format(self.udid, OpenVPN_appPackage, OpenVPN_appActivity)
        self.command(order)
        time.sleep(5)
