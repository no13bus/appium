from django.test import TestCase

# Create your tests here.

import requests

page = 10
"""
4 5 6 7 8 9 10
"""
# for i in range(page-3, page+4):
#     print(i)

# def func(index=1):
#     print(index)
#     if index > 4:
#         return
#     index += 1
#     if index ==2:
#         return
#     return func(index)
#
# import linecache
#
# phone_number = linecache.getline(r'D:\git\zalo\zalo_script\user_document\004641d375cbc21aa95dc0684fab6c6d.txt', 15)
#
# print(phone_number)
# phon_info = phone_number.strip("\n").replace(" ", "").split("|")


# import json
# def f(name, sex, age):
#     print(name, sex, age)
#
# r = requests.request("PUT", 'http://127.0.0.1:8000/api/phoninfo/', data = {'udid':'123456', "Param": json.dumps({"name": 'andy', "sex": "famale", "age": 18})})
# print(r)

import xlrd


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


import os
from Zalo import settings
def DisposeExcel(filepath):
    file_name = filepath.split("\\")[-1].split(".")[0]
    file_url_path = os.path.join("static", "user_file", "%s.txt" % file_name)
    with open(filepath, "w", encoding="utf8") as f:
        for i in read_excel(filepath):
            f.write("{} | {}\n".format(i[0], int(i[1])))
    return settings.HOST_IP + file_url_path



print(DisposeExcel("E:\phoneinfo.xlsx"))