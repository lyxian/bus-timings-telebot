import telebot
import logging

from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from utils import getToken, getCurrLoc, loadBusStops, getHaversineDistance, getFormattedMessage, generateMap, removeMapFile

def createBot():
    TOKEN = getToken()

    bot = telebot.TeleBot(token=TOKEN)
    telebot.logger.setLevel(logging.DEBUG)

    @bot.message_handler(commands=['start', 'help'])
    def _start(message):
        text = 'Please use markup keyboard to start app'
        bot.send_message(message.chat.id, text, reply_markup=createMarkup())

    @bot.message_handler(content_types=['location'])
    def _message(message):
        bot.delete_message(message.chat.id, message.id)
        if message.location:
            setRadius = 0.3 # (km)
            busLimit = 100
            urlOnly = False
            currLoc = getCurrLoc([message.location.latitude, message.location.longitude])
            busStops = sorted([i for i in loadBusStops(currLoc) if 'latitude' in i.keys() and getHaversineDistance(*currLoc, i['latitude'], i['longitude']) <= setRadius], key=lambda x: x['distance'], reverse=True)[:busLimit]
            text = getFormattedMessage(busStops[:busLimit], setRadius)
            imagePath = generateMap(currLoc, busStops, urlOnly)
            if not urlOnly:
                with open('map.png', 'rb') as file:
                    imageData = file.read()
                removeMapFile(imagePath)
                imagePath = imageData
            bot.send_message(message.chat.id, text, parse_mode='HTML')
            bot.send_photo(chat_id=message.chat.id, photo=imagePath, parse_mode='HTML')
            # print(text)
        else:
            bot.send_message(message.chat.id, 'Location not received, please enable correct permissions and try again..')

    def createMarkup():
        markup = ReplyKeyboardMarkup(input_field_placeholder='test')
        markup.add(KeyboardButton('start', request_location=True))
        return markup

    return bot

if __name__ == "__main__":
    bot = createBot()