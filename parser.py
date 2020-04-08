import mysql.connector
from bs4 import BeautifulSoup

bd = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='root',
    database='testdatabase',
)

mycursor = bd.cursor()

with open("html.txt", "r", encoding='utf-8') as f:
    x = f.read()
    soup = BeautifulSoup(   x, 'lxml')
    for a in soup.find_all('a', href=True, title=True):
        print("Found the URL:", a['href'], a['title'])
        try:
            mycursor.execute('INSERT INTO datasets(url, nick, status) VALUES (%s, %s, %s)', (a['href'], a['title'], '-', ))
        except:
            print("Уже есть в базе данных:", a['href'], a['title'])

    bd.commit()

