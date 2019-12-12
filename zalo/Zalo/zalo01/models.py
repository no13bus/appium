from django.db import models
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    phone = models.CharField(max_length=11, null=True, unique=True)

    def __str__(self):
        return self.username


class IdInfo(models.Model):
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=32, unique=True)
    phone = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=32)
    creationtime = models.DateTimeField(auto_now_add=True)
    updatetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Server(models.Model):
    ip = models.GenericIPAddressField(unique=True)
    series = models.CharField(max_length=16, unique=True)
    creationtime = models.DateTimeField(auto_now_add=True)
    updatetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ip


class OpenVpn(models.Model):
    file_name = models.CharField(max_length=32, unique=True)
    file_path = models.CharField(max_length=64, unique=True)
    ip_port = models.CharField(max_length=32, default=1)
    status_choices = ((0, "close"), (1, "open"))
    status = models.IntegerField(choices=status_choices, default=1)
    device_count = models.IntegerField(default=0)  # 已绑定
    device_max = models.IntegerField(default=5)  # 最大绑定设备数
    creationtime = models.DateTimeField(auto_now_add=True)
    updatetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_name


class PhoneInfo(models.Model):
    phone_name = models.CharField(max_length=32, null=True, blank=True, unique=True)

    udid = models.CharField(max_length=32, null=True, blank=True, unique=True)

    status_choices = ((0, "off"), (1, "fault"), (2, "on"))
    # 设备状态
    status = models.IntegerField(choices=status_choices, default=0)
    choices = ((0, "off"), (1, "on"), (2, "update"))
    # 是否已经登陆，运行zalo
    zalo_status = models.IntegerField(choices=choices, default=0)
    # 是否安装app
    app_install = models.IntegerField(choices=choices, default=0)
    # 是否在运行中
    is_operation = models.IntegerField(choices=choices, default=0)
    # vpn是否开启
    VPN_status = models.IntegerField(choices=choices, default=0)

    # ZAlO账号是否被限制
    # is_restrict = models.IntegerField(choices=choices, default=0)

    server = models.ForeignKey(to="Server", on_delete=models.CASCADE)
    idinfo = models.OneToOneField(to="IdInfo", on_delete=models.SET_NULL, null=True)
    # 绑定的vpn,为空之前必须退出vpn
    OpenVpn = models.ForeignKey(to="OpenVpn", on_delete=models.SET_NULL, null=True)
    userinfo = models.ForeignKey(to="UserInfo", on_delete=models.SET_NULL, null=True, blank=True)

    creationtime = models.DateTimeField(auto_now_add=True)
    updatetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.udid

class Phone_Operation_Log(models.Model):
    """ 统计当天的发送数、添加数、用来展示以及统计，"""
    # 有效发送数
    send_msg = models.IntegerField()
    # 有效添加数
    add_friend = models.IntegerField()
    # 发送给陌生人个数
    send_stranger = models.IntegerField()
    # 通过请求的好友数
    accept_request = models.IntegerField()
    # 操作类型
    operation = models.CharField(max_length=64)
    # 操作用户id
    userinfo = models.IntegerField()
    # 操作zalo id
    zaloinfo = models.IntegerField()
    # 操作时间戳
    executetime = models.FloatField()
    # 描述
    description = models.CharField(max_length=64)


class Screenshot(models.Model):
    """ 手机截图，"""
    photo_path = models.CharField(max_length=200, unique=True)
    phone_id = models.IntegerField()
    phone_operation_log_id = models.IntegerField()
