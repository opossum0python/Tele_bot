import mysql.connector
import time
import telebot
import random
from datetime import datetime
from telebot import types


bd = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='root',
    database='testdatabase',
)
mycursor = bd.cursor()

bot = telebot.TeleBot('1193978058:AAFpqSt-celG35PfsE_0kxHrVqM6FUcz_zM')


def select_T():
    mycursor.execute("SELECT url, nick, status, datacheak FROM datasets WHERE status='-' ORDER BY datacheak ASC LIMIT 1")
    return_ = 'Посмотри эти видео и отпишись нам: \n\n'
    for x in mycursor:
        return_ += 'https://www.youtube.com/' + x[0]+ '\n' + str(x[1]) + '\n\n'
        print(x[3])
        mycursor.execute("UPDATE datasets SET datacheak=CURRENT_TIMESTAMP() WHERE url='" + x[0] + "'" )
        bd.commit()
    print(return_)
    return return_

def select_N():
    mycursor.execute("SELECT url, nick, status, thesis datacheak FROM datasets WHERE status='+' ORDER BY datacheak ASC LIMIT 1")
    return_ = 'Жалобы кидать на сие видео: \n\n'
    for x in mycursor:
        return_ += 'https://www.youtube.com/' + x[0] + '\n\n\n' + str(x[1])+'\n\n'+ x[3]
        mycursor.execute("UPDATE datasets SET datacheak=CURRENT_TIMESTAMP() WHERE url='" + x[0] + "'")
        bd.commit()
    return return_

def cheak_T(id):
    mycursor.execute("SELECT cheak_T FROM user WHERE id={0}".format(str(id)))
    for attemp in mycursor:
        if attemp[0] >= 4:
            return False
        mycursor.execute("UPDATE user SET cheak_T=" + str(attemp[0] + 1) + " WHERE id = " + str(id))
        return True

def cheak_N(id):
    mycursor.execute("SELECT cheak_N FROM user WHERE id={0}".format(str(id)))
    for attemp in mycursor:
        if attemp[0] >= 4:
            return False
        mycursor.execute("UPDATE user SET cheak_N=" + str(attemp[0] + 1) + " WHERE id = " + str(id))
        return True

@bot.message_handler(commands=['start'])
def welcome(message):
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Что я такое")
    item2 = types.KeyboardButton("Обратная связь")
    item3 = types.KeyboardButton("Каналы")
    item4 = types.KeyboardButton("Чат")
    item5 = types.KeyboardButton("Жалобы")
    item6 = types.KeyboardButton("Смотреть")
    markup.add(item1, item2, item3, item4, item5, item6)

    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ бот проекта быти - 'Чистый ютуб'. У Меня ты можешь получить доступ к видео, на которые можно кинуть жалобу + можешь помочь нам в отсмотре видео и поиске неугодных правилам ютуба".format(
                         message.from_user),
                     parse_mode='html', reply_markup=markup)

    send_db(message.from_user.first_name, message.from_user.username, message.from_user.id)

@bot.message_handler(content_types=['text'])
def lalala(message):
    if message.chat.type == 'private':
        if message.text == 'Что я такое':
            bot.send_message(message.chat.id, "Дорогой друг, я бот который предназачен для проекта чистый ютуб")
        elif message.text == 'Обратная связь':
            bot.send_message(message.chat.id, "Тут ссылки на админов")
        elif message.text == 'Каналы':
            bot.send_message(message.chat.id, "Тут ссылки на каналы")
        elif message.text == 'Чат':
            bot.send_message(message.chat.id, "Тут ссылка на канал В телеге")
        elif message.text == 'Жалобы':
            if cheak_T(message.from_user.id):
                text_select_T = select_T()
                bot.send_message(message.chat.id, text_select_T)
        elif message.text == 'Смотреть':
            if cheak_N(message.from_user.id):
                text_select_N = select_N()
                bot.send_message(message.chat.id, text_select_N)
    time.sleep(1)

while True:
    try:
        bot.polling(none_stop=True)
    except:
        time.sleep(10)