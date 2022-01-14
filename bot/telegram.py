import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.environ['API_TOKEN']
API_URL = os.environ['API_URL']

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['prediction'])
async def add_prediction(message: types.Message):
    _, confidence, prediction = message.text.split(' ', 2)
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json={
            'user': message.from_user.username,
            'description': prediction,
            'confidence': confidence,
        }) as r:
            await message.reply(await r.json())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)