import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from peewee import *

import telebot
from telebot import types
from models import *
import config

bot = telebot.TeleBot(config.token)
app = Flask(__name__)
app.config.from_object(__name__)

import webhook
import webtest
import dataloader


@app.before_request
def _db_connect():
    DB.connect()

@app.teardown_request
def _db_close(exc):
    if not DB.is_closed():
        DB.close()

DB.create_tables([Campaign, ChatUser, CampaignSend, ChatFunnel, ChatGeo, ChatFilter, ChatReplic, OffersBeta, Offers, OffersPrice, OffersPicTxt, StoreDiscounts], safe=True)


@app.route('/')
def index():
    return 'Index'


@bot.message_handler(regexp="(лавное|Назад|назад)")
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Каталог', 'Магазины')
    markup.row('Рекомендации', 'Акции')
    bot.send_message(message.chat.id, "Пятница уже не за горами!", reply_markup=markup)

    #bot.reply_to(message, ("Привет.\nЯ бот"))

if __name__ == '__main__':
    app.run(debug=True)
