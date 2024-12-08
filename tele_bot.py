import json
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os
import time

TOKEN = '7877336539:AAEYtg3Go8yNf2px-fMFg-66i0fdMwHMLdA'
bot = TeleBot(token=TOKEN)

# Load data from file or initialize an empty dictionary
try:
    with open("final_data.json", "r", encoding='utf-8') as file:
        final_data = json.load(file)
except FileNotFoundError:
    final_data = {}
except json.decoder.JSONDecodeError:
    final_data = {}


# Function to save data to the JSON file
def save_data():
    with open("final_data.json", "w", encoding='utf-8') as file:
        json.dump(final_data, file, ensure_ascii=False, indent=4)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_photo(message.chat.id, open('police_car.png', 'rb'))
    bot.send_message(
        message.chat.id,
        '''What can this bot do?
Այս Bot- ը նախատեսված է ՃՈ իրավախախտումների մասին տեղեկություններ ստանալու համար :
Դուք կարող եք գրանցել Ձեր մեքենան և ստանալ հաղորդագրություններ նոր իրավախախտումների ժամանակ:''')
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("Գրանցել նոր մեքենա 🚗")
    button2 = KeyboardButton("Տեսնել իմ բոլոր մեքենաները 🏠")
    button3 = KeyboardButton("Վերադառնալ գլխավոր Menu ◀")
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Գրանցել նոր մեքենա 🚗")
def start_registration(message):
    chat_id = message.chat.id
    final_data.setdefault(str(chat_id), {})  # Initialize user data
    msg = bot.send_message(chat_id, "Մուտքագրեք մեքենայի համարանիշը 00XX000 ֆորմատով")
    bot.register_next_step_handler(msg, process_car_number)

def process_car_number(message):
    chat_id = str(message.chat.id)
    car_number = message.text
    final_data[chat_id][car_number] = []  # Initialize car entry
    msg = bot.send_message(chat_id, f"Դուք մուտքագրել եք {car_number} համարանիշը, մուտքագրեք սոցիալական քարտի համարը։")
    bot.register_next_step_handler(msg, process_social_card, car_number)

def process_social_card(message, car_number):
    chat_id = str(message.chat.id)
    social_card = message.text
    final_data[chat_id][car_number].append(social_card)
    msg = bot.send_message(chat_id, f"Դուք մուտքագրել եք {social_card} սոցիալական քարտի համարը, մուտքագրեք վարորդական վկայականի համարը։")
    bot.register_next_step_handler(msg, process_driver_card, car_number)

def process_driver_card(message, car_number):
    chat_id = str(message.chat.id)
    driver_card = message.text
    final_data[chat_id][car_number].append(driver_card)
    msg = bot.send_message(chat_id, f"Դուք մուտքագրել եք {driver_card} վարորդական վկայականի համարը, մուտքագրեք հեռախոսահամարը։")
    bot.register_next_step_handler(msg, process_phone_number, car_number)

def process_phone_number(message, car_number):
    chat_id = str(message.chat.id)
    phone_number = message.text
    final_data[chat_id][car_number].append(phone_number)
    bot.send_message(chat_id, f"Դուք մուտքագրել եք {phone_number} հեռախոսահամարը, Ձեր տվյալները հաջողությամբ գրանցված են համակարգում։")
    save_data()  # Save data to JSON file after registration

@bot.message_handler(func=lambda message: message.text == "Տեսնել իմ բոլոր մեքենաները 🏠")
def show_cars(message):
    chat_id = str(message.chat.id)
    car_data = final_data.get(chat_id, {})
    if not car_data:
        bot.send_message(message.chat.id, "Դուք դեռ չունեք գրանցված մեքենա։")
        return
    
    keyboard = InlineKeyboardMarkup()
    for car_number in car_data:
        button = InlineKeyboardButton(f"{car_number}", callback_data=f"{car_number}")
        keyboard.add(button)
    msg = bot.send_message(message.chat.id, "Ձեր մեքենաները:", reply_markup=keyboard)
    bot.register_next_step_handler(msg, parse_data, car_number)

def parse_data(message, car_number):
    car_number = message.text
    with open('final_data.json', 'r') as file:
        data = json.load(file)
    print(data)
    SOC, PRAVA, HAMAR = data[f"{message.chat.id}"][f"{car_number}"]

    driver = webdriver.Chrome()

    driver.get(url='https://roadpolice.am/hy')
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, '#index_page_steps > div > div > ul > li:nth-child(1) > button > span > span').click()
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, '#psn-va').send_keys(SOC)
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, '#license_number-va').send_keys(PRAVA)
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, '#phone-number').send_keys(HAMAR)
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, '#drivers-login-submit').click()
    time.sleep(5)
    driver.find_element(By.CSS_SELECTOR, 'body > div > header > div > div > div.top-box__bottom-section.clear-fix.pr > nav > ul > li:nth-child(3) > a').click()
    time.sleep(3)
    items = driver.find_elements(By.CLASS_NAME, 'text-underline')
    for i in items:
        bot.send_message(message.chat.id, f'https://viv.police.am/decision/{i.text}', car_number)
    time.sleep(3)

bot.polling()