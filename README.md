[![CodeFactor](https://www.codefactor.io/repository/github/0niel/mirea-schedule-bot/badge)](https://www.codefactor.io/repository/github/0niel/mirea-schedule-bot)
# mirea-schedule-bot
Бот выводит расписание на текущую и следующую неделю для выбранной группы. Расписание парсится с сайта и excel документа каждые 10 минут.

## Установка и запуск
Бот работает на python3.7+. 
1. Установите зависимости, описанные на requirements.txt: `pip install -r requirements.txt`
2. Настройте бота в `config.json`
3. Запустите run.py (`python run.py`)
4. В диалоге с ботом воспользуйтесь командами `/week_number [номер]` и `/even [True/False]` для установки номера текущей недели и ее четности. Пример: `/week_number 4`, `/even True`

### Структура config.json
* `vk_token` - token бота-сообщества в ВКонтакте
* `mongo_connect` - [строка для подключения](mongodb+srv://msiet5wVdc5fh3AS:<password>@schedulebot.xredu.mongodb.net/<dbname>?retryWrites=true&w=majority) к MongoDB
* `admin_id` - ID страницы, которая будет считаться администратором. Нужно для управляющих команд.


Бесплатно захостить: heroku.com, бесплатный MongoDB хостинг: mongodb.com
