# -*- coding: utf-8 -*-
__author__ = 'Luke'

from zalo01 import models
from Zalo.settings import *
import logging.config
import logging
import xlrd


# log配置字典
LOGGING_DIC = {
    'version': 1,
    'disable_existing_loggers': False,

    # 定义日志的格式
    'formatters': {
        'standard': {
            'format': standard_format
        },
        'simple': {
            'format': simple_format
        },
        'id_simple': {
            'format': id_simple_format
        }
    },

    # 定义日志输出的目标：文件或者终端
    'handlers': {
        'access': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件
            'formatter': 'standard',
            'filename': LOG_PATH,  # 日志文件
            'maxBytes': 1024*1024,  # 单位比特，超过就新建文件
            'backupCount': 5,  # 最多保存多少份文件
            'encoding': 'utf-8',  # 日志文件的编码
        },
    },
    'loggers': {
        '': {
            'handlers': ['access'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
logging.config.dictConfig(LOGGING_DIC)
LogRecord = logging.getLogger()


def filtrate_None(value):
    for i in value:
        if i == "":
            return False
    return True


def read_excel(file_path):
    """ 读取excel文件"""
    wb = xlrd.open_workbook(filename=file_path)  # 打开文件
    table = wb.sheet_by_index(0)
    for i in range(1, table.nrows):
        value = table.row_values(i)
        if filtrate_None(value):
            yield value


def get_screenshot(phone_obj):
    """ 获取最后的截图"""
    screenshot = models.Screenshot.objects.filter(phone_id=phone_obj.id).order_by("id").reverse().first()
    if screenshot:
        return screenshot.photo_path.replace("\\\\", "\\")
    return "/static/img/pindex.png"


def get_phone_info_status(phone_obj):
    """ 获取设备的状态"""
    if phone_obj.status != 2:
        # return "未连接"
        return "Chưa kết nối"
    if phone_obj.zalo_status == 1 and phone_obj.VPN_status == 1:
        if phone_obj.is_operation:
            # return "运行中"
            return "Đang chạy"
        else:
            # return "空闲"
            return "Rảnh"
    else:
        # return "待登录"
        return "Đang đăng nhập"

