from utils import getToken
import telebot
import logging

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def createBot():
    TOKEN = getToken()

    bot = telebot.TeleBot(token=TOKEN)
    telebot.logger.setLevel(logging.DEBUG)

    @bot.message_handler(commands=['start', 'help'])
    def _start(message):
        text = 'Please use markup keyboard to start app'
        bot.send_message(message.chat.id, text, reply_markup=createMarkup())

    @bot.message_handler(func=lambda message: message.text == 'start')
    def _message(message):
        latitude, longitude = [message.location.latitude, message.location.longitude]
        telebot.logging.debug(message)

    def createMarkup():
        markup = ReplyKeyboardMarkup(input_field_placeholder='test')
        markup.add(KeyboardButton('start', request_location=True))
        return markup

    return bot

if __name__ == "__main__":
    bot = createBot()