from aiogram import Bot, types
from aiogram import Dispatcher 

KEY_API = '5233217036:AAGZ5bccSihk2yLmY2NSECS5YN7FOeA9XlI'
bot = Bot(token=KEY_API, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)