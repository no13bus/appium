# -*- coding: utf-8 -*-
__author__ = 'Luke'

import pika
import json

# 远程rabbitmq服务的配置信息
USER = 'luke'
PASSWORD = 'luke2019'
RABBITMQ_IP = '127.0.0.1'
RABBITMQ_PORT = 5672


def push(queue_ip, message_data, back_key=None):
    credentials = pika.PlainCredentials(USER, PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_IP, RABBITMQ_PORT, '/', credentials))
    channel = connection.channel()
    # 创建一个名为balance的队列，对queue进行durable持久化设为True(持久化第一步)
    channel.queue_declare(queue=queue_ip, durable=True)
    if back_key:
        channel.queue_declare(queue=back_key, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue_ip,  # 写明将消息发送给队列balance
        body=message_data,  # 要发送的消息
        properties=pika.BasicProperties(delivery_mode=2, )  # 设置消息持久化(持久化第二步)，将要发送的消息的属性标记为2，表示该消息要持久化
    )
    connection.close()


def pull(queue_name):
    credentials = pika.PlainCredentials(USER, PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_IP, RABBITMQ_PORT, '/', credentials))
    channel = connection.channel()
    result = {}

    def callback(ch, method, properties, body):
        result["res"] = json.loads(body)
        connection.close()

    # 开始依次消费balance队列中的消息
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()  # 启动消费
    return result["res"]
