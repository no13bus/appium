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


class HelpView(APIView):

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



