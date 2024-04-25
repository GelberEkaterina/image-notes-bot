import logging
import asyncio
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ConversationHandler, CommandHandler
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import Message
import aiohttp
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os

BOT_TOKEN = '7116319751:AAGoO4z5EKLLt8cML5seEGlhBFNF7_5K6ow'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
logger = logging.getLogger(__name__)

Base = declarative_base()


class MediaIds(Base):
    __tablename__ = 'Media ids'
    id = Column(Integer, primary_key=True)
    file_id = Column(String(255))
    filename = Column(String(255))


engine = create_engine(f'sqlite:///data.db')

if not os.path.isfile(f'./data.db'):
    Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


async def help(update, context):
    await update.message.reply_text(
        "Этот бот может создавать заметки-изображения.\n"
        "Также, он может отправлять напоминания")
    return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


async def start(update, context):
    reply_keyboard = [['Создать заметку'],
                      ['Открыть заметку', 'Создать напоминание']]
    markup = ReplyKeyboardMarkup(reply_keyboard)
    await update.message.reply_text("Что Вы хотите сделать?", reply_markup=markup)
    return 1


async def get_name(update, context):
    context.user_data['state'] = update.message.text
    if context.user_data['state'] == 'Создать заметку':
        await update.message.reply_text("Отправьте фотографию для заметки с её названием в подписи")
    elif context.user_data['state'] == 'Открыть заметку':
        await update.message.reply_text('Введите название файла')
    elif context.user_data['state'] == 'Создать напоминание':
        await update.message.reply_text('Введите текст напоминания')
    else:
        await update.message.reply_text('Выберите один из вариантов')
        return 1
    return 2


async def respond(update, context):
    if context.user_data['state'] == 'Создать заметку':
        await update.message.reply_photo(update.message.photo[-1].file_id, caption=update.message.caption)
    if context.user_data['state'] == 'Открыть заметку':
        await update.message.reply_text()
    if context.user_data['state'] == 'Создать напоминание':
        await update.message.reply_text('Ф')
    return ConversationHandler.END


async def view_notes(message: types.Message, context):
    await message.reply("Какую заметку вы бы хотели посмотреть?")


async def get_response(url, params):
    logger.info(f"getting {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


async def reminder(message: types.Message):
    await message.reply("Введите текст напоминания")


@dp.message(F.photo)
async def echo_gif(message: Message):
    await message.reply_photo(message.photo[-1].file_id)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", help))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, get_name)],
            2: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, respond)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.run_polling()


if __name__ == "__main__":
    main()
