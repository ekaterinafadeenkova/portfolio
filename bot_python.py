
import telebot
import json
import requests
import datetime
import threading
import random
from telebot import types
from giphy import get_gif_by_name
from DataBaseUtils import change_subscription_by_id
from weather import get_weather
from kanye import get_kanye_quote
from scheduler import send_random_gif_at_18_00

#вставляем наш токен
bot = telebot.TeleBot('7061213881:AAGLGGKW5mWHlE8eVFWMavj0wGXt94mXjcA')

#сообщение-приветствие, поясняющее функции бота
hello = '''
Привет! Я -  бот для домашнего задания Фадеенковой Екатерины.

Вот команды, которые я умею выполнять: 
/name - запомню Ваши ФИО
/find_gif - найду гифку по вашему запросу
/subscription - подключу рассылку случайной гифки, при повторном нажатии отключу (сработает только после регистрации /name)
/weather - расскажу все о погоде в Вашем городе
/kanye -  отправлю случайную цитату Канье Уэста
/dinner - придумаю блюдо на ужин
/emoji - отправлю случайное эмодзи
/flip - подброшу монетку и покажу результат
/help- снова покажу все команды
'''

help_message = '''
/name - запомню Ваши ФИО
/find_gif - найду гифку по вашему запросу
/subscription - подключу рассылку случайной гифки, при повторном нажатии отключу (сработает только после регистрации /name)
/weather - расскажу все о погоде в Вашем городе
/kanye -  отправлю случайную цитату Канье Уэста
/dinner - придумаю блюдо на ужин
/emoji - отправлю случайное эмодзи
/flip - подброшу монетку и покажу результат
/help- снова покажу все команды
'''

# Создаём отдельный поток для планировщика
thread_scheduler = threading.Thread(target=send_random_gif_at_18_00, args=(bot,))
# Запускаем поток
thread_scheduler.start()

# --------------------------------------------------------
# Handler-ы для команд
# --------------------------------------------------------

# Объявляем словарь, где будем хранить данные о пользователях
user_data = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, hello)

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def start(message):
    bot.send_message(message.chat.id, help_message)

# Обработчик команды /name
@bot.message_handler(commands=['name'])
def name(message):
    # Очищаем данные о пользователе
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, 'Введите имя')
    # переходим к следующему шагу
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_data[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, 'Введите отчество')
    bot.register_next_step_handler(message, get_fathername)

def get_fathername(message):
    user_data[message.chat.id]['fathername'] = message.text
    bot.send_message(message.chat.id, 'Введите фамилию')
    bot.register_next_step_handler(message, get_surname)

def get_surname(message):
    user_data[message.chat.id]['surname'] = message.text

    # Сохраняем данные о пользователе в файл
    with open('user_data.json', 'w') as f:
        json.dump(user_data, f)

    # подключаем кнопки с использованием inline-клавиатуры
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_yes, key_no)
    # выводим фио, спрашиваем все ли верно (под вопросом кнопки да,нет)
    question = 'Все верно? : ' + user_data[message.chat.id]['surname'] + ' ' + user_data[message.chat.id][
        'name'] + ' ' + user_data[message.chat.id]['fathername']
    bot.send_message(message.chat.id, text=question, reply_markup=keyboard)

# обработчик команды find_gif
@bot.message_handler(commands=['find_gif'])
def find_gif_handler(message):
    bot.send_message(message.from_user.id, "Введите слово или словосочетание для поиска гифки")
    bot.register_next_step_handler(message, get_find_name)

# функция поиска для гифки
def get_find_name(message):
    bot.send_message(message.from_user.id, f"Ваша гифка:")
    link = get_gif_by_name(message.text)
    bot.send_animation(message.from_user.id, link)
    
# Обработчик команды subscription
@bot.message_handler(commands=['subscription'])
def subscription_handler(message):
    status = change_subscription_by_id(message.from_user.id)
    bot.send_message(message.from_user.id, f"Ваш статус подписки был изменён на: {status}")
    send_random_gif_at_18_00(bot)

# обработчик команды weather
@bot.message_handler(commands=['weather'])
def ask_city(message):
    bot.send_message(message.chat.id, "Введите название города:")
    bot.register_next_step_handler(message, get_weather_by_city)

# функция распаковки данных из фукции get_weather
def get_weather_by_city(message):
    city = message.text
    weather_data = get_weather(city)
    
    if 'main' in weather_data and 'temp' in weather_data['main'] and 'weather' in weather_data and len(weather_data['weather']) > 0 and 'description' in weather_data['weather'][0]:
        temperature = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        wind_speed = weather_data['wind']['speed']
        
        description = weather_data['weather'][0]['description']
        
        bot.send_message(message.chat.id, f"Погода в городе {city}: {description.capitalize()}\n"
                                          f"Температура: {temperature}°C\n"
                                          f"Ощущается как: {feels_like}°C\n"
                                          f"Скорость ветра: {wind_speed} м/с\n")
    else:
        bot.send_message(message.chat.id, "Извините, не удалось получить информацию о погоде для указанного города.")

# обработчик команды kanye
@bot.message_handler(commands=['kanye'])
def dog_fact_handler(message):
    quote = get_kanye_quote()
    bot.send_message(message.chat.id, quote)

# обработчик команды dinner
@bot.message_handler(commands=['dinner'])
def send_recipe(message):
    try:
        with open('dinner.txt', 'r', encoding='utf-8') as file:
            recipes = file.read().split('\n\n')  # Разделяем рецепты по двойному переносу строки
            random_recipe = random.choice(recipes).strip()  # Выбираем случайный рецепт
            bot.send_message(message.chat.id, f"Попробуйте приготовить:\n{random_recipe}")
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Файл с рецептами не найден.")

# обработчик команды emoji
@bot.message_handler(commands=['emoji'])
def send_random_emoji(message):
    # Список эмодзи 
    emoji_list = ["💄", "\U0001F60E", "👑", "😋", "💋"]
    # Отправляем случайное эмодзи из списка
    random_emoji = random.choice(emoji_list)
    bot.send_message(message.chat.id, random_emoji)

#обработчик команды flip
@bot.message_handler(commands=['flip'])
def flip_coin(message):
    # случайно выбираем из двух
    result = random.choice(["Орел", "Решка"])
    bot.send_message(message.chat.id, f"Выпало: {result}")

#проверяем есть ли пользователь в нашем файле с информацией о клиентах
def check_client_in_db(user_id):
        with open('user_data.json', 'r') as file:
            for line in file:
                data = line.strip().split(' ')
                if int(data[0]) == user_id:
                    return True
        return False
  
# --------------------------------------------------------
# Callback-и для Inline markup
# --------------------------------------------------------

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # выводим ответы на кноки клавиатуры
    if call.data == "yes": 
        bot.send_message(call.message.chat.id, 'Записано')
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Попробуйте еще раз /name')

# зацикливаем бота
bot.infinity_polling(none_stop=True)




