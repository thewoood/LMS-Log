import os 
import asyncio
import telebot
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
bot = AsyncTeleBot(TOKEN, parse_mode='MARKDOWN')

@bot.message_handler(commands=['start'])
async def start(message: telebot.types.Message):
    text = f'Type /id to get current chat ID`'
    await bot.reply_to(message, text)

@bot.message_handler(commands=['id'])
async def id(message: telebot.types.Message):
    text = f'Your Chat ID is:\n`{message.chat.id}`'
    await bot.reply_to(message, text)

async def main():
    await bot.set_my_commands([telebot.types.BotCommand('id', 'Get chat ID')])
    await bot.polling()

asyncio.run(main())