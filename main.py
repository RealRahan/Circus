import telebot
from telebot.async_telebot import AsyncTeleBot
import asyncio
import requests
import random

bot = AsyncTeleBot("5349158861:AAHDYoxRZ06mgLICouCMXfxKc482tI-_l7Y")

@bot.message_handler(commands=['start'])
async def send_welcome(message):
	await bot.reply_to(message, f"""
اهلا بك
/start - هذة القائمة
/ss - لقطة شاشة لموقع معين
/roll - رمي حجرة النرد
/meme - عرض صورة ميم مع تعليق نصي
""")

@bot.message_handler(commands=["ss"])
async def screenshot(message):
	site = telebot.util.extract_arguments(message.text)
	await bot.send_photo(message.chat.id, photo=f"https://image.thum.io/get/width/1280/crop/720/https://{site}")

@bot.message_handler(commands=["roll"])
async def roll_cmd(message):
 await bot.reply_to(message, random.randint(1, 100))

@bot.message_handler(commands=["meme"])
async def meme_cmd(message):
 r=requests.get("https://some-random-api.ml/meme")
 await bot.reply_to(message, r.json()["caption"])
 await bot.send_photo(message.chat.id, r.json()["image"])
 await bot.send_message(message.chat.id, f"Meme ID ({r.json()['id']})")

asyncio.run(bot.polling())
