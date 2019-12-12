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
import os


class ZaloIdView(APIView):

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def get(self, request):
        phonenumber = request.GET.get("phonenumber")
        if phonenumber:
            id_info_all = models.IdInfo.objects.filter(phone=phonenumber).order_by("updatetime").reverse()
        else:
            id_info_all = models.IdInfo.objects.all().order_by("updatetime").reverse()
        result = common.Page_dispose(request, id_info_all.count())
        if result["code"] != 200:
            return Response(result)
        id_info_result = IDSerializers(
            id_info_all[result["start_page"]:result["end_page"]], many=True
        )
        return render(request, "Zalo/zalo_list.html", {
            "id_info_all": id_info_result.data, "nav": "zaloid",
            "page_obj": result,
        })

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def post(self, request):
        phone = request.data.get("phone")
        password = request.data.get("password")
        zalo_name = request.data.get("zalo_name")
        zalo_code = request.data.get("zalo_code")
        excel_file = request.FILES.get("excel_file", None)
        result = {"code": 200}
        if excel_file:
            file_url = common.save_file(excel_file)
            file_path = os.path.join(BASE_DIR, "static", "user_file", file_url.split("/")[-1])
            query_set_list = []
            for in_info in read_excel(file_path):
                if models.IdInfo.objects.filter(phone=int(in_info[1])) or models.IdInfo.objects.filter(name=in_info[3]):
                    continue
                query_set_list.append(
                    models.IdInfo(
                        code=int(in_info[0]), phone=int(in_info[1]),
                        password=in_info[2], name=in_info[3]
                    )
                )
            models.IdInfo.objects.bulk_create(query_set_list)
            result["msg"] = "批量添加成功({})".format(len(query_set_list))
        else:
            zalo_obj = models.IdInfo.objects.filter(phone=phone)
            if zalo_obj:
                return Response({"code": 400, "msg": "This cell phone number already exists"})
            if not phone or not password or not zalo_name:
                return Response({"code": 400, "msg": "All fields are required"})
            models.IdInfo.objects.create(
                phone=phone, password=password, name=zalo_name, code=zalo_code
            )
            result["msg"] = "添加成功"
        return Response(result)


class ZaloIdAlterView(APIView):

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def get(self, request, pk):
        result = {"code": 200, "msg": ""}
        zaloinfo = models.IdInfo.objects.filter(pk=pk).first()
        if zaloinfo:
            result["data"] = {
                "id": zaloinfo.id, "code": zaloinfo.code, "name": zaloinfo.name,
                "phone": zaloinfo.phone, "password": zaloinfo.password
            }
        else:
            result["code"] = 403
            result["msg"] = "该条数据不存在"
        return Response(result)

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def put(self, request, pk):
        result = {"code": 200, "msg": ""}
        code = request.data.get("code")
        name = request.data.get("name")
        phone = request.data.get("phone")
        password = request.data.get("password")
        if code and name and phone and password:
            models.IdInfo.objects.filter(pk=pk).update(
                code=code, name=name, phone=phone, password=password
            )
            result["msg"] = "更改zalo账号信息成功"
        else:
            result["code"] = 403
            result["msg"] = "请输入正确的参数"
        return Response(result)

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def delete(self, request, pk):
        # 如果zalo删除时有绑定设备，
        result = {"code": True, "msg": ""}
        phoneinfo = models.PhoneInfo.objects.filter(idinfo_id=pk).first()
        if phoneinfo:
            result["code"] = False
            result["msg"] = "zalo账号已绑定({}),如需删除必须先解除绑定".format(phoneinfo.phone_name)
        else:
            try:
                models.IdInfo.objects.filter(pk=pk).delete()
                result["msg"] = "删除zalo账号成功!"
            except BaseException as b:
                result["code"] = False
                result["msg"] = str(b)
        return Response(result)
