from pymongo import MongoClient
import json


config = json.load(open("config.json", 'r'))

client = MongoClient(config['mongo_connect'])
db = client['ScheduleBot']
schedule_collection = db['Schedule']
