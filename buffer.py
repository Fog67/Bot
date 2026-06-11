import sqlite3
import json
import logging
import os
import shutil
from typing import List, Dict
from datetime import datetime
import paho.mqtt.client as mqtt
import socket
def is_connected(host = "8.8.8.8", port = 53, timeout = 3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

class LocalBuffer:
    def __init__(self, path = r'D:\Desktop\testbuffer\buffer.db'):
        self.path = path
        self.init_db()
        self.clean_old_data(days=30)

    def init_db(self):
        with sqlite3.connect(self.path) as connect:
            cursor = connect.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS message_queue(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        meter_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        UNIQUE(meter_id, timestamp)
                    )''')
            connect.commit()

    def save(self, data: list[dict]):
        with sqlite3.connect(self.path) as connect:
            cursor = connect.cursor()
            for d in data:
                json_form = json.dumps(d)
                cursor.execute('''INSERT OR IGNORE INTO message_queue (meter_id, timestamp, payload)
                    VALUES (?, ?, ?)''', (d['meter_id'], d['timestamp'], json_form))
            connect.commit()

    def get_db(self):
        with sqlite3.connect(self.path) as connect:
            cursor = connect.cursor()
            cursor.execute('SELECT id, payload FROM message_queue ORDER BY id ASC')
            return cursor.fetchall()

    def delete_sent(self, sent: list[int]):
        if not sent:
            return
        with sqlite3.connect(self.path) as connect:
            cursor = connect.cursor()
            placeholder = ','.join('?' * len(sent))
            cursor.execute(f'DELETE FROM message_queue WHERE id IN ({placeholder})', sent)
            connect.commit()

    def clean_old_data(self, days = 30):
        with sqlite3.connect(self.path) as connect:
            cursor = connect.cursor()
            cursor.execute(f'''
                        DELETE FROM message_queue 
                        WHERE timestamp < datetime('now', '-{days} days')
                    ''')
            connect.commit()

class MQTTPublisher:
    def __init__(self, host: str, port: int, topic: str):
        self.host = host
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
    def publish(self, data: list[dict]):
        try:
            self.client.connect(self.host, self.port, keepalive=300)
            for d in data:
                json_form = json.dumps(d)
                self.client.publish(self.topic,json_form, qos=1)
            self.client.disconnect()
            return True
        except Exception as e:
            print(e)
            return False

class Manager:
    def __init__(self, host = "test.mosquitto.org", port = 1883, topic = "sensors/data"):
        self.db = LocalBuffer()
        self.mqtt = MQTTPublisher(host, port, topic)

    def publish(self, data: list[dict]):
        if not data:
            return
        if is_connected():
            print("Есть подключение к сети")

            if self.mqtt.publish(data):
                print('Данные отправлены')

            self.send_buffer()

        else:
            print("Нет подключения к сети")
            self.db.save(data)
            print("Данные сохранены в локальный буфер")

    def send_buffer(self):
        db = self.db.get_db()
        if not db:
            return
        to_send = []
        to_delete = []
        for message_id, info in db:
            to_send.append(json.loads(info))
            to_delete.append(message_id)

        if self.mqtt.publish(to_send):
            self.db.delete_sent(to_delete)
            print("Данные отправлены из буфера")
        else:
            print("Данные не отправлены из буфера")

