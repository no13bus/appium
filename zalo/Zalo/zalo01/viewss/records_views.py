# -*- coding: utf-8 -*-
__author__ = 'Luke'

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.views import APIView, Response
from zalo01.serializers import OperationLogSerializers, UserSerializers
from Zalo.settings import redis_cache, HOST_IP
from zalo01.viewss.server_views import is_superuser
from django.shortcuts import render
from zalo01 import models
from zalo01 import common
from Zalo import rabbitMQ
import uuid, json, time


class RecordsView(APIView):

    @method_decorator(login_required)
    def get(self, request):
        """ 获取所有的结果 """
        if request.user.is_superuser:
            zalo_id = request.GET.get("zalo_id")
            user_id = request.GET.get("user_id")
            phonenumber = request.GET.get("phonenumber")
            if phonenumber:
                zaloinfo = models.IdInfo.objects.filter(phone=phonenumber).first()
                if zaloinfo:
                    records_all = models.Phone_Operation_Log.objects.filter(zaloinfo=zaloinfo.id).order_by("executetime").reverse()
                else:
                    records_all = models.Phone_Operation_Log.objects.filter(zaloinfo=0).order_by("executetime").reverse()
            else:
                if zalo_id:
                    records_all = models.Phone_Operation_Log.objects.filter(zaloinfo=zalo_id).order_by("executetime").reverse()
                elif user_id:
                    records_all = models.Phone_Operation_Log.objects.filter(userinfo=user_id).order_by("executetime").reverse()
                else:
                    records_all = models.Phone_Operation_Log.objects.all().order_by("executetime").reverse()

        else:
            records_all = models.Phone_Operation_Log.objects.filter(userinfo=request.user.id).order_by("executetime").reverse()
        result = common.Page_dispose(request, records_all.count())
        records_result = OperationLogSerializers(records_all[result["start_page"]:result["end_page"]], many=True)
        user_all = [{"id": user.id, "username": user.username} for user in models.UserInfo.objects.all()]
        zalo_all = [{"id": id.id, "phone": id.phone} for id in models.IdInfo.objects.all()]
        return render(request, "records/records_index.html", {
            "records_all": records_result.data, "nav": "records", "page_obj": result,
            "user_all": user_all, "zalo_all": zalo_all, "is_superuser": True,
        })


class RecordsAlterView(APIView):

    @method_decorator(login_required)
    def delete(self, request, pk):
        """ 获取所有的结果 """
        result = {"code": 200, "msg": "successfully delete"}
        obj = models.Phone_Operation_Log.objects.filter(id=pk, userinfo=request.user.id)
        if request.user.is_superuser:
            models.Phone_Operation_Log.objects.filter(id=pk).delete()
        elif obj:
            obj.delete()
        else:
            result["code"] = 400
            result["msg"] = "Sorry, you are not authorized"
        return Response(result)