"""
    author: Jin-Mo,Lin
    email: s106003041@g.ksu.edu.tw
    description: MySQL Database
"""
import json
from peewee import *

print('start')

db = MySQLDatabase('jetson_db', user='jetson', passwd='!@IxhxbbmdjLcj2022', host='192.168.21.11', port=3307)

print('before connect')

db.connect()

print('connect to database')


class BaseModel(Model):
    class Meta:
        database = db


class AI(BaseModel):
    id = AutoField()
    pro_serial = CharField()
    mic_no = IntegerField()
    result = TextField()

    class Meta:
        table_name = 'ai_result'


print('insert')

AI.create(pro_serial='tteedd', mic_no='2', result=json.dumps(['NG', 'OK', 'NG', 'OK']))

print('end')

ai_list = AI.select()

for item in ai_list:
    print(f"id: {item.id}, pro_serial: {item.pro_serial}, mic_no: {item.mic_no}, result: {item.result}")
