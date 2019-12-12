"""Zalo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from zalo01.viewss.user_views import LogoutView, LoginView, SuperUserView, SuperUserAlterView
from zalo01.viewss.server_views import ServerView, ServerAlterView
from zalo01.viewss.phone_views import PhoneView, WebSocketView, Code, Get_AJAX_Room, PhoneAlterView, Progress_bar
from zalo01.viewss.ZaloId_views import ZaloIdView, ZaloIdAlterView
from zalo01.viewss.Vpn_views import VpnView, VpnAlterView
from zalo01.viewss.records_views import RecordsView, RecordsAlterView
from zalo01.viewss.API import *

urlpatterns = [
    path(r'admin/', admin.site.urls),

    path(r'login/', LoginView.as_view()),
    path(r'logout/', LogoutView.as_view()),

    path(r'websocket/', WebSocketView),
    path(r'Progressbar/', Progress_bar),
    path(r'getroom/', Get_AJAX_Room.as_view()),

    path(r'index/', PhoneView.as_view()),
    path(r'help/', PhoneView.as_view()),

    path(r'', PhoneView.as_view()),

    # path(r'result/', Resultview.as_view()),
    path(r'code/', Code.as_view()),

    # url(r'index$', LogoutView.as_view()),

    path(r"superuser/", SuperUserView.as_view()),
    path(r"superuser/<int:pk>/", SuperUserAlterView.as_view()),


    path(r'server/', ServerView.as_view()),
    path(r'server/<int:pk>/', ServerAlterView.as_view()),


    path(r'phone/', PhoneView.as_view()),
    path(r'phone/<int:pk>/', PhoneAlterView.as_view()),


    path(r'zaloid/', ZaloIdView.as_view()),
    path(r'zaloid/<int:pk>/', ZaloIdAlterView.as_view()),

    path(r'openvpn/', VpnView.as_view()),
    path(r'openvpn/<int:pk>/', VpnAlterView.as_view()),


    path(r'records/', RecordsView.as_view()),
    path(r'records/<int:pk>/', RecordsAlterView.as_view()),


    path(r'api/uploading/screenshot/', ScreenShotAPIView.as_view()),
    path(r'api/phoninfo/', PhoneAPIView.as_view()),
    path(r'api/operation/', OperationAPIView.as_view()),
    path(r'api/ProgressBar/', ProgressBarView.as_view()),




]
