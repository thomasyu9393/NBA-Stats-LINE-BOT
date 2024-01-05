from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
import configparser

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'Channel_Access_Token'))
handler = WebhookHandler(config.get('line-bot', 'Channel_Secret'))

from app import routes, main
