# -*- coding: utf-8 -*-
__author__ = 'Luke'

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from django.db import close_old_connections
from Zalo.settings import redis_cache, HOST_IP
from django.db.models import Q
from django.db.models import F
from zalo01 import models
from Zalo import rabbitMQ, settings
from Zalo.common import read_excel
import hashlib, time, os
import zipfile
import json
import uuid


def update_chat_room(request, room_class_index=None):
    """ 更新聊天室 """
    room_dict = redis_cache.get("chat_rooms_name")
    if room_dict:
        room_dict = json.loads(room_dict)
    if room_dict:
        if room_class_index:
            return room_dict[room_class_index]
    else:
        update_room = redis_cache.get("update_room")
        if update_room:
            update_room = update_room.decode("utf8")
        else:
            redis_cache.set("update_room", 0)
            update_room = update_room.decode("utf8")
        if not int(update_room):
            phone = models.PhoneInfo.objects.filter(status=2, zalo_status=1, VPN_status=1, app_install=1).first()
            if phone:
                message_data = json.dumps(
                    {
                        "instruct": "Get_Chat_Rooms_name", "data":
                        {
                            "udid": phone.udid, "device_name": phone.phone_name,
                            "id_id": phone.idinfo.phone, "id": phone.id
                        },
                        "content": {}, "redis_key": {},
                        "user": request.user.username, "user_id": request.user.id})
                queue_name = "{}_appium".format(phone.server.ip)
                rabbitMQ.push(queue_name, message_data, "")
                models.PhoneInfo.objects.filter(id=phone.id).update(is_operation=1)
                redis_cache.set("update_room", 1)


def Page_dispose(request, obj_count):
    """ 页码处理 """
    result = {"code": 200}
    base_url = request.get_full_path()
    url_list = base_url.split("?")
    if len(url_list) > 2:
        url_list = url_list[1].split("&")
        result["base_url"] = ""
        for url in map(lambda url: None if "page" in url or "size" in url else url, url_list):
            if url:
                result["base_url"] += url + "&"
        print(result["base_url"])
    page = request.GET.get("page", 1)
    size = request.GET.get("size", 15)
    try:
        page = int(page)
        size = int(size)
    except:
        result["code"] = 402
        # result["msg"] = "页码或每页显示数不正确，请正确输入正整数。"
        result["msg"] = "Số trang hoặc mỗi trang hiển tị không chính xác, vui lòng nhập số chính xác đầy đủ"
        return result
    d_sum = divmod(obj_count, size)
    remainder = 0
    if d_sum[1] > 0:
        remainder = 1
    _sum_page = d_sum[0] + remainder
    result["up_page"] = page - 1
    result["down_page"] = page + 1
    if page < 0:
        page = 0
        result["up_page"] = None
    if page >= _sum_page:
        page = _sum_page - 1
    if page >= _sum_page - 1:
        result["down_page"] = None
    if page < 4:
        _end = _sum_page + 1
        if _sum_page > 7:
            _end = 8
        result["page_range"] = range(1, _end)
    elif page >= _sum_page - 3:
        result["page_range"] = range(page - 3, _sum_page)
    else:
        result["page_range"] = range(page - 3, page + 4)
    result["now_page"] = page
    result["start_page"] = (page - 1) * size
    result["end_page"] = page * size
    if obj_count < size:
        result["start_page"] = 0
        result["end_page"] = obj_count
    result["size"] = size
    return result


def get_vpn_ip(file_name):
    file_path = os.path.join(settings.BASE_VPN, file_name)
    vpn_dict = {"vpn_name": file_name, "file_url": "/static/openvpn/{}".format(file_name)}
    with open(file_path, 'r', encoding="utf8") as f:
        for i in f.readlines():
            if "remote" in i:
                li = i.strip("\n").split(" ")
                vpn_dict["ip"] = li[1] + ":" + li[2]
                return vpn_dict


def uncompress_zipfile(content, zip_vpn_name):
    """ 解压 vpn文件"""
    file_path = os.path.join(settings.BASE_VPN, zip_vpn_name)
    with open(file_path, "wb") as f:
        for chunk in content.chunks():
            f.write(chunk)
    zp = zipfile.ZipFile(file_path, 'r')
    zp.extractall(settings.BASE_VPN)
    zp.close()
    os.remove(file_path)
    return os.listdir(settings.BASE_VPN)


def get_random(user):
    time_str = str(time.time())
    md5 = hashlib.md5(bytes(user, encoding="utf8"))
    md5.update(bytes(time_str, encoding="utf8"))
    return md5.hexdigest()


def update_phone(server_ip, pk, create_error):
    # MQ推送消息
    queue_name = "{}_adb".format(server_ip)
    key_uuid = str(uuid.uuid4())
    message_data = json.dumps({"instruct": "Look_devices", "content": {}, "queue_name": key_uuid})
    rabbitMQ.push(queue_name, message_data, key_uuid)
    # MQ消费消息
    result = rabbitMQ.pull(key_uuid)
    if result["code"] != 200:
        return result
    status_dict = {"device": 2, "off": 0}
    close_old_connections()
    udid_list = []
    server_obj = models.Server.objects.filter(id=pk).first()
    for udid, status in result["data"].items():
        udid_list.append(udid)
        status = status_dict.get(status, 1)
        phone_obj = models.PhoneInfo.objects.filter(server_id=pk, udid=udid)
        if not phone_obj:
            zalo_id = models.IdInfo.objects.filter(phoneinfo=None).first()
            vpn = models.OpenVpn.objects.filter(device_max__gt=F("device_count")).first()
            if zalo_id and vpn:
                new_phone = models.PhoneInfo.objects.create(server_id=pk, udid=udid,
                                                            status=status, idinfo=zalo_id,
                                                            OpenVpn=vpn)
                device_name = str(server_obj.series) + str(new_phone.id)
                models.PhoneInfo.objects.filter(id=new_phone.id).update(phone_name=device_name)
                models.OpenVpn.objects.filter(id=vpn.id).update(device_count=F("device_count") + 1)
            else:
                create_error.append({"udid": udid, "status": status})
        else:
            models.PhoneInfo.objects.filter(server_id=pk, udid=udid).update(status=status)
    models.PhoneInfo.objects.exclude(udid__in=udid_list).update(status=0)
    return result


def class_status(result):
    device_list = []
    offline_list = []
    close_list = []
    for port, status in result["data"].items():
        # 0 已关闭， 1 已开启， 2 已开启，无法使用
        # if status == ""
        if status["status"] == "device":
            device_list.append((port, status["udid"]))
        elif status["status"] == "offline":
            offline_list.append(port)
        else:
            close_list.append(port)
    return device_list, offline_list, close_list


def save_file(content, result=None, file=False, file_base="user_file"):
    """
    file 为 True 返回文件路径,否则返回url
    file_base 保存文件的路径
    """
    if not content:
        if result:
            result["code"] = 403
            result["msg"] = "Vui lòng nhập đúng loại tham số"
        return
    key_uuid = str(uuid.uuid4())
    md5 = hashlib.md5()
    base_path = os.path.join(settings.BASE_DIR, "static", file_base)
    file_path = os.path.join(base_path, "%s.%s" % (key_uuid, str(content).split(".")[-1]))
    with open(file_path, "wb") as f:
        for chunk in content.chunks():
            md5.update(chunk)
            f.write(chunk)
    file_md5 = md5.hexdigest()
    new_file = os.path.join(base_path, "%s.%s" % (file_md5, str(content).split(".")[-1]))
    if not os.path.isfile(new_file):
        os.rename(file_path, new_file)
    else:
        os.remove(file_path)
    path = os.path.join("static", file_base, "%s.%s" % (file_md5, str(content).split(".")[-1]))
    if file:
        return os.path.join(settings.BASE_DIR, path)
    url = settings.HOST_IP + path
    return url.replace("\\", "/")


def DisposeExcel(filepath):
    file_url_path = os.path.join("static", "user_file", "%s.txt" % filepath.split("\\")[-1].split(".")[0])
    file_path = os.path.join(settings.BASE_DIR, file_url_path)
    with open(file_path, "w", encoding="utf8") as f:
        for i in read_excel(filepath):
            f.write("{} | {}\n".format(i[0], int(i[1])))
    url = settings.HOST_IP + file_url_path
    return url.replace("\\", "/")


class SuperAdmin(BasePermission):
    message = "Super admin to view skip: http://192.168.1.196:8000/index"

    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True
        return False


class TokenAuth(BaseAuthentication):
    def authenticate(self, request):
        # 获取用户传来的token参数
        token = request.GET.get("token", None)
        token_obj = models.UserInfo.objects.filter(token=token).first()
        if token_obj:
            # 返回用户对象跟token_obj
            return token_obj.user, token_obj.token
        else:
            raise AuthenticationFailed("认证失败")


class DisposeContent:
    """
    数据处理，设备筛选，结果返回。
    """

    def __init__(self, request, result):
        self.new_content = {}
        self.request = request
        self.result = result

    def if_value_null(self):
        """判断值是否为空"""
        for _key, _value in self.request.data.items():
            if _value == "":
                self.result["code"] = 403
                self.result["msg"] = "Please fill in the required parameters"
                return

    def save_photo(self, photo_list):
        """ 保存图片"""
        photo_url_list = []
        for photo in photo_list:
            try:
                int(photo)
            except:
                continue
            file = self.request.FILES.get(photo)
            file_url = save_file(file)
            photo_url_list.append(file_url)
        return photo_url_list

    def get_service(self, zalo_status):
        phone_id_list = self.request.data.get("phone_list")
        phone_id_list = phone_id_list.strip().split(",")
        if zalo_status:
            phone_obj_all = models.PhoneInfo.objects.filter(
                id__in=phone_id_list, userinfo=self.request.user, zalo_status=zalo_status,
                VPN_status=zalo_status, is_operation=0, status=2,
            )
        else:
            phone_obj_all = models.PhoneInfo.objects.filter(
                Q(zalo_status__in=[0, 2]) | Q(VPN_status__in=[0, 2]),
                id__in=phone_id_list, userinfo=self.request.user, is_operation=0, status=2
            )
        if not phone_obj_all:
            self.result["code"] = 401
            # self.result["msg"] = "请至少选择一台已启动并登录的设备."
            self.result["msg"] = "Vui lòng chọn ít nhất một thiết bị đã được bắt đầu và đăng nhập."
        if not zalo_status:
            # self.result["msg"] = "请至少选择一台已启动未登录的设备."
            self.result["msg"] = "Vui lòng chọn ít nhất một thiết bị đã được bắt đầu và chưa đăng nhập."
        return phone_obj_all

    def start_zalo(self):
        """ 登陆zalo """
        phone_obj_all = self.get_service(0)
        if self.result["code"] == 200:
            self.result["msg"] = "Bắt đầu đăng nhập số lượng lớn({})".format(
                str([phone.phone_name for phone in phone_obj_all]))
        return self.new_content, phone_obj_all

    def send_circle_of_friends(self):
        """ 朋友圈内容处理 """
        self.if_value_null()
        photo_list = self.request.data.get("photo_list")
        text_content = self.request.FILES.get("text_content")
        longitude = self.request.data.get("longitude")
        latitude = self.request.data.get("latitude")
        self.new_content["longitude"] = longitude
        self.new_content["latitude"] = latitude
        text_content_url = save_file(text_content, self.result)
        phone_obj_all = self.get_service(1)
        photo_url_list = self.save_photo(photo_list)
        self.new_content["photo_url_list"] = photo_url_list
        self.new_content["text_content_url"] = text_content_url
        if self.result["code"] == 200:
            self.result["msg"] = "Bắt đầu gửi tin số lượng lớn({})".format(
                str([phone.phone_name for phone in phone_obj_all]))
        return self.new_content, phone_obj_all

    def Group_send_message(self):
        """ 群发已加好友内容处理 """
        self.if_value_null()
        text_content = self.request.FILES.get("text_content")
        time_out = self.request.data.get("time_out")
        try:
            time_out = int(time_out)
        except:
            self.result["code"] = 402
            self.result["msg"] = "Vui lòng nhập đúng loại tham số"
            return None, None
        photo_list = self.request.data.get("photo_list")
        photo_url_list = self.save_photo(photo_list)
        self.new_content["photo_url_list"] = photo_url_list
        text_content_url = save_file(text_content, self.result)
        self.new_content["text_content_url"] = text_content_url
        self.new_content["time_out"] = time_out
        phone_obj_all = self.get_service(1)
        if self.result["code"] == 200:
            self.result["msg"] = "Bắt đầu gửi hàng loạt bạn bè đã kết bạn({})".format(
                str([phone.phone_name for phone in phone_obj_all]))
        return self.new_content, phone_obj_all

    def Add_people_nearby(self):
        """ 添加附近人 """
        self.if_value_null()
        longitude = self.request.data.get("longitude")
        latitude = self.request.data.get("latitude")
        add_sleep = self.request.data.get("add_sleep")
        call_content = self.request.FILES.get("add_file")
        send_count = self.request.data.get("send_count")
        add_count = self.request.data.get("add_count")
        photo_list = self.request.data.get("photo_list")
        photo_url_list = self.save_photo(photo_list)
        self.new_content["photo_url_list"] = photo_url_list
        sex = self.request.data.get("sex")
        self.new_content["longitude"] = longitude
        self.new_content["latitude"] = latitude
        print(longitude, latitude)
        time.sleep(120000)

        try:
            send_count = int(send_count)
            add_sleep = int(add_sleep)
            add_count = int(add_count)
        except:
            self.result["code"] = 402
            self.result["msg"] = "Vui lòng nhập đúng loại tham số"
            return None, None
        if send_count > 20 or add_count > 30:
            self.result["code"] = 402
            self.result["msg"] = " Thêm / gửi số lượng không thể lớn hơn ngưỡng đặt ra"
            return None, None
        call_url = save_file(call_content, self.result)
        self.new_content["add_sleep"] = add_sleep
        self.new_content["send_count"] = send_count
        self.new_content["add_count"] = add_count
        self.new_content["sex"] = sex
        self.new_content["call_url"] = call_url
        phone_obj_all = self.get_service(1)
        if self.result["code"] == 200:
            self.result["msg"] = "Bắt đầu thêm những người xung quanh({})".format(
                str([phone.phone_name for phone in phone_obj_all]))
        return self.new_content, phone_obj_all

    def Add_Chat_Rooms_Friend(self):
        """ 聊天室处理 """
        self.if_value_null()
        room_index = self.request.data.get("room_index")
        room_name = self.request.data.get("room_name")
        room_sleep = self.request.data.get("room_sleep")
        # 每个设备添加多少个好友,发送多少好友
        room_send_count = self.request.data.get("room_send_count")
        room_add_count = self.request.data.get("room_add_count")
        call_file = self.request.FILES.get("call_file")
        photo_list = self.request.data.get("photo_list")
        photo_url_list = self.save_photo(photo_list)
        call_url = save_file(call_file, self.result)
        try:
            room_sleep = int(room_sleep)
            room_send_count = int(room_send_count)
            room_add_count = int(room_add_count)
        except:
            self.result["code"] = 402
            self.result["msg"] = "Vui lòng nhập đúng loại tham số"
            return None, None
        room_name = room_name.split("(")[0].strip()
        phone_obj_all = self.get_service(1)
        self.new_content["room_sleep"] = room_sleep
        self.new_content["room_index"] = room_index
        self.new_content["room_name"] = room_name
        self.new_content["room_send_count"] = room_send_count
        self.new_content["room_add_count"] = room_add_count
        self.new_content["call_file_url"] = call_url
        self.new_content["photo_url_list"] = photo_url_list
        if self.result["code"] == 200:
            self.result["msg"] = " Bắt đầu vào phòng trò chuyện để thêm / gửi tin nhắn({})".format(
                str([phone.phone_name for phone in phone_obj_all]))
        return self.new_content, phone_obj_all

    def Add_Phone_number_friend(self):
        """ 根据电话号码加好友 """
        self.if_value_null()
        # 每个设备添加多少个好友,发送多少好友
        add_phone_number_file = self.request.FILES.get("add_phone_number_file")
        add_phone_number_call = self.request.FILES.get("add_phone_number_call")
        phonenumberoperate = self.request.data.get("phonenumberoperate")
        phonenumber_count = self.request.data.get("phonenumber_count")
        try:
            phonenumberoperate = int(phonenumberoperate)
            phonenumber_count = int(phonenumber_count)
        except:
            self.result["code"] = 402
            self.result["msg"] = "Vui lòng nhập đúng loại tham số"
            return None, None
        if phonenumberoperate:
            photo_list = self.request.data.get("photo_list")
            photo_url_list = self.save_photo(photo_list)
            self.new_content["photo_url_list"] = photo_url_list
        phone_obj_all = self.get_service(1)
        AddPhoneNumberPath = save_file(add_phone_number_file, self.result, True)
        add_phone_number_file_url = DisposeExcel(AddPhoneNumberPath)
        call_url = save_file(add_phone_number_call, self.result)
        self.new_content["call_url"] = call_url
        self.new_content["add_phone_number_url"] = add_phone_number_file_url
        self.new_content["phonenumberoperate"] = phonenumberoperate
        self.new_content["phonenumber_count"] = phonenumber_count
        if self.result["code"] == 200:
            self.result["msg"] = "Bắt đầu thêm / gửi số lượng lớn bằng SĐT({})".format(
                str([phone.phone_name for phone in phone_obj_all]))
        return self.new_content, phone_obj_all

    def Send_Group_Chat(self):
        """ 进入聊天室发消息，每次用以一个"""
        group_room_text_content = self.request.FILES.get("group_room_text_content")
        group_room_sleep = self.request.data.get("group_room_sleep", 0)
        group_room_index = self.request.data.get("group_room_index")
        try:
            group_room_index = int(group_room_index)
            group_room_sleep = int(group_room_sleep)
        except:
            self.result["code"] = 402
            self.result["msg"] = "Vui lòng nhập đúng loại tham số"
            return None, None
        phone_obj_all = self.get_service(1)
        group_room_text_content_file_url = save_file(group_room_text_content, self.result)
        self.new_content["group_room_text_content_file_url"] = group_room_text_content_file_url
        self.new_content["group_room_sleep"] = group_room_sleep
        self.new_content["group_room_index"] = group_room_index
        if self.result["code"] == 200:
            self.result["msg"] = "Bắt đầu gửi tin và tiến hành vào trong danh mục phân loại PTC({})".format(
                str([phone.phone_name for phone in phone_obj_all]))
        return self.new_content, phone_obj_all

    def Friend_Request(self):
        """通过好友请求"""
        phone_obj_all = self.get_service(1)
        if self.result["code"] == 200:
            self.result["msg"] = "Bắt đầu thông qua lời mời kết bạn({})".format(
                str([phone.phone_name for phone in phone_obj_all]))
        return self.new_content, phone_obj_all
