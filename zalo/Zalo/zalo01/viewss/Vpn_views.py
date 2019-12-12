# -*- coding: utf-8 -*-
__author__ = 'Luke'

from django.contrib.auth.decorators import login_required
from zalo01.viewss.server_views import is_superuser
from django.utils.decorators import method_decorator
from rest_framework.views import APIView, Response
from zalo01.serializers import OpenVPNSerializers
from django.db.models import F
from django.shortcuts import render
from zalo01 import models
from zalo01 import common
import zipfile


class VpnView(APIView):

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def get(self, request):
        vpnname = request.GET.get("vpnname")
        if vpnname:
            open_vpn_all = models.OpenVpn.objects.filter(file_name__icontains=vpnname)
        else:
            open_vpn_all = models.OpenVpn.objects.all()
        result = common.Page_dispose(request, open_vpn_all.count())
        openvpn_result = OpenVPNSerializers(open_vpn_all[result["start_page"]:result["end_page"]], many=True)
        return render(request, "VPN/vpnindex.html", {
            "openvpn_all": openvpn_result.data, "nav": "openvpn", "page_obj": result
        })

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def post(self, request):
        result = {"code": 401, "msg": ""}
        open_zip = request.FILES.get("zipfile")
        device_max = request.data.get("device_count", 5)
        if str(open_zip).split(".")[-1] != "zip":
            result["msg"] = "Only the zip format is supported"
            return Response(result)
        zip_vpn_name = str(open_zip).split("\\")[-1]
        _count = 0
        for vpn in map(common.get_vpn_ip, common.uncompress_zipfile(open_zip, zip_vpn_name)):
            vpn_obj = models.OpenVpn.objects.filter(file_name=vpn["vpn_name"])
            if vpn_obj:
                continue
            models.OpenVpn.objects.create(
                file_name=vpn["vpn_name"], file_path=vpn["file_url"],
                ip_port=vpn["ip"], device_max=device_max
            )
            _count += 1
        result["msg"] = "upload successful({})".format(_count)
        result["code"] = 200
        return Response(result)


class VpnAlterView(APIView):

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def get(self, request, pk):
        open_vpn = models.OpenVpn.objects.filter(id=pk).first()
        phone_list = models.PhoneInfo.objects.filter(OpenVpn=open_vpn)
        result = {"code": 200,
                  "device_list": [{"device_name": phone.phone_name, "device_id": phone.id} for phone in phone_list]
                  }
        return Response(result)

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def put(self, request, pk):
        result = {"code": 401, "msg": ""}
        vpn_status = request.data.get("is_status")
        connect_max = request.data.get("connect_max")
        devices = request.data.get("devices")
        if devices:
            device_list = devices.split(",")
        else:
            device_list = []
        open_vpn = models.OpenVpn.objects.filter(id=pk).first()
        phone_list = models.PhoneInfo.objects.filter(OpenVpn=open_vpn, id__in=device_list)
        try:
            vpn_status = int(vpn_status)
            if not vpn_status:
                connect_max = 0
            connect_max = int(connect_max)
        except:
            result["msg"] = "Please enter the correct parameters"
            return Response(result)
        # 判断当前vpn是否禁用, 一旦禁用则删除该VPN下的所有设备，
        if not vpn_status:
            models.PhoneInfo.objects.filter(OpenVpn=open_vpn).update(OpenVpn=None, VPN_status=0)
            models.OpenVpn.objects.filter(id=pk).update(device_count=0)
        else:
            # 更改当前解除绑定的vpn
            models.PhoneInfo.objects.filter(OpenVpn=open_vpn). \
                exclude(id__in=device_list).update(OpenVpn=None, VPN_status=0)
            models.OpenVpn.objects.filter(id=pk).update(device_count=F("device_count") - len(device_list))
            # 判断是否设置最大值，如果最大值小于当前绑定数，则更改最大值为当前绑定数
            if connect_max < phone_list.count():
                connect_max = phone_list.count()
        models.OpenVpn.objects.filter(id=pk).update(device_max=connect_max, status=vpn_status)
        result["code"] = 200
        result["msg"] = "update successfully."
        return Response(result)

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def delete(self, request, pk):
        models.OpenVpn.objects.filter(id=pk).delete()
        return Response({"code": 200, "msg": "successfully delete"})
