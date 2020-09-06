from kutana import Plugin, HandlerResponse, get_path
from kutana.backends import Vkontakte, Telegram
from kutana.backends.vkontakte.backend import VKRequest
from pymongo import MongoClient
from bs4 import BeautifulSoup
from lxml import html
import openpyxl
import numpy as np
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import pytz
import re
import urllib
import requests
import asyncio
import json
from datetime import datetime
import time
import os

config = json.load(open("config.json", 'r'))

client = MongoClient(config['mongo_connect'])

db = client['mirea']
schedule_collection = db['schedule']

MENU_BUTTON = {
    "one_time": False,
    "buttons": [
        [
            {
                "action": {"type": "text", "payload": "1", "label": "Меню"},
                "color": "secondary",
            }
        ]
    ]
}

KEYBOARD_MENU_OBJECT = {
    "inline": True,
    "buttons": [
        [
            {
                "action": {"type": "text", "payload": "20", "label": "Расписание"},
                "color": "primary",
            },
            {
                "action": {"type": "text", "payload": "21", "label": "Время проведения занятий"},
                "color": "primary",
            },
        ],
        # [
        #     {
        #         "action": {"type": "text", "payload": "22", "label": "Учебный материал"},
        #         "color": "primary",
        #     },
        # ]
    ],
}

KEYBOARD_DAY_CURRENT_SELECT_OBJECT = {
    "inline": True,
    "buttons": [
        [
            {
                "action": {"type": "text", "payload": "{\"button\": \"current 0\"}", "label": "ПН"},
                "color": "primary",
            },
            {
                "action": {"type": "text", "payload": "{\"button\": \"current 1\"}", "label": "ВТ"},
                "color": "primary",
            },
            {
                "action": {"type": "text", "payload": "{\"button\": \"current 2\"}", "label": "СР"},
                "color": "primary",
            },
            {
                "action": {"type": "text", "payload": "{\"button\": \"current 3\"}", "label": "ЧТ"},
                "color": "primary",
            },
            {
                "action": {"type": "text", "payload": "{\"button\": \"current 4\"}", "label": "ПТ"},
                "color": "primary",
            }
        ],
    ],
}

KEYBOARD_DAY_NEXT_SELECT_OBJECT = {
    "inline": True,
    "buttons": [
        [
            {
                "action": {"type": "text", "payload": "{\"button\": \"next 0\"}", "label": "ПН"},
                "color": "primary",
            },
            {
                "action": {"type": "text", "payload": "{\"button\": \"next 1\"}", "label": "ВТ"},
                "color": "primary",
            },
            {
                "action": {"type": "text", "payload": "{\"button\": \"next 2\"}", "label": "СР"},
                "color": "primary",
            },
            {
                "action": {"type": "text", "payload": "{\"button\": \"next 3\"}", "label": "ЧТ"},
                "color": "primary",
            },
            {
                "action": {"type": "text", "payload": "{\"button\": \"next 4\"}", "label": "ПТ"},
                "color": "primary",
            }
        ],
    ],
}

KEYBOARD_WEEK_SELECT_OBJECT = {
    "inline": True,
    "buttons": [
        [
            {
                "action": {"type": "text", "payload": "31", "label": "Текущая неделя"},
                "color": "secondary",
            },
            {
                "action": {"type": "text", "payload": "32", "label": "Следующая неделя"},
                "color": "secondary",
            },
        ]
    ],
}

KEYBOARD_WEEK_SELECT_OBJECT_STRING = json.dumps(KEYBOARD_WEEK_SELECT_OBJECT)
KEYBOARD_DAY_NEXT_SELECT_OBJECT_STRING = json.dumps(KEYBOARD_DAY_NEXT_SELECT_OBJECT)
KEYBOARD_DAY_CURRENT_SELECT_OBJECT_STRING = json.dumps(KEYBOARD_DAY_CURRENT_SELECT_OBJECT)
KEYBOARD_MENU_OBJECT_STRING = json.dumps(KEYBOARD_MENU_OBJECT)
MENU_BUTTON_STRING = json.dumps(MENU_BUTTON)
plugin = Plugin(name="MIREA", description="Bot for VK")

async def new_schedule_check(ctx):
    while True:

        #################### get url:
        resp = requests.get("https://www.mirea.ru/schedule/")
        soup = BeautifulSoup(resp.text, 'lxml')

        test = soup.findAll('a', class_='uk-link-toggle')
        url = test[15].get('href')
        #############################
      
        f = open(get_path(__file__, "schedule.xlsx"), "wb") # открываем файл для записи, в режиме wb
        ufr = requests.get(url)
        f.write(ufr.content) 
        f.close()

        wb = openpyxl.load_workbook(get_path(__file__, "schedule.xlsx")) 
        ws = wb.active
        SCHEDULE_LETTER = ''
        CABINETS_LETTER = ''
        TYPE_LETTER = ''

        for column in range(50, 900):
            column_letter = get_column_letter(column)
            current_column = ws[column_letter]

            for cell in current_column:
                if isinstance(cell.value, str):
                    #print(cell.value)
                    if cell.value.find('25-20') > -1:
                        #print(cell.value)
                        LETTER = column_letter
                        TYPE_LETTER  = get_column_letter(column+1)
                        CABINETS_LETTER  = get_column_letter(column+3)

        column_days = ws[LETTER]
        culumn_cabs = ws[CABINETS_LETTER]
        culumn_type = ws[TYPE_LETTER]

        arr_days = []
        arr_cabs = []
        arr_types = []

        for cell in column_days:
            arr_days.append(cell.value)

        for cell in culumn_cabs:
            arr_cabs.append(cell.value)

        for cell in culumn_type:
            arr_types.append(cell.value)

        arr_cabs = arr_cabs[3:75]
        arr_days = arr_days[3:75]
        arr_types = arr_types[3:75]

        cabs = np.array_split(arr_cabs, 6)
        days = np.array_split(arr_days, 6)
        types = np.array_split(arr_types, 6)

        os.remove(get_path(__file__, "schedule.xlsx"))

        all_days_list = []
        all_cabs_list = []
        all_types_list = []

        for day in days:
            all_days_list.append(list(day))

        for cab in cabs:
            all_cabs_list.append(list(cab))

        for typed in types:
            all_types_list.append(list(typed))

        schedule_all = schedule_collection.find_one({'type': 'days'})
        tz = pytz.timezone('Europe/Moscow')
        date = datetime.now(tz).weekday()

        if schedule_all is not None:
            if date == 6 and schedule_all['changeEven'] == False:
                schedule_collection.update_one({'type': 'days'}, {'$set': {'changeEven': True}})
            elif date == 0 and schedule_all['changeEven'] == True:
                isEven = schedule_all['isEven']
                schedule_collection.update_one({'type': 'days'}, {'$set': {'isEven': not isEven, 'changeEven': False}})
            schedule_collection.update_one({'type': 'days'}, {'$set': {'schedule': all_days_list, 'cabs': all_cabs_list, 'types': all_types_list}})
        else:
            schedule_collection.insert_one({'type': 'days', 'schedule': all_days_list, 'cabs': all_cabs_list, 'types': all_types_list, 'changeEven': False, 'isEven': False})
     
        await asyncio.sleep(600)

async def convert(obj):
    if obj is not None:
        return " [" + obj + "]"
    else:
        return ''

@plugin.on_commands(["menu", 'меню', 'начать', 'start', 'help', 'помощь', 'икбо'])
async def _(msg, ctx):
    await ctx.reply("Выберите опцию:", keyboard=KEYBOARD_MENU_OBJECT_STRING)

@plugin.vk.on_payload([31])
async def _(msg, ctx):
    schedule_all = schedule_collection.find_one({'type': 'days'})
    if schedule_all['isEven']:
        await ctx.reply("Текущая неделя четная. Выберите день текущей недели:", keyboard=KEYBOARD_DAY_CURRENT_SELECT_OBJECT_STRING)
    else:
        await ctx.reply("Текущая неделя нечетная. Выберите день текущей недели:", keyboard=KEYBOARD_DAY_CURRENT_SELECT_OBJECT_STRING)

@plugin.vk.on_payload([32])
async def _(msg, ctx):
    schedule_all = schedule_collection.find_one({'type': 'days'})
    if schedule_all['isEven']:
        await ctx.reply("Следующая неделя нечетная. Выберите день следующей недели:", keyboard=KEYBOARD_DAY_NEXT_SELECT_OBJECT_STRING)
    else:
        await ctx.reply("Следующая неделя четная. Выберите день следующей недели:", keyboard=KEYBOARD_DAY_NEXT_SELECT_OBJECT_STRING)

@plugin.on_commands(["расписание", 'р', 'schedule'])
async def _(msg, ctx):
    schedule_all = schedule_collection.find_one({'type': 'days'})
    if schedule_all['isEven']:
        await ctx.reply("Текущая неделя четная. Выберите день текущей недели:", keyboard=KEYBOARD_DAY_CURRENT_SELECT_OBJECT_STRING)
    else:
        await ctx.reply("Текущая неделя нечетная. Выберите день текущей недели:", keyboard=KEYBOARD_DAY_CURRENT_SELECT_OBJECT_STRING)

@plugin.vk.on_payload([20])
async def _(msg, ctx):
    await ctx.reply("Выберите неделю", keyboard=KEYBOARD_WEEK_SELECT_OBJECT_STRING)


@plugin.on_any_unprocessed_message()
async def on_payloads(msg, ctx):
    if 'payload' in msg.raw['object']['message']:
        if isinstance(msg.raw['object']['message']['payload'], str):
            payload = json.loads(msg.raw['object']['message']['payload'])
            if payload['button'].split()[0] == 'current' or payload['button'].split()[0] == 'next':
                msg = ''
                schedule_all = schedule_collection.find_one({'type': 'days'})
                index = int(payload['button'].split()[1])
                arr_lesson = np.array_split(schedule_all['schedule'][index], 6)
                arr_cabs = np.array_split(schedule_all['cabs'][index], 6)
                arr_types = np.array_split(schedule_all['types'][index], 6)

                if payload['button'].split()[0] == 'current':
                    for i in range(6):
                        if arr_lesson[i][int(schedule_all['isEven'])] is not None:
                            msg += "☠ " + str(i+1) + " пара: " + arr_lesson[i][int(schedule_all['isEven'])] + await convert(arr_cabs[i][int(schedule_all['isEven'])]) + await convert(arr_types[i][int(schedule_all['isEven'])]) + "\n"
                elif payload['button'].split()[0] == 'next':
                    for i in range(6):
                        if arr_lesson[i][int(not schedule_all['isEven'])] is not None:
                            msg += "☠ " + str(i+1) + " пара: " + arr_lesson[i][int(not schedule_all['isEven'])] + await convert(arr_cabs[i][int(not schedule_all['isEven'])]) + await convert(arr_types[i][int(not schedule_all['isEven'])]) + "\n"
                
                await ctx.reply(msg)

@plugin.vk.on_payload([21])
async def _(msg, ctx):
    msg = "1 пара – 9:00-10:30\n"
    msg += "2 пара – 10:40-12:10\n"
    msg += "3 пара – 12:40-14:10\n"
    msg += "4 пара – 14:20-15:50\n"
    msg += "5 пара – 16:20-17:50\n"
    msg += "6 пара – 18:00-19:30"

    await ctx.reply(msg)

@plugin.on_start()
async def _(app):
    backend = app.get_backends()[0]

    # Run only if first backend is Vkontakte
    if backend.get_identity() == "vkontakte":
        asyncio.ensure_future(new_schedule_check(backend))

@plugin.on_any_message(priority=10)
async def _(msg, ctx):
    if ctx.backend.get_identity() != "vkontakte":
        return HandlerResponse.SKIPPED

    payload = msg.raw["object"]["message"].get("payload")
    if not payload or payload != "4":
        return HandlerResponse.SKIPPED
    