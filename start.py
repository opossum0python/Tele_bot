import mysql.connector
import time
import telebot
import threading
from telebot import types


bd = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='root',
    database='testdatabase',
)
mycursor = bd.cursor()
bot = telebot.TeleBot('') # Сюда вписать токен телеграмм-бота
database_reset = True
send_message = True
messages = []
threading_list = []

class StartTime:
    """
    Данный класс предназначен для функции start_send_message
    это костыль для обновления таймера, не знал как лучше реализовать
    """
    def __init__(self):
        self._start_time = time.monotonic()

    def update(self):
        self._start_time = time.monotonic()

    def time(self):
        return self._start_time

def database_user_reset():
    """
    Сие функция создана для обнуления количества запросов юзера, запускается в отдельном потоке
    при завершении основного цикла, завершается изменением data_reset = False
    :return:
    """
    mycursor.execute("UPDATE user SET cheak_T=0, cheak_N=0")
    print('база данных обновлена')

    start_time_reset = time.monotonic()
    while database_reset:
        if time.monotonic() - start_time_reset >= 3600:
            try:
                mycursor.execute("UPDATE user SET cheak_T=0, cheak_N=0")
                print('база данных обновлена', database_reset)
            except:
                print('Что то с доступом к базе даных')
        else:
            time.sleep(10)

def send_db(first_name, username, id):
    """
    сие функция создана для того что бы добавлять пользователей в базу данных
    :param first_name: имя пользователя
    :param username: ссылка на пользователя
    :param id: id пользователя
    :return:
    """
    try:
        mycursor.execute('INSERT INTO user(first_name, username, id, cheak_N, cheak_T) VALUES (%s, %s, %s, 0, 0)', (first_name, username, id,))
        bd.commit()
        print('тебя добавили в бд')
    except:
        print('Ты есть в бд')

def select_T():
    """
    Данная функция предназначена для запроса к базе данных к таблице datasets
    в SQL запросе возвращается Последняя строка, которая запрашивалась от юзеров
    в которой столбец статус == '-', что означает что ролик не посмотрен и остается в базе
    :return: Стока с SQL запроса
    """
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
    """
    Данная функция предназначена для запроса к базе данных к таблице datasets
    в SQL запросе возвращается Последняя строка, которая запрашивалась от юзеров
    в которой столбец статус == '+', что означает что ролик проверен и составлено описани
    :return: Стока с SQL запроса
    """
    mycursor.execute("SELECT url, nick, status, thesis datacheak FROM datasets WHERE status='+' ORDER BY datacheak ASC LIMIT 1")
    return_ = 'Жалобы кидать на сие видео: \n\n'
    for x in mycursor:
        return_ += 'https://www.youtube.com/' + x[0] + '\n\n\n' + str(x[1])+'\n\n'+ x[3]
        mycursor.execute("UPDATE datasets SET datacheak=CURRENT_TIMESTAMP() WHERE url='" + x[0] + "'")
        bd.commit()
    return return_

def cheak_T(id):
    """
    данная функция проверяет пользователя на количество запросов в столбце cheak_T
     и в случае, если результат запроса недостаточно мал, увеличиваает его на один
     проверка на возможность попрсить ссылку на видео, которое надо посмотреть и составить описание
    :param id: id пользователя
    :return: bool
    """
    mycursor.execute("SELECT cheak_T FROM user WHERE id={0}".format(str(id)))
    for attemp in mycursor:
        if attemp[0] >= 4:
            return False
        mycursor.execute("UPDATE user SET cheak_T=" + str(attemp[0] + 1) + " WHERE id = " + str(id))
        return True

def cheak_N(id):
    """
    данная функция проверяет пользователя на количество запросов в столбце cheak_T
     и в случае, если результат запроса недостаточно мал, увеличиваает его на один
     проверка на возможность попрсить ссылку на видео, на котоное надо кинуть жалобу
    :param id: id пользователя
    :return: bool
    """
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

def message_send(messages):
    """
    Сие функция предназначена для отправки ответных сообений
    на вход поступает массив сосотоящий из массивов
    0 индеккс == id пользователя
    1 индекс == Тексту сообщения
    :param messages:
    :return:
    """
    print(messages)
    for data_message in messages:
        print(data_message)
        if data_message[1] == 'Что я такое':
            bot.send_message(data_message[0], "Дорогой друг, я бот который предназачен для проекта чистый ютуб")
        elif data_message[1] == 'Обратная связь':
            bot.send_message(data_message[0], "Тут ссылки на админов")
        elif data_message[1] == 'Каналы':
            bot.send_message(data_message[0], "Тут ссылки на каналы")
        elif data_message[1] == 'Чат':
            bot.send_message(data_message[0], "Тут ссылка на канал В телеге")
        elif data_message[1] == 'Жалобы':
            if cheak_T(data_message[0]):
                text_select_T = select_T()
                bot.send_message(data_message[0], text_select_T)
        elif data_message[1] == 'Смотреть':
            if cheak_N(data_message[0]):
                text_select_N = select_N()
                bot.send_message(data_message[0], text_select_N)
        time.sleep(0.5)

@bot.message_handler(content_types=['text'])
def message_analysis(message):
    """
    данная функция будет слушать все входящие сообщения и записывать результаты в массив
    :param message:
    :return:
    """
    if message.chat.type == 'private':
        if message.text == 'Что я такое':
            messages.append([message.chat.id, message.text])
        elif message.text == 'Обратная связь':
            messages.append([message.chat.id, message.text])
        elif message.text == 'Каналы':
            messages.append([message.chat.id, message.text])
        elif message.text == 'Чат':
            messages.append([message.chat.id, message.text])
        elif message.text == 'Жалобы':
            messages.append([message.chat.id, message.text])
        elif message.text == 'Смотреть':
            messages.append([message.chat.id, message.text])

def start_send_messege():
    """
    Данная функция выполняется в отдельном потоке, она запускает другую функцию, с определенным временем
     с определенным таймингом
    :return:
    """
    start_time = StartTime()
    while send_message:
        if time.monotonic() - start_time.time() >= 10:
            thread = threading.Thread(target=message_send, args=([messages]))
            threading_list.append(thread)
            thread.start()
            print('Поток на отправку сообщений запущен')
            start_time.update()
            messages.clear()
        time.sleep(5)


thread_data_base_reset = threading.Thread(target=database_user_reset)
threading_list.append(thread_data_base_reset)
thread_data_base_reset.start()

thread_start_send_message = threading.Thread(target=start_send_messege)
threading_list.append(thread_start_send_message)
thread_start_send_message.start()

for i in range(10):
    try:
        bot.polling(none_stop=True)
    except:
        pass

database_reset = False
send_message = False

for thread in threading_list:
    thread.join()

print('Скрипт завершен')