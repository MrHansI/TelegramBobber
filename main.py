import smtplib
import time
from twilio.rest import Client
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
from config import TGToken

TOKEN = TGToken

def send_sms(to_number, text):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    username = "example@gmail.com"
    password = "password"
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(username, password)
    message = f"Subject: Сообщение\n\n{text}"
    server.sendmail(username, to_number, message)
    server.quit()

def make_call(to_number):
    account_sid = "SID"
    auth_token = "Token"
    client = Client(account_sid, auth_token)
    call = client.calls.create(
        to=to_number,
        from_="+14151234567",
        url="http://demo.twilio.com/docs/voice.xml"
    )

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот для отправки SMS и совершения звонков")

def echo(update, context):
    if len(context.args) == 1 and context.args[0].isdigit():
        phone_number = context.args[0]
        reply_keyboard = [['СМС-бомбер', 'Спам-звонок']]
        context.user_data['phone_number'] = phone_number
        context.user_data['spam_type'] = None
        context.user_data['usage_count'] = 0
        update.message.reply_text("Выбери способ спама:", reply_markup=reply_keyboard)
    elif update.message.text in ['СМС-бомбер', 'Спам-звонок']:
        spam_type = update.message.text
        context.user_data['spam_type'] = spam_type
        if context.user_data['usage_count'] == 0:
            context.user_data['usage_count'] += 1
            update.message.reply_text(f"{spam_type} для номера {context.user_data['phone_number']} запущен")
            main(context.user_data['phone_number'], spam_type)
        else:
            reply_keyboard = [['Оплатить', 'Отмена']]
            update.message.reply_text("Оплати дальнейшее использование", reply_markup=reply_keyboard)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Некорректный ввод")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Отправь /start, чтобы начать использование бота. Подробнее на сайте: https://mybotwebsite.com")

def main(to_number, spam_type):
    message_text = "Привет, это тест!"
    call_duration_sec = 60
    while True:
        if spam_type == "СМС-бомбер":
            send_sms(to_number, message_text)
        elif spam_type == "Спам-звонок":
            make_call(to_number)
        time.sleep(1)

updater = Updater(token=TOKEN, use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(MessageHandler(filters.text & ~filters.command, echo))

updater.start_polling()
updater.idle()
