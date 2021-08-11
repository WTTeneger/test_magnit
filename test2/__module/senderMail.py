from __module.theards import thread
import os

import smtplib                                      # Импортируем библиотеку по работе с SMTP
# Добавляем необходимые подклассы - MIME-типы
from email.mime.multipart import MIMEMultipart      # Многокомпонентный объект
from email.mime.text import MIMEText   
html_message_1 = open('test2/__html_mail/message1.html', encoding='utf-8').read()


@thread
def SendMessageMail(ToMail, name_, text_):
    addr_from = "ting@ru-ting.ru"                # Адресат
    password  = "TESTPASSMAIL12"                 # Пароль
    addr_to   = ToMail                           # Получатель

    msg = MIMEMultipart()                               # Создаем сообщение
    msg['From']    = addr_from                          # Адресат
    msg['To']      = addr_to                            # Получатель
    msg['Subject'] = 'TING Уведомления'                   # Тема сообщения

    body = ""
    msg.attach(MIMEText(body, 'plain'))                 # Добавляем в сообщение текст

    
    textHtml = html_message_1.replace('{name}', name_).replace("{text}",text_)
    
    msg.attach(MIMEText(textHtml, 'html', 'utf-8'))         # Добавляем в сообщение HTML-фрагмент

    server = smtplib.SMTP('mail.hosting.reg.ru', 587)           # Создаем объект SMTP
    server.starttls()                                   # Начинаем шифрованный обмен по TLS
    server.login(addr_from, password)                   # Получаем доступ
    server.send_message(msg)                            # Отправляем сообщение
    server.quit()                                       # Выходим


