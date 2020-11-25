# # -*- coding: utf-8 -*-
import telebot
import flask
import requests
import time
import json
from flask import Flask
from flask import request
import rasa
from rasa.core.agent import Agent
from rasa.core import interpreter
from rasa.core.interpreter import RasaNLUInterpreter
from rasa.core.utils import EndpointConfig
import asyncio
import urllib.request
import re
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
import config

bot = telebot.TeleBot(config.TOKEN)
bot.remove_webhook()
bot.set_webhook(config.URL)
action_endpoint = config.ACTION_ENDPOINT
agent1 = Agent.load('./models/20201125-014322.tar.gz', action_endpoint=EndpointConfig(action_endpoint))


def classify(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_batch = np.expand_dims(img_array, axis=0)
    img_preprocessed = preprocess_input(img_batch)
    model = tf.keras.models.load_model('./models/resnet50.h5')
    prediction = model.predict(img_preprocessed)
    return decode_predictions(prediction, top=3)[0]


async def process(agent, msg):
    output = await agent.handle_text(msg)
    return output[0]['text']


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def receive_update():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return {"ok": True}


@bot.message_handler(content_types=['text'])
def default_command(message):
    bot.send_message(message.chat.id, asyncio.run(process(agent1, message.text)))


@bot.message_handler(commands=['start', 'help'])
def command_help(message):
    bot.reply_to(message, "Hello, did someone call for help?")


@bot.message_handler(content_types=['audio', 'video', 'document', 'location', 'contact', 'sticker'])
def default_command(message):
    bot.reply_to(message, "Hi, I am a dog recognizer bot."
                          "Send me a photo of the dog and I will tell you its breed!")


@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    try:
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        file_path = file_info.file_path
        photo_url = f'https://api.telegram.org/file/bot{config.TOKEN}/{file_path}'
        bot.send_message(message.chat.id, 'wait please!')
        photo_name = re.findall(r'\/(\w+)\.', file_path)[0]
        urllib.request.urlretrieve(photo_url, photo_name)
        predict = str(classify(f"./{photo_name}"))

        bot.send_message(message.chat.id, predict)
    except Exception as e:
        bot.reply_to(message, e)


if __name__ == "__main__":
    app.run(host="flask", port=5000)
