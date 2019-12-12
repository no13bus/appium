# -*- coding: utf-8 -*-
__author__ = 'Luke'

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.views import APIView, Response
from zalo01.serializers import UserSerializers
from django.shortcuts import render, redirect, HttpResponse
from zalo01.viewss.server_views import is_superuser
from zalo01 import common
from django.contrib import auth
from zalo01 import models


class LoginView(APIView):

    def get(self, request):
        return render(request, 'user/login.html')

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user_obj = auth.authenticate(username=username, password=password)
        if user_obj:
            auth.login(request, user_obj)
            return Response({"code": True, "msg": "登陆成功", "admin": user_obj.is_superuser})
        return Response({"code": False, "msg": "账户不存在或密码错误"})


class LogoutView(APIView):

    def get(self, request):
        auth.logout(request)
        return redirect("/login/")


class SuperUserView(APIView):

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def get(self, request):
        user_all = models.UserInfo.objects.exclude(id__in=[request.user.id])
        result = common.Page_dispose(request, user_all.count())
        if result["code"] != 200:
            return Response(result)
        user_obj = UserSerializers(user_all[result["start_page"]:result["end_page"]], many=True)
        return render(request, 'user/user_list.html', {"user_all": user_obj.data, "nav": "superuser",
                                                       "page_obj": result})

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        is_active = request.data.get("is_active")
        mobile_list = request.data.get("mobile_list", "")
        # 查看用户名是否被占用
        is_user = models.UserInfo.objects.filter(username=username).first()
        if not username or not password or not is_active:
            return Response({"code": 400, "msg": "User name and password and permissions are required"})
        if is_user:
            return Response({"code": 400, "msg": "Duplicate user name"})
        user = models.UserInfo.objects.create_user(
            username=username, password=password, is_active=is_active,
            phone=password,
        )
        # 管理的机器
        if mobile_list:
            mobile_list = mobile_list.strip().split(",")
            models.PhoneInfo.objects.filter(id__in=mobile_list).update(userinfo=user)
        return Response({"code": 200, "msg": "Creating a successful"})


class SuperUserAlterView(APIView):

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def get(self, request, pk):
        user_obj = models.UserInfo.objects.filter(pk=pk).first()
        result = UserSerializers(user_obj)
        Phone_all_obj = models.PhoneInfo.objects.all()
        # Phone_all = PhoneSerializers(Phone_all_obj, many=True)
        phone_list = []
        for phone in Phone_all_obj:
            phone_dict = {"status": 0, "phone_id": phone.id}
            if not phone.userinfo:
                phone_dict["status"] = 0
            elif phone.userinfo == user_obj:
                phone_dict["status"] = 1
            else:
                phone_dict["status"] = 2
            phone_list.append(phone_dict)
        return render(request, "user/user_add.html",
                      {"user_info": result.data, "phone_all": phone_list, "nav": "superuser"})
        # return Response(result.data)

    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def post(self, request, pk):
        username = request.data.get("username")
        password = request.data.get("password")
        is_active = request.data.get("is_active")
        mobile_list = request.data.get("mobile_list", "")
        if not username or not password or not is_active:
            return Response({"code": 400, "msg": "User name and password and permissions are required"})
        former_user = models.UserInfo.objects.filter(pk=pk).first()
        if not former_user:
            return Response({"code": 400, "msg": "The user does not exist"})
        former_user.set_password(password)
        former_user.save()
        models.UserInfo.objects.filter(pk=pk).update(phone=password)
        models.PhoneInfo.objects.filter(userinfo=former_user).update(userinfo=None)
        models.UserInfo.objects.filter(pk=pk).update(username=username, is_active=is_active)
        if mobile_list:
            mobile_list = mobile_list.strip().split(",")
            models.PhoneInfo.objects.filter(id__in=mobile_list).update(userinfo=former_user)
        return Response({"code": 200, "msg": "update successfully"})


    @method_decorator(login_required)
    @method_decorator(is_superuser)
    def delete(self, request, pk):
        result = {"code": True, "msg": ""}
        try:
            models.UserInfo.objects.filter(pk=pk).delete()
            result["msg"] = "successfully delete"
        except BaseException as b:
            result["code"] = False
            result["msg"] = str(b)
        return Response(result)
