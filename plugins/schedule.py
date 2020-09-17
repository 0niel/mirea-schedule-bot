from kutana import Plugin, HandlerResponse
from database import schedule_collection
import numpy as np
import json


KEYBOARD_MENU_OBJECT = {
    "inline": False,
    "one_time": False,
    "buttons": [
        [
            {
                "action": {"type": "text", "payload": "20", "label": "Расписание"},
                "color": "primary",
            },
            {
                "action": {"type": "text", "payload": "21", "label": "Время проведения занятий"},
                "color": "primary",
            }
        ]
    ]
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

plugin = Plugin(name="MIREA Schedule", description="Bot for VK")


async def convert(obj):
    if obj is not None:
        return "[" + obj + "]"
    return ''


@plugin.on_commands(["menu", 'меню', 'начать', 'start', 'help', 'помощь', 'икбо'])
async def _(_, ctx):
    await ctx.reply("Выберите опцию.", keyboard=KEYBOARD_MENU_OBJECT_STRING)


@plugin.on_commands(["week_number"])
async def _(msg, ctx):
    if msg.raw['object']['message']['from_id'] == json.load(open("config.json", 'r'))['admin_id']:
        schedule_collection.update_one({'type': 'schedule'},
                                       {'$set': {'week_number': int(ctx.body)}})

        await ctx.reply("Номер недели успешно изменен на " + ctx.body)


@plugin.on_commands(["even"])
async def _(msg, ctx):
    if msg.raw['object']['message']['from_id'] == json.load(open("config.json", 'r'))['admin_id']:
        is_even = False
        if ctx.body == 'True':
            is_even = True
        elif ctx.body == 'False':
            is_even = False
        schedule_collection.update_one({'type': 'schedule'},
                                       {'$set': {'is_even': is_even}})

        await ctx.reply("Четность недели успешно установлена на " + ctx.body)


@plugin.vk.on_payload([32])
async def _(_, ctx):
    schedule_all = schedule_collection.find_one({'type': 'schedule'})
    if schedule_all['is_even']:
        await ctx.reply("Следующая неделя нечетная. Выберите день следующей недели:",
                        keyboard=KEYBOARD_DAY_NEXT_SELECT_OBJECT_STRING)
    else:
        await ctx.reply("Следующая неделя четная. Выберите день следующей недели:",
                        keyboard=KEYBOARD_DAY_NEXT_SELECT_OBJECT_STRING)


@plugin.vk.on_payload([31])
async def _(_, ctx):
    await current_week_schedule(ctx)


@plugin.on_commands(["расписание", 'р', 'schedule'])
async def _(_, ctx):
    await current_week_schedule(ctx)


async def current_week_schedule(ctx):
    schedule_all = schedule_collection.find_one({'type': 'schedule'})
    if schedule_all['is_even']:
        await ctx.reply("Текущая неделя четная. Выберите день текущей недели:",
                        keyboard=KEYBOARD_DAY_CURRENT_SELECT_OBJECT_STRING)
    else:
        await ctx.reply("Текущая неделя нечетная. Выберите день текущей недели:",
                        keyboard=KEYBOARD_DAY_CURRENT_SELECT_OBJECT_STRING)


@plugin.vk.on_payload([20])
async def _(_, ctx):
    await ctx.reply("Выберите неделю", keyboard=KEYBOARD_WEEK_SELECT_OBJECT_STRING)


def get_day_by_index(index):
    if index == 0:
        day = 'Понедельник'
    elif index == 1:
        day = 'Вторник'
    elif index == 2:
        day = 'Среда'
    elif index == 3:
        day = 'Четверг'
    else:
        day = 'Пятница'

    return day


def get_time_by_index(index):
    if index == 0:
        time = "9:00-10:30"
    elif index == 1:
        time = "10:40-12:10"
    elif index == 2:
        time = "12:40-14:10"
    elif index == 3:
        time = "14:20-15:50"
    elif index == 4:
        time = "16:20-17:50"
    else:
        time = "18:00-19:30"
    return time


@plugin.on_any_unprocessed_message()
async def on_payloads(msg, ctx):
    if 'payload' in msg.raw['object']['message']:
        if isinstance(msg.raw['object']['message']['payload'], str):
            payload = json.loads(msg.raw['object']['message']['payload'])
            if payload['button'].split()[0] == 'current' or payload['button'].split()[0] == 'next':

                schedule_all = schedule_collection.find_one({'type': 'schedule'})
                index = int(payload['button'].split()[1])
                arr_lesson = np.array_split(schedule_all['schedule'][index], 6)
                arr_cabs = np.array_split(schedule_all['cabinets'][index], 6)
                arr_types = np.array_split(schedule_all['lesson_types'][index], 6)
                arr_teachers = np.array_split(schedule_all['teachers'][index], 6)
                day = get_day_by_index(index)

                if payload['button'].split()[0] == 'current':
                    msg = f"{day} текущей недели:\n"
                    for i in range(6):
                        if arr_lesson[i][int(schedule_all['is_even'])] is not None:
                            if arr_lesson[i][int(schedule_all['is_even'])].find(' н.') > -1:
                                if str(schedule_all['week_number']) in \
                                        arr_lesson[i][int(schedule_all['is_even'])].split(' н. ')[0].split(','):
                                    arr_lesson[i][int(schedule_all['is_even'])] = \
                                        arr_lesson[i][int(schedule_all['is_even'])].split(' н. ')[1]
                                else:
                                    continue
                            msg += "☠ {0} пара ({1}): {2} {3} {4} {5}\n".format(
                                str(i + 1),
                                get_time_by_index(i),
                                arr_lesson[i][int(schedule_all['is_even'])],
                                await convert(arr_cabs[i][int(schedule_all['is_even'])]),
                                await convert(arr_types[i][int(schedule_all['is_even'])]),
                                await convert(arr_teachers[i][int(schedule_all['is_even'])])
                            )

                elif payload['button'].split()[0] == 'next':
                    msg = f"{day} следующей недели:\n"
                    for i in range(6):
                        if arr_lesson[i][int(not schedule_all['is_even'])] is not None:
                            if arr_lesson[i][int(not schedule_all['is_even'])].find(' н.') > -1:
                                if str(schedule_all['week_number'] + 1) in \
                                        arr_lesson[i][int(not schedule_all['is_even'])].split(' н. ')[0].split(','):
                                    arr_lesson[i][int(not schedule_all['is_even'])] = \
                                        arr_lesson[i][int(not schedule_all['is_even'])].split(' н. ')[1]
                                else:
                                    continue
                            msg += "☠ {0} пара ({1}): {2} {3} {4} {5}\n".format(
                                str(i + 1),
                                get_time_by_index(i),
                                arr_lesson[i][int(not schedule_all['is_even'])],
                                await convert(arr_cabs[i][int(not schedule_all['is_even'])]),
                                await convert(arr_types[i][int(not schedule_all['is_even'])]),
                                await convert(arr_teachers[i][int(not schedule_all['is_even'])])
                            )

                await ctx.reply(msg)


@plugin.vk.on_payload([21])
async def _(_, ctx):
    msg = "1 пара – 9:00-10:30\n"
    msg += "2 пара – 10:40-12:10\n"
    msg += "3 пара – 12:40-14:10\n"
    msg += "4 пара – 14:20-15:50\n"
    msg += "5 пара – 16:20-17:50\n"
    msg += "6 пара – 18:00-19:30"

    await ctx.reply(msg)


@plugin.on_any_message(priority=10)
async def _(msg, ctx):
    if ctx.backend.get_identity() != "vkontakte":
        return HandlerResponse.SKIPPED

    payload = msg.raw["object"]["message"].get("payload")
    if not payload or payload != "4":
        return HandlerResponse.SKIPPED
