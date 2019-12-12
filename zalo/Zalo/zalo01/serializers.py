# -*- coding: utf-8 -*-
__author__ = 'Luke'

from rest_framework import serializers
from zalo01.models import *
import time


class ServerSerializers(serializers.ModelSerializer):
    mobiles = serializers.SerializerMethodField()

    def get_mobiles(self, obj):
        mobiles = PhoneInfo.objects.filter(server=obj)
        return [{"name": mobile.udid, "id": mobile.id, "status": mobile.status} for mobile in mobiles]

    class Meta:
        model = Server
        fields = ["id", "ip", "mobiles"]


class UserSerializers(serializers.ModelSerializer):
    mobile = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()

    def get_mobile(self, obj):
        # obj是当前序列化的book对象
        phones = PhoneInfo.objects.filter(userinfo=obj)
        return [phone.id for phone in phones]

    def get_is_active(self, obj):
        is_active = obj.is_active
        if is_active:
            return "allow"
        return "forbid"

    def get_last_login(self, obj):
        if not obj.last_login:
            return ""
        strtime = time.mktime(obj.last_login.timetuple())
        return time.strftime("%Y-%m-%d %X", time.localtime(strtime))

    def get_date_joined(self, obj):
        strtime = time.mktime(obj.date_joined.timetuple())
        return time.strftime("%Y-%m-%d %X", time.localtime(strtime))

    class Meta:
        model = UserInfo
        # is_staff 是否是管理人员, is_active 账户状态
        fields = ["id", "username", "email", "phone", "is_active", "mobile", "last_login", "date_joined", "password"]


class PhoneSerializers(serializers.ModelSerializer):
    phone_status = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    zalo_id = serializers.SerializerMethodField()
    OpenVpn_name = serializers.SerializerMethodField()
    operation = serializers.SerializerMethodField()
    zalo = serializers.SerializerMethodField()
    vpn = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        if obj.userinfo:
            return obj.userinfo.username
        return ""

    def get_phone_status(self, obj):
        status_dict = {0: "off", 1: "fault", 2: "on"}
        return status_dict[obj.status]

    def get_zalo_id(self, obj):
        if obj.idinfo:
            return obj.idinfo.name
        return ""

    def get_OpenVpn_name(self, obj):
        if obj.OpenVpn:
            return obj.OpenVpn.file_name
        return ""

    def get_operation(self, obj):
        return obj.get_is_operation_display()

    def get_zalo(self, obj):
        return obj.get_zalo_status_display()

    def get_vpn(self, obj):
        return obj.get_VPN_status_display()


    class Meta:
        model = PhoneInfo
        fields = "__all__"
        # fields = ["id", "udid", "phone_status", "zalo_id", "phone_name", "user_name", "OpenVpn_name"]


class IDSerializers(serializers.ModelSerializer):
    creationtime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updatetime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    Phone_name = serializers.SerializerMethodField()

    def get_Phone_name(self, obj):
        phone = PhoneInfo.objects.filter(idinfo=obj).first()
        if phone:
            return phone.phone_name
        return None

    class Meta:
        model = IdInfo
        fields = "__all__"
        # fields = ["id", "phone", "password", "creationtime", "updatetime", "Phone_name"]


class OpenVPNSerializers(serializers.ModelSerializer):
    phone_all = serializers.SerializerMethodField()
    vpn_status = serializers.SerializerMethodField()

    def get_phone_all(self, obj):
        phone_all = PhoneInfo.objects.filter(OpenVpn=obj)
        return [phone.phone_name for phone in phone_all]

    def get_vpn_status(self, obj):
        is_active = obj.status
        if is_active:
            return "open"
        return "close"

    class Meta:
        model = OpenVpn
        fields = "__all__"
        # fields = ["id", "file_name", "file_path", "phone_all", "device_count", "vpn_status", "ip_port"]


class OperationLogSerializers(serializers.ModelSerializer):
    date_time = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    zalophone = serializers.SerializerMethodField()
    screenshot_url = serializers.SerializerMethodField()
    VietnamOperation = serializers.SerializerMethodField()
    device = serializers.SerializerMethodField()

    def get_VietnamOperation(self, obj):
        vietnam = {
            "start_zalo": "Đăng nhập", "send_circle_of_friends": "Đăng tường",
            "Add_people_nearby": "Kết bạn theo vị trí", "Group_send_message": "Đăng nhóm đã được thêm vào",
            "Add_Chat_Rooms_Friend": "Phòng trò chuyện", "Add_Phone_number_friend": "Thêm số điện thoại",
            "Send_Group_Chat": "Gửi tin vào phòng trò chuyện", "Friend_Request": "Chấp nhận lời mời kết bạn",
                   }
        return vietnam[obj.operation]

    def get_device(self, obj):
        phone = PhoneInfo.objects.filter(idinfo_id=obj.zaloinfo).first()
        return phone.phone_name

    def get_date_time(self, obj):
        return time.strftime("%Y-%m-%d %X", time.localtime(float(obj.executetime)))

    def get_username(self, obj):
        user_obj = UserInfo.objects.filter(id=obj.userinfo).first()
        return user_obj.username

    def get_zalophone(self, obj):
        id_obj = IdInfo.objects.filter(id=obj.zaloinfo).first()
        if id_obj:
            return id_obj.phone
        return None

    def get_screenshot_url(self, obj):
        """获取图片地址"""
        screenshot = Screenshot.objects.filter(phone_operation_log_id=obj.id).first()
        if screenshot:
            return screenshot.photo_path
        return None

    class Meta:
        model = Phone_Operation_Log
        fields = "__all__"
