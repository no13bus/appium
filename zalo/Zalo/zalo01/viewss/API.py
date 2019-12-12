# -*- coding: utf-8 -*-
__author__ = 'Luke'

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from zalo01.viewss.server_views import is_superuser
from rest_framework.views import APIView, Response
from django.shortcuts import render, redirect
from zalo01.serializers import IDSerializers
from zalo01 import models, common
from Zalo.common import read_excel
from Zalo.settings import *
import time
import json
import re


class ScreenShotAPIView(APIView):

    def post(self, request):
        """ 上传截图"""
        result = {}
        picture = request.FILES.get("picture")
        phone_id = request.data.get("phone_id")
        phone_operation_log_id = request.data.get("phone_operation_log_id")
        phone_obj = models.PhoneInfo.objects.filter(id=phone_id)
        Phone_Operation_Log_obj = models.Phone_Operation_Log.objects.filter(id=phone_operation_log_id)
        if picture and phone_obj and Phone_Operation_Log_obj:
            picture_path = common.save_file(picture, None, True, "screenshot")
            picture_path = re.search(r"static.*", picture_path).group()
            picture_path = "\\\\" + picture_path.replace("\\", "\\\\")
            s_obj = models.Screenshot.objects.filter(photo_path=picture_path).first()
            if s_obj:
                result["code"] = 403
                result["msg"] = "已经存在该条图片记录"
            else:
                screenshot = models.Screenshot.objects.create(
                    photo_path=picture_path, phone_id=phone_id,
                    phone_operation_log_id=phone_operation_log_id
                )
                result["code"] = 200
                result["msg"] = "插入记录成功"
                result["data"] = {"id": screenshot.id}
        else:
            result["code"] = 403
            result["msg"] = "请提供正确的参数"
        return Response(result)


class PhoneAPIView(APIView):


    def put(self, request):
        """ 更改设备状态 """
        udid = request.data.get("udid")
        Param = json.loads(request.data.get("Param"))
        phone_obj = models.PhoneInfo.objects.filter(udid=udid)
        if phone_obj:
            phone_obj.update(**Param)
        return Response({"code": 200, "msg": ""})


class OperationAPIView(APIView):

    def post(self, request):
        """ 添加操作记录"""
        Param = json.loads(request.data.get("Param"))
        Operation_obj = models.Phone_Operation_Log.objects.create(**Param)
        return Response({"code": 200, "msg": "", "data": Operation_obj.id})


class RedisAPIView(APIView):

    def get(self, request):
        """ 查询"""
        pass

    def post(self, request):
        """ 添加"""
        method = request.data.get("method")
        RedisKey = request.data.get("RedisKey")
        value = request.data.get("value")
        ex = request.data.get("ex")
        if method == "hmset":
            eval("redis_cache.{}(RedisKey, value)".format(method))
        if ex:
            eval("redis_cache.{}(RedisKey, value, ex=ex)".format(method))
        else:
            eval("redis_cache.{}(RedisKey, value)".format(method))



    def put(self, request):
        """ 修改"""
        pass


class ProgressBarView(APIView):

    def delete(self, request):
        """ 清空所有进度条 """
        order = "{}_order".format(request.user.username)
        redis_cache.delete(order)
        return Response({})
