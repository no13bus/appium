# -*- coding: utf-8 -*-
__author__ = 'Luke'

from zalo_appium.StratAppium import BaseAppium
from selenium.webdriver.common.by import By
from common.redis_conn import *
from common.file_handling import UpdatePhoneInfo
# from common.log import LogRecord
import time
import json
import os


class Operation(BaseAppium):
    """ 登录"""

    def __init__(self, Appium_ip, udid, sysport, vpn_name, username, password, user_id, VPN_status):
        BaseAppium.__init__(self, Appium_ip, udid, sysport)
        self.vpn_name = vpn_name
        self.username = username
        self.password = password
        self.user_id = user_id
        self.VPN_status = VPN_status

    def out_init(self):
        self.cut_zalo()
        if self.Search_label_id("com.zing.zalo:id/btnLogin"):
            return True
        self.Choice_index(4)

    def out_core(self):
        xpath = "//*[@resource-id='com.zing.zalo:id/zalo_action_bar']/android.widget.LinearLayout[2]/android.widget.FrameLayout[2]"
        self.driver.find_element_by_xpath(xpath).click()
        self.driver.find_element_by_id("com.zing.zalo:id/ll_setting_logout").click()
        self.driver.find_element_by_id("com.zing.zalo:id/button1").click()

    def open_roots_list(self):
        """ 打开手机存储"""
        try:
            xpath = "//*[@content-desc='显示根目录']"
            self.driver.find_element_by_xpath(xpath).click()
        except:
            pass
        xpath = "//*[@resource-id='com.android.documentsui:id/roots_list']/android.widget.LinearLayout[3]"
        self.driver.find_element_by_xpath(xpath).click()

    def Start_vpn(self):
        """ 启动 open_vpn"""
        self.QuitVpn()
        title_list = self.driver.find_elements(By.ID, "de.blinkt.openvpn:id/tab_title")
        title_list[2].click()
        check_list = self.driver.find_elements(By.ID, "android:id/checkbox")
        tag = check_list[2].get_attribute("checked")
        if tag != "true":
            check_list[2].click()
        title_list = self.driver.find_elements(By.ID, "de.blinkt.openvpn:id/tab_title")
        title_list[0].click()
        xpath = "//*[@content-desc='添加']"
        English_xpath = "//*[@content-desc='Add']"
        try:
            self.driver.find_element_by_xpath(English_xpath).click()
        except:
            self.driver.find_element_by_xpath(xpath).click()
        self.driver.find_element_by_id("android:id/button3").click()
        if not self.Search_label_id("com.android.documentsui:id/menu_search"):
            self.open_roots_list()
        self.driver.find_element_by_id("com.android.documentsui:id/menu_search").click()
        _input = self.driver.find_element_by_id("android:id/search_src_text")
        _input.send_keys(self.vpn_name)
        time.sleep(1)
        os.system("adb -s {} shell input keyevent 66".format(self.udid))
        time.sleep(1)
        self.driver.find_element_by_id("com.android.documentsui:id/icon_thumb").click()
        self.driver.find_element_by_id("de.blinkt.openvpn:id/ok").click()
        self.driver.find_element_by_id("de.blinkt.openvpn:id/vpn_list_item_left").click()
        self.Search_label_id("android:id/button1", True)


    def QuitVpn(self):
        """ 退出vpn """
        self.cut_vpn()
        if self.Search_label_id("de.blinkt.openvpn:id/vpn_item_title"):
            self.driver.find_element_by_id("de.blinkt.openvpn:id/quickedit_settings").click()
            self.driver.find_element_by_id("de.blinkt.openvpn:id/remove_vpn").click()
            self.driver.find_element_by_id("android:id/button1").click()

    def get_code(self, phone_number):
        """
        获取验证码
        """
        for i in range(40):
            if redis_cache.exists(phone_number):
                code_data = json.loads(redis_cache.get(phone_number))
                code_list = [int(i) for i in code_data["code"]]
                redis_cache.delete(phone_number)
                self.Result["code"] = 200
                self.Result["data"] = code_list
                return
            time.sleep(5)
        self.Result["code"] = 400
        self.Result["msg"] = "Đã quá thời gian nhận mã xác nhận, vui lòng đăng nhập lại."

    def Input_code(self, code):
        """ Type the login verification code """
        error_number = 0
        while error_number < 2:
            try:
                xpath = "//*[@resource-id='com.zing.zalo:id/scrollView']/android.widget.LinearLayout[1]/android.widget.LinearLayout[2]/android.widget.TextView[1]"
                self.driver.find_element_by_xpath(xpath).click()
                for i in code:
                    order = "adb -s {} shell input text {}".format(self.udid, i)
                    os.system(order)
                self.driver.find_element_by_id("com.zing.zalo:id/btnSubmitActivationCode").click()
                self.update_password()
                if self.Search_label_id("com.zing.zalo:id/btnSubmitActivationCode"):
                    error = self.driver.find_element_by_id("com.zing.zalo:id/tvDes")
                    error_msg = error.text
                    self.Result["code"] = 402
                    self.Result["msg"] = error_msg.replace("\n", "")
                else:
                    self.Result["code"] = 200
                    self.Result["msg"] = "Nhận mã xác nhận thành công, đăng nhập thành công."
                return
            except BaseException as b:
                error_number += 1
        self.Result["code"] = 403
        self.Result["msg"] = "Nhập mã xác nhận thất bại nhiều lần."

    def update_password(self):
        if self.Search_label_id("com.zing.zalo:id/btnNext", True):
            self.driver.find_element_by_id("com.zing.zalo:id/et_newpass").send_keys("root!@#2019")
            self.driver.find_element_by_id("com.zing.zalo:id/et_newpass_confirm").send_keys("root!@#2019")
            self.driver.find_element_by_id("com.zing.zalo:id/layout_dochangepass").click()
            self.driver.find_element_by_id("com.zing.zalo:id/button1").click()
            UpdatePhoneInfo({"udid": self.udid, "Param": json.dumps({"password": "root!@#2019"})})

    def login_init(self):
        """ 初始化到登陆页面 """
        self.cut_zalo()
        self.Zalo_init()

    def restore_chat_history(self):
        """ 恢复聊天记录 """
        if self.Search_label_id("com.zing.zalo:id/btnRestoreData"):
            self.driver.find_element_by_id("com.zing.zalo:id/btnIgnoreRestore")
            self.driver.find_element_by_id("com.zing.zalo:id/button1")

    def input_user_password(self):
        """ Landing zalo """
        for i in range(2):
            if self.Search_label_id("com.zing.zalo:id/btnLogin"):
                self.driver.find_element_by_id('com.zing.zalo:id/str_language_applied_en').click()
                self.driver.find_element_by_id("com.zing.zalo:id/btnLogin").click()
                user = self.driver.find_element_by_id("com.zing.zalo:id/edtAccount")
                user.send_keys(self.username)
                pwd = self.driver.find_element_by_id("com.zing.zalo:id/edtPass")
                pwd.send_keys(self.password)
                self.driver.find_element_by_id("com.zing.zalo:id/btnLogin").click()
                if self.Search_label_id("com.zing.zalo:id/sliding_tabs"):
                    # self.Result["msg"] = "登录成功!"
                    self.Result["msg"] = "Đăng nhập thành công."
                    return
                elif self.Search_label_id("com.zing.zalo:id/btnIgnoreRestore"):
                    self.IGNORE()
                    self.SKIP()
                    # self.Result["msg"] = "登录成功!"
                    self.Result["msg"] = "Đăng nhập thành công."
                    return
                self.Result["code"] = 500
                # self.Result["msg"] = "遇到其它登录验证..."
                self.Result["msg"] = "Nhận được checkpoint khác."
                return
            time.sleep(5)
        else:
            self.Result["code"] = 200
            # self.Result["msg"] = "已经登录,无需重复登录"
            self.Result["msg"] = "Đã đăng nhập, không thể đăng nhập lại."

    def Login(self):
        self.login_init()
        self.input_user_password()
        if self.Result["code"] == 200:return
        # 判断是否登录成功,如果没有登录成功,返回错误信息,网络问题可重试几次.
        if self.error_prompt(): return
        self.Verify_friend()
        if self.Result["code"] == 200:
            self.Login_Get_Code()
        if self.Result["code"] == 402:
            # 验证码发送超过限量
            return
        if self.Result["code"] == 302:
            redis_set = "{}_code_set".format(self.user_id)
            phone_number = "{}".format(self.Result["data"])
            redis_cache.sadd(redis_set, phone_number)
            self.get_code(phone_number)
            if self.Result["code"] == 200:
                self.Input_code(self.Result["data"])
                if self.Result["code"] == 200:
                    self.IGNORE()
                    self.SKIP()


    def Zalo_Login(self):
        """ zalo登录，已经设置vpn"""
        error_number = 0
        while error_number < 4:
            try:
                if not self.VPN_status:
                    self.Start_vpn()
                    UpdatePhoneInfo({"udid": self.udid, "Param": json.dumps({"VPN_status": 1})})
                    self.VPN_status = 1
                self.Login()
                if self.Result["code"] == 200:
                    UpdatePhoneInfo({"udid": self.udid, "Param": json.dumps({"zalo_status": 1})})
                return self.Result
            except BaseException as b:
                # LogRecord.error(str(b))
                error_number += 1
        self.Result["msg"] = "Thất bại nhiều lần, bắt buộc đăng xuất."
        self.Result["code"] = 500
        return self.Result

    def UpdateVpn(self):
        """ 更换vpn """
        error_number = 0
        q = 1
        while error_number < 4:
            try:
                if q:
                    self.QuitVpn()
                    q = 0
                self.Start_vpn()
                self.Result["msg"] = "Thành công thay đổi VPN."
                return self.Result
            except BaseException as b:
                # LogRecord.error(str(b))
                error_number += 1
        self.Result["code"] = 401
        self.Result["msg"] = "Thay đổi VPN thất bại nhiều lần, đã bị đăng xuất."
        return self.Result

    def logout(self):
        error_number = 0
        while error_number < 4:
            try:
                if self.out_init():
                    return False
                self.out_core()
                return False
            except BaseException as b:
                # LogRecord.error(str(b))
                error_number += 1
        self.Result["msg"] = "Đăng xuất Zalo thất bại nhiều lần, đã bị đăng xuất."
        return self.Result
