import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import Message

BOT_TOKEN = '7116319751:AAGoO4z5EKLLt8cML5seEGlhBFNF7_5K6ow'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
logger = logging.getLogger(__name__)


@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.reply(
        "Этот бот может создавать заметки-изображения.\n"
        "Также, он может отправлять напоминания и выводить карту места по названию")


@dp.message(Command("start"))
async def start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Создать заметку")],
        [types.KeyboardButton(text="Посмотреть заметки")],
        [types.KeyboardButton(text="Посмотреть карту места")],
        [types.KeyboardButton(text="Создать напоминание")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer("Что Вы хотите сделать?", reply_markup=keyboard)


@dp.message(F.text.lower() == "создать заметку")
async def create_note(message: types.Message, context):
    await message.reply("Введите название заметки")


@dp.message(F.text.lower() == "посмотреть заметки")
async def without_puree(message: types.Message):
    await message.reply("Какую заметку вы бы хотели посмотреть?")


@dp.message(F.text.lower() == "посмотреть место")
async def place(message: types.Message):
    await message.reply("Введите название места")


@dp.message(F.text.lower() == "создать напоминание")
async def reminder(message: types.Message):
    await message.reply("Введите текст напоминания")


@dp.message(F.photo)
async def echo_gif(message: Message):
    await message.reply_photo(message.photo[-1].file_id)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
