# -*- coding: utf-8 -*-
__author__ = 'Luke'

from settings import *
import pika
import json


def PullMQ(queue, callback_func):
    """ 消费 """
    credentials = pika.PlainCredentials(USER, PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBITMQ_IP, RABBITMQ_PORT, '/', credentials=credentials))
    channel = connection.channel()

    # 开始依次消费balance队列中的消息
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_consume(queue=queue, on_message_callback=callback_func, )
    channel.start_consuming()  # 启动消费


def PushMQ(queue_name, res_msg):
    """ 生产 """
    credentials = pika.PlainCredentials(USER, PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBITMQ_IP, RABBITMQ_PORT, '/', credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,  # 写明将消息发送给队列balance
        body=json.dumps(res_msg),  # 要发送的消息
        properties=pika.BasicProperties(delivery_mode=2, )  # 设置消息持久化(持久化第二步)，将要发送的消息的属性标记为2，表示该消息要持久化
    )
