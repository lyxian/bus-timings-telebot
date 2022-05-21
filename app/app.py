from flask import Flask, request
import threading
import telebot
import time
import sys
import os

from bot import createBot

if len(sys.argv) == 2:
    DEBUG_MODE = eval(sys.argv[1])
else:
    DEBUG_MODE = True

app = Flask(__name__)
bot = createBot()

weburl = os.getenv("PUBLIC_URL") + bot.token

print(weburl)

@app.route("/stop")
def stop():
    shutdown_hook = request.environ.get("werkzeug.server.shutdown")
    try:
        shutdown_hook()
        print("--End--")
    except:
        pass

@app.route("/" + bot.token, methods=["POST"])
def getMessage():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return "!", 200

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        bot.remove_webhook()
        print("Setting webhook...")
        try:
            bot.set_webhook(url=weburl)
            return "Webhook set!", 200
        except:
            return "Webhook not set...Try again...", 400
    elif request.method == "POST":
        print("Wating...")
        return "!", 200

def start():
    bot.remove_webhook()
    time.sleep(2)
    print("Setting webhook...", end=" ")
    try:
        bot.set_webhook(url=weburl)
        print("Webhook set!")
        return "Webhook set!"
    except Exception as e:
        msg = "Webhook not set...Try again..."
        print(f'Error={e}\n{msg}')
        return

if __name__ == "__main__":
    # start()
    startThread = threading.Thread(target=start, daemon=True)
    startThread.start() # .join()
    # time.sleep(1)
    app.run(debug=DEBUG_MODE, host="0.0.0.0", port=int(os.environ.get("PORT", 5005)))