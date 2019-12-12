# -*- coding: utf-8 -*-
__author__ = 'Luke'

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from dwebsocket.decorators import accept_websocket
from rest_framework.views import APIView, Response
from zalo01.serializers import PhoneSerializers, OperationLogSerializers
from func_timeout import func_set_timeout
from Zalo.settings import redis_cache, HOST_IP
from django.db.models import F
from django.shortcuts import render, HttpResponse
from zalo01.viewss.server_views import is_superuser
from zalo01 import common, models
from Zalo import rabbitMQ
from Zalo.common import get_screenshot, get_phone_info_status
import uuid, json, time
import threading


class PhoneView(APIView):

    @method_decorator(login_required)
    def get(self, request):
        phone_all = models.PhoneInfo.objects.filter(userinfo=request.user)
        server_ip_dict = {}
        for phone in phone_all:
            if server_ip_dict.get(phone.server.id, None):
                continue
            server_ip_dict[phone.server.id] = phone.server.ip
        th_list = []
        for server_id, server_ip in server_ip_dict.items():
            satrt_th = threading.Thread(target=common.update_phone, args=(server_ip, server_id, []))
            th_list.append(satrt_th)
            satrt_th.start()
        for i in th_list:
            i.join()
        phone_all = models.PhoneInfo.objects.filter(userinfo=request.user).order_by("status").reverse()
        phone_json_list = []
        for phone_info in phone_all:
            if phone_info.idinfo:
                phone_json_list.append(
                    {"phone_id": phone_info.id, "phone_name": phone_info.phone_name,
                     "phone_status": phone_info.status, "phone_screenshot": get_screenshot(phone_info),
                     "phone_info_status": get_phone_info_status(phone_info)
                     }
                )
        # 更新聊天室
        common.update_chat_room(request)
        return render(request, "Phone/phone_index.html",
                      {
                          "nav": "phone",
                          "phone_all": phone_json_list
                      }
                      )

    @method_decorator(login_required)
    def post(self, request):
        result = {"code": 200, "msg": ""}
        instruct = request.data.get("instruct")
        phone_id_list = request.data.get("phone_list")
        if phone_id_list == "":
            result["code"] = 401
            result["msg"] = "Vui lòng chọn 1 thiết bị để tiến hành thao tác"
            return Response(result)
        dispose_content = common.DisposeContent(request, result)
        new_content, phone_obj_all = eval("dispose_content.{}()".format(instruct))
        if result["code"] != 200:
            return Response(result)
        # 根据服务器IP进行分发
        start_phone = {}
        Base_url = HOST_IP + "static/openvpn/"
        for phone in phone_obj_all:
            if not start_phone.get(phone.server.ip, None):
                start_phone[phone.server.ip] = []
            start_phone[phone.server.ip].append(
                {
                    "udid": phone.udid, "zalo_id": phone.idinfo.code + phone.idinfo.phone,
                    "device_name": phone.phone_name,
                    "zalo_pwd": phone.idinfo.password, "id": phone.id,
                    "user_id": request.user.id, "app_install": phone.app_install,
                    "open_vpn_name": phone.OpenVpn.file_name, "open_vpn_url": Base_url + phone.OpenVpn.file_name,
                    "VPN_status": phone.VPN_status, "id_id": phone.idinfo.id, "zalo_status": phone.zalo_status
                }
            )
        device_number = 0
        # 登陆验证码相关!!!!
        redis_set = "{}_code_set".format(request.user.id)
        over_set = "{}_over_set".format(request.user.id)
        user_handle_sum = "{}_handle_sum".format(request.user.id)  # 执行设备数
        accomplish = "{}_accomplish".format(request.user.id)  # 已完成
        redis_cache.delete(accomplish)
        redis_cache.delete(over_set)
        redis_cache.delete(redis_set)
        redis_cache.set(user_handle_sum, len(phone_obj_all))
        # 重写进度条，支持多任务进度条。
        task_name = "{}_{}".format(instruct, int(time.time()))
        # instruct 操作, execute_status 状态（是否开始执行 0~1）
        # progress 进度(0~100)百分比
        # device_all 设备总数, succeed_sum 执行完毕数
        # wait_time 发送进入队列时间，start_time 第一个设备执行时间， over_time 结束时间
        task_info = {
            "instruct": instruct, "execute_status": 0,
            "progress": 0, "wait_time": time.time(),
            "start_time": None, "over_time": None, "uuid": task_name,
            "devices": str([device.phone_name for device in phone_obj_all]),
            "device_all": len(phone_obj_all), "succeed_device": dict(),
        }
        redis_cache.hmset("{}_order".format(request.user.username), {task_name: json.dumps(task_info)})
        print("开始分发", instruct, start_phone, new_content)
        for ip, value in start_phone.items():
            queue_name = "{}_appium".format(ip)
            for adb in value:
                # 分发时，存入redis,执行完后更改状态,查看结果。
                key_uuid = str(uuid.uuid4())
                redis_key = "{}_{}_{}".format(request.user.id, adb["id"], time.time())
                new_content["device_number"] = device_number
                message_data = json.dumps(
                    {"instruct": instruct, "data": adb, "content": new_content, "redis_key": redis_key,
                     "user": request.user.username, "user_id": request.user.id, "task_name": task_name})
                rabbitMQ.push(queue_name, message_data, key_uuid)
                models.PhoneInfo.objects.filter(id=adb["id"]).update(is_operation=1)
                device_number += 1
        return Response(result)

    @method_decorator(login_required)
    def put(self, request):
        pass


class PhoneAlterView(APIView):

    @method_decorator(login_required)
    def get(self, request, pk):
        lo_zalo = None
        lo_vpn = None
        phone_obj = models.PhoneInfo.objects.filter(pk=pk).first()
        device_info = {"user_id": "", "zalo_id": "", "vpn_id": ""}
        if phone_obj.userinfo:
            device_info["user_id"] = str(phone_obj.userinfo.id)
        if phone_obj.idinfo:
            device_info["zalo_id"] = str(phone_obj.idinfo.id)
        if phone_obj.OpenVpn:
            device_info["vpn_id"] = str(phone_obj.OpenVpn.id)
        user_all = models.UserInfo.objects.filter(is_active=1)
        user_list = [{"username": user.username, "id": user.id} for user in user_all]
        vpn_list = [{"name": vpn.file_name, "id": vpn.id} for vpn in
                    models.OpenVpn.objects.filter(device_max__gt=F("device_count"), status=1)]
        local_vpn = models.OpenVpn.objects.filter(phoneinfo=phone_obj).first()
        if local_vpn:
            lo_vpn = {"id": local_vpn.id, "name": local_vpn.file_name}
            if lo_vpn in vpn_list:
                vpn_list.remove(lo_vpn)
        local_id = models.IdInfo.objects.filter(phoneinfo=phone_obj).first()
        zalo_list = [{"id": zalo.id, "name": zalo.name} for zalo in models.IdInfo.objects.filter(phoneinfo=None)]
        if local_id:
            lo_zalo = {"id": local_id.id, "name": local_id.name}
            if lo_zalo in zalo_list:
                zalo_list.remove(lo_zalo)
        return Response({
            "code": 200, "zalo_list": zalo_list, "user_list": user_list,
            "device": device_info, "vpn_list": vpn_list, "lo_zalo": lo_zalo,
            "lo_vpn": lo_vpn, "devicename": phone_obj.phone_name,
        })

    @method_decorator(login_required)
    def put(self, request, pk):
        # 如果更改了zalo账号以及vpn，则将状态对应改为2,下次执行app操作时会更新状态。
        phone_obj = models.PhoneInfo.objects.filter(pk=pk).first()
        if not request.user.is_superuser:
            if phone_obj.userinfo.id != request.user.id:
                return Response({"code": 403, "msg": "No Access"})
        phone_obj = models.PhoneInfo.objects.filter(pk=pk).first()
        devicename = request.data.get("devicename")
        user_id = request.data.get("user_id")
        zalo_id = request.data.get("zalo_id")
        vpn_id = request.data.get("vpn_id")
        vpn_status = request.data.get("vpn_status")
        zalo_status = request.data.get("zalo_status")
        # 设备状态,当这个状态为1表示正在运行，如果修改为0为造成错误，所以请务必确认手机是否在正常运行中。
        is_operation = request.data.get("is_operation")
        if not phone_obj:
            return Response({"code": 401, "msg": "The phone doesn't exist"})
        try:
            user_id = int(user_id)
            zalo_id = int(zalo_id)
            vpn_id = int(vpn_id)
        except:
            return Response({"code": 401, "msg": "Please enter the correct parameters"})
        if devicename:
            if phone_obj.phone_name != devicename:
                models.PhoneInfo.objects.filter(pk=pk).update(phone_name=devicename)
        if user_id:
            if not phone_obj.userinfo:
                models.PhoneInfo.objects.filter(pk=pk).update(userinfo_id=user_id)
            elif not phone_obj.userinfo.id == user_id:
                models.PhoneInfo.objects.filter(pk=pk).update(userinfo_id=user_id)
        else:
            models.PhoneInfo.objects.filter(pk=pk).update(userinfo_id=None)
        if vpn_id:
            if not phone_obj.OpenVpn:
                models.PhoneInfo.objects.filter(pk=pk).update(OpenVpn_id=vpn_id, VPN_status=0)
            elif not phone_obj.OpenVpn.id == vpn_id:
                models.PhoneInfo.objects.filter(pk=pk).update(OpenVpn_id=vpn_id, VPN_status=2)
        else:
            models.PhoneInfo.objects.filter(pk=pk).update(OpenVpn_id=None, VPN_status=0)
        if zalo_id:
            if not phone_obj.idinfo:
                models.PhoneInfo.objects.filter(pk=pk).update(idinfo_id=zalo_id, zalo_status=0)
            elif not phone_obj.idinfo.id == zalo_id:
                models.PhoneInfo.objects.filter(pk=pk).update(idinfo_id=zalo_id, zalo_status=2)
        else:
            models.PhoneInfo.objects.filter(pk=pk).update(idinfo_id=None, zalo_status=0)
        if vpn_status:
            models.PhoneInfo.objects.filter(pk=pk).update(VPN_status=vpn_status)
        if zalo_status:
            models.PhoneInfo.objects.filter(pk=pk).update(zalo_status=zalo_status)
        if is_operation:
            models.PhoneInfo.objects.filter(pk=pk).update(is_operation=is_operation)
        return Response({"code": 200, "msg": "successfully"})


@func_set_timeout(10)
def Get_message(request, _uid):
    res_data = rabbitMQ.pull(_uid)
    print("收到消息了", res_data)
    return res_data


class Get_AJAX_Room(APIView):

    def get(self, request):
        result = {"code": 400}
        room_class_index = request.GET.get("room_class_index")
        room_res = common.update_chat_room(request, room_class_index)
        if room_res:
            result["code"] = 200
            result["data"] = room_res
        else:
            result["msg"] = "更新聊天室中，请稍后重试。"
        return Response(result)


@accept_websocket
def WebSocketView(request):
    if request.is_websocket():
        print("%s 连接上了websocket" % request.user.username)
        accomplish = "{}_accomplish".format(request.user.id)
        _uid = "{}_mq_code".format(request.user.id)
        redis_set = "{}_code_set".format(request.user.id)
        over_set = "{}_over_set".format(request.user.id)
        short = "{}_short".format(request.user.id)
        user_handle_sum = "{}_handle_sum".format(request.user.id)
        while True:
            try:
                time.sleep(5)
                msg = request.websocket.read()
                if msg:
                    if msg.decode("utf8") == "quit":
                        request.websocket.close()
                        return
                res_data = {}
                redis_cache.sdiffstore(short, redis_set, over_set)
                phone_number = redis_cache.spop(short)
                if phone_number:
                    phone_number = phone_number.decode("utf8")
                    res_data["phone_number"] = phone_number
                    redis_cache.sadd(over_set, phone_number)
                res_data["progress_bar"] = len(redis_cache.sinter(accomplish)) / int(
                    redis_cache.get(user_handle_sum).decode("utf8")) * 100
                request.websocket.send(json.dumps(res_data).encode('utf-8'))
                if res_data["progress_bar"] == 100:
                    request.websocket.close()
                    return
            except BaseException as b:
                return


@accept_websocket
def Progress_bar(request):
    if request.is_websocket():
        while True:
            try:
                _user_key = "{}_order".format(request.user.username)
                result = {"record_list": []}
                for x in redis_cache.hkeys(_user_key):
                    dict_info = json.loads(redis_cache.hmget(_user_key, x.decode("utf8"))[0].decode("utf8"))
                    if not dict_info["over_time"]:
                        print(dict_info)
                        dict_info["progress"] = round(len(dict_info["succeed_device"]) / dict_info["device_all"] * 100,
                                                      2)
                        if dict_info["device_all"] <= len(dict_info["succeed_device"]):
                            dict_info["over_time"] = time.time()
                            redis_cache.hmset(_user_key, {x.decode("utf8"): json.dumps(dict_info)})
                        result["record_list"].append(dict_info)
                request.websocket.send(json.dumps(result).encode('utf-8'))
                msg = request.websocket.read()
                if msg:
                    msg_info = msg.decode("utf8")
                    if msg_info == "quit":
                        request.websocket.close()
                        return
                    # else:
                    #     redis_cache.hdel(_user_key, msg_info)
                time.sleep(5)
            except BaseException as b:
                print(b)
                return


class Code(APIView):

    def post(self, request):
        phone_number = request.data.get("phone_number")
        code = request.data.get("code")
        print(code)
        if len(code) != 4:
            return Response({"code": 401, "msg": "Verification code error"})
        result_json = json.dumps({"phone_number": phone_number, "code": code})
        redis_cache.set(phone_number, result_json)
        redis_cache.expire(phone_number, 120)
        return Response({"code": 200, "msg": "Received your captcha"})
