# -*- coding: utf-8 -*-
__author__ = 'Luke'
import redis
import json
import time

pool = redis.ConnectionPool(host='127.0.0.1', port='6379')
#
r1 = redis.Redis(connection_pool=pool)
# r1.delete("luke_order")
# r1.hmset("luke_order", {"task_name":json.dumps({"name": "andy"})})
# print(r1.hkeys("luke_order"))
# dict_info = json.loads(r1.hmget("luke_order", "send_circle_of_friends_1575610191")[0].decode("utf8"))
# dict_info["succeed_device"]["ok"] = "ok"
# print(dict_info)
# #
# #
# # user_redis = "{}_order".format("luke")
# dict_info = json.loads(r1.hmget(user_redis, "task_name")[0].decode("utf8"))
# dict_info["name"] = "luke"
# r1.hmset("luke_order", {"task_name":json.dumps(dict_info)})
# print(json.loads(r1.hmget(user_redis, "task_name")[0].decode("utf8")))
# r1.set("update_room", 0)
# print(r1.get("name").decode("utf8"))
# r1.set("name", "dream2")
# print(r1.get("update_room"))

# print(r1.hget("root", "room_class"))
#
# print(r1.hgetall('root'))
# lule :{ 命令_时间： {操作, 状态（是否开始执行 0~1），进度(0~100)百分比，是否执行完毕状态（0~1），发送时间，执行时间，结束时间，过期时间}}
# r1.hmset('appp', {'k2': "123456", 'k3': 'v3'})
# print(r1.hgetall('appp'))
# r1.hdel("appp", "k2")
# print(r1.hgetall('appp'))
# print(r1.hmget('luke_order', "start_zalo_1574674350"))
# print(len({'k2': "123456", 'k3': 'v3'}))
# res_dict = r1.hkeys('luke_order', k2)
# res_dict = r1.delete('luke_order')
# print(res_dict)
# def get_value(name, re):
#     value = r1.hmget('luke_order', name.decode("utf8"))
#     value_dict = json.loads(value[0].decode("utf8"))
#     if not value_dict["over"]:
#         return value_dict

# for i in range(5):

# [i if i else "" for i in map(lambda x:json.loads(r1.hmget('luke_order', x.decode("utf8"))[0].decode("utf8")) if not json.loads(r1.hmget('luke_order', x.decode("utf8"))[0].decode("utf8"))["over"] else None, res_dict)]


# # 获取全部键值
# print(r1.hgetall('luke'))
#
# # 获取键值数量
# print(r1.hlen('luke'))
#
# # 获取所有的key
# print(r1.hkeys('luke'))

# 获取所有的value
# print(r1.hvals('luke'))

# # 判断key在不在
# print(r1.hexists('luke', 'test1'))
#
# # 删除对应的键值
# print(r1.hdel('luke', '3_6'))
#
# # 获取键值个数
# print(r1.hlen('luke'))
# p@zzw0rId!
# 集合添加
# r1.sadd("redis_set", "phone_number")
# r1.sadd("redis_set", "48")
# r1.sadd("redis_set", "2")
# r1.sadd("redis_set", "3")
# r1.sadd("redis_set", "1")
# # r1.srem("redis_set", "phone_number")  # 删除指定集合键
# r1.sadd("redis_set1", "1")
# r1.sadd("redis_set1", "2")
# r1.sadd("redis_set1", "3")
# r1.sadd("redis_set1", "48")
# r1.sadd("redis_set1", "phone_number")
# res = r1.sdiffstore("short", "redis_set", "redis_set1")
# # print(res)
# print(r1.spop("short"))
# print(r1.sinter("short"))

# print(r1.sinter("redis_set"))
# r1.sadd("redis_progress_bar")
# import json
# r1.set("sum", json.dumps({"1":1}))
# print(r1.get("sum"))
# r1.expire("sum", 5)
# time.sleep(6)
# print(r1.get("sum"))
# print(type(json.loads(r1.get("sum"))))
# print(r1.exists("sum"))

# time.sleep(5)
# print(r1.exists("sum"))
# r1.delete("luke")
# print(r1.hgetall("luke"))

# r1.set("update_room", 0)


# r1.sadd('set-key', 'c')
# print(len(r1.sinter("set-key")))
# print(r1.spop("set-key"))
# print(r1.spop("set-key"))
# print(len(r1.sinter("set-key")))

r1.set("update_room", 0)
"""
appium端口及adb端口
"""
# r1.sadd("appium_and_adb1", json.dumps({"appium": 4723, "adb": 8200}))
# r1.sadd("appium_and_adb1", json.dumps({"appium": 4723, "adb": 8200}))
# # r1.sadd("appium_and_adb", json.dumps({"appium": 4725, "adb": 8201}))
# # r1.sadd("appium_and_adb", json.dumps({"appium": 4727, "adb": 8202}))
# # r1.sadd("appium_and_adb", json.dumps({"appium": 4729, "adb": 8203}))
# # r1.sadd("appium_and_adb", json.dumps({"appium": 4731, "adb": 8204}))
# # r1.sadd("appium_and_adb", json.dumps({"appium": 4733, "adb": 8205}))
# print(json.loads(r1.spop("appium_and_adb1")))
# # if r1.sinter("appium_and_adb"):
# #     print("还有值")
# print(r1.sinter("appium_and_adb1"))
# r1.delete("appium_and_adb1")
# print(r1.sinter("appium_and_adb1"))
# # def work(index):
# #     d = r1.spop("appium_and_adb")
# #     print(json.loads(d))
# #     time.sleep(50)
# #
# # import multiprocessing
# # if __name__ == '__main__':
# #     p_count = len(r1.sinter("appium_and_adb"))
# #     for i in range(p_count):
# #         p = multiprocessing.Process(target=work, args=(i,))
#         p.start()
