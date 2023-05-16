import telebot
import markups
import weather
import openweather
from simpleeval import simple_eval
from peewee import *
from datetime import datetime

db = SqliteDatabase('base.sqlite')

class Place(Model):

    id = IntegerField()
    name = TextField()
    address = TextField()

    class Meta:
        database = db
        db_table = "place"

class Event(Model):

    id = IntegerField()
    name = TextField()
    date = DateField()
    place_id = IntegerField()
    

    class Meta:
        database = db
        db_table = "event"




apikeys = {
  "tgbot": "6079005383:AAFo69oDnmwh--6HyABJ8boCyh9lk-juBQc",
  "geocode": "f3f4df44-d21f-4567-a82c-029f3f52127d",
  "oweather": "2fca23578879140a4731ee0eaba9487d"
}


templates = {
'geoposition':
'Отправьте название или геопозицию местности',
'info':
'Автор: Артем Родионов',
             'help':
'Бот позволяет посмотреть список ближайших мероприятий в интересующем месте.',

             'weather':
'''Погода в {place}:
На улице {weather}, температура  {temp} °C
Ветер: {wind} метров с секунду
''',
             'error':
'Поиск не дал результатов'
}


cmds = {'weather': 'Погода',
        'help': 'Помощь',
        'afisha': 'Афиша'}



bot = telebot.TeleBot(apikeys['tgbot'])


@bot.message_handler(commands=['start', 'help'])
def info(msg):
    bot.reply_to(msg, templates['info'], reply_markup=markups.main, parse_mode='MarkDown')


@bot.message_handler(func=lambda msg: msg.text == cmds['help'])
def help(msg):
    bot.reply_to(msg, templates['help'], reply_markup=markups.main, parse_mode='MarkDown')


@bot.message_handler(func=lambda msg: msg.text == cmds['weather'])
def input_weather(msg):
    msg = bot.reply_to(msg, templates['geoposition'], reply_markup=markups.main, parse_mode='MarkDown')
    bot.register_next_step_handler(msg, output_weather)


def output_weather(msg):
    g = weather.weather(apikeys['geocode'])
    if msg.content_type == 'text':
        geocode = g.get_coordinates(msg.text)
        if not geocode['existence']:
            bot.reply_to(msg, templates['error'], parse_mode='MarkDown')
            return
    elif msg.content_type == 'location':
        geocode = g.get_place(msg.location.latitude, msg.location.longitude)
        geocode['lat'], geocode['lon'] = msg.location.latitude, msg.location.longitude
    else:
        bot.reply_to(msg, templates['error'], parse_mode='MarkDown')
        return

    w = openweather.OpenWeather(apikeys['oweather'])
    res = w.weather(geocode['lat'], geocode['lon'])

    text = templates['weather'].format(
        place=geocode['location'], weather=res['weather'][0]['description'],
        temp=res['main']['temp'],  wind=res['wind']['speed'])

    bot.reply_to(msg, text, parse_mode='MarkDown', reply_markup=markups.main)


@bot.message_handler(func=lambda msg: msg.text == cmds['afisha'])
def input_afisha(message):
    getWord = bot.send_message(message.chat.id, "Введите название места")
    bot.register_next_step_handler(getWord, output_afisha)

def output_afisha(msg):
    found_town_id = -1;
    selected_town = 0
    for place in Place.select().where(Place.name == msg.text):
        found_town_id = place.id
        selected_town = place
    if found_town_id == -1:
        bot.reply_to(msg, "Место не найдено", parse_mode='MarkDown')
        return
    return_text = "Ближайшие мероприятия в " + selected_town.name + " по адресу " + selected_town.address + "\n"
    date_now = datetime.now().date()
    for event in Event.select().where(Event.place_id == found_town_id).where(Event.date >= date_now).order_by(Event.date).limit(5):
        return_text += str(event.date) + ", " + event.name + "\n"
    if return_text == "Ближайшие мероприятия в данном месте:\n":
        bot.reply_to(msg, "Мероприятий в " + selected_town.name + " по адресу " + selected_town.addres + " не найдено", parse_mode='MarkDown')
        return

    g = weather.weather(apikeys['geocode'])
    geocode = g.get_coordinates(selected_town.address)
    if not geocode['existence']:
        bot.reply_to(msg, templates['error'], parse_mode='MarkDown')
        return
    w = openweather.OpenWeather(apikeys['oweather'])
    res = w.weather(geocode['lat'], geocode['lon'])

    weather_text = templates['weather'].format(
        place=geocode['location'], weather=res['weather'][0]['description'],
        temp=res['main']['temp'],  wind=res['wind']['speed'])

    return_text += "\nОбратите внимание на погоду в месте назначения:\n" + weather_text

    bot.reply_to(msg, return_text , parse_mode='MarkDown', reply_markup=markups.main)
        


@bot.message_handler()
def err(msg):
    bot.reply_to(msg, "Неизвестная команда. Попробуйте еще раз", reply_markup=markups.main)


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling(none_stop=True)
