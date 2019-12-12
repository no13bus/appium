# -*- coding: utf-8 -*-
__author__ = 'Luke'

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.views import APIView, Response
from django.shortcuts import render, redirect
from django.db import close_old_connections
from zalo01.serializers import *
from Zalo import rabbitMQ
from zalo01 import models
from zalo01 import common


def is_superuser(func):
    def newfunc(*args, **kwargs):
        request = args[0]
        if not request.user.is_superuser:
            # return render(request, "user/login.html")
            return Response({"code": 400, "msg": "不是超级管理员"})
        res = func(*args, **kwargs)
        return res

    return newfunc


class ServerView(APIView):

    @method_decorator(login_required)
    def get(self, request):
        server_all = models.Server.objects.all()
        server_result = ServerSerializers(server_all, many=True)
        return render(request, "Server/server_index.html", {
            "server_all": server_result.data, "nav": "server",
            "server_ip": "Choice Server",
        })

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def post(self, request):
        server_ip = request.data.get("server_ip")
        series = request.data.get("series")
        result = {"code": 200, "msg": "Server added successfully, Please start the corresponding service on the server"}
        if len(server_ip.split(".")) != 4:
            result["code"] = 401
            result["msg"] = "Please fill in the server IP correctly"
            return Response(result)
        sever = models.Server.objects.filter(ip=server_ip).first()
        if sever:
            # 统一错误页面
            result["code"] = 401
            result["msg"] = "Server already exists"
            return Response(result)
        try:
            models.Server.objects.create(ip=server_ip, series=series)
        except BaseException as b:
            result["msg"] = str(b)
            result["code"] = 500
        return Response(result)



class ServerAlterView(APIView):

    @method_decorator(login_required)
    def get(self, request, pk):
        server_obj = models.Server.objects.filter(id=pk).first()
        if not server_obj:
            return Response({"code": 400, "msg": "服务器不存在"})
        create_error = []
        result = common.update_phone(server_obj.ip, pk, create_error)
        if result["code"] != 200:
            return Response(result)
        if request.user.is_superuser:
            phone_all_obj = models.PhoneInfo.objects.filter(server_id=pk)
        else:
            phone_all_obj = models.PhoneInfo.objects.filter(server_id=pk, userinfo_id=request.user.id)
        server_all = models.Server.objects.all()
        result = common.Page_dispose(request, phone_all_obj.count())
        phone_result = PhoneSerializers(phone_all_obj[result["start_page"]:result["end_page"]], many=True)
        server_result = ServerSerializers(server_all, many=True)
        return render(request, "Server/server_index.html",
                      {
                          "server_all": server_result.data, "nav": "server",
                          "server_pk": int(pk), "phone_all": phone_result.data,
                          "error_len": len(create_error), "server_ip": server_obj.ip,
                          "page_obj": result
                      })

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def delete(self, request, pk):
        models.PhoneInfo.objects.filter(id=pk).delete()
        return Response({"code": 200, "msg": "successfully delete"})