# -*- coding: utf-8 -*-
__author__ = 'Luke'

import logging.config
import logging

# 定义三种日志输出格式
standard_format = '[%(asctime)s][%(threadName)s:%(thread)d][%(pathname)s:%(lineno)d]' \
                  '[%(levelname)s][%(message)s]'  # 其中name为getlogger指定的名字

simple_format = '[task_id:%(name)s][%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'

id_simple_format = '[task_id:%(name)s][%(levelname)s][%(asctime)s] %(message)s'

LOG_PATH = r'D:\git\zalo\zalo_script\log\error.log'

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
    'filters': {},

    # 定义日志输出的目标：文件或者终端
    'handlers': {
        # 打印到终端的日志
        # 'stream': {
        #     'level': 'DEBUG',
        #     'class': 'logging.StreamHandler',  # 打印到屏幕
        #     'formatter': 'simple'
        # },
        # 打印到文件的日志,收集info及以上的日志
        'access': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件
            'formatter': 'standard',
            'filename': LOG_PATH,  # 日志文件
            # 'maxBytes': 1024*1024*5,  # 日志大小 5M
            'maxBytes': 3000,  # 单位比特，超过就新建文件
            'backupCount': 5,  # 最多保存多少份文件
            'encoding': 'utf-8',  # 日志文件的编码
        },
    },
    'loggers': {
        '': {
            'handlers': ['access'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
# logging.config.dictConfig(LOGGING_DIC)
#
# LogRecord = logging.getLogger()
# # LogRecord.info('456')


