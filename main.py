import logging

from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ConversationHandler, CommandHandler

from aiogram import Bot, Dispatcher

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

BOT_TOKEN = '7116319751:AAGoO4z5EKLLt8cML5seEGlhBFNF7_5K6ow'
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)

Base = declarative_base()


class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True)
    photo_id = Column(String)
    caption = Column(Integer)


engine = create_engine('sqlite:///data.db')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


async def help(update, context):
    await update.message.reply_text(
        "Этот бот может создавать заметки-изображения.\n"
        "Также, он может отправлять напоминания")
    return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


async def start(update, context):
    reply_keyboard = [['Создать заметку', 'Список заметок'],
                      ['Открыть заметку', 'Очистить заметки']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Что Вы хотите сделать?", reply_markup=markup)
    return 1


async def get_name(update, context):
    session = Session()
    context.user_data['state'] = update.message.text

    if context.user_data['state'] == 'Создать заметку':
        await update.message.reply_text("Отправьте фотографию для заметки с её названием в подписи")

    elif context.user_data['state'] == 'Открыть заметку':
        query = select(Photo.caption)
        list_of_notes = session.execute(query).fetchall()
        ans = list(filter(lambda y: y is not None, map(lambda x: x[0], list_of_notes)))
        if len(ans) > 0:
            await update.message.reply_text('Введите название заметки')
        else:
            await update.message.reply_text('Заметок нет')
            return 1

    elif context.user_data['state'] == 'Список заметок':
        query = select(Photo.caption)
        list_of_notes = session.execute(query).fetchall()
        ans = list(filter(lambda y: y is not None, map(lambda x: x[0], list_of_notes)))
        if len(ans) > 0:
            await update.message.reply_text('\n'.join(ans))
        else:
            await update.message.reply_text('Заметок нет')
        session.close()
        return 1

    elif context.user_data['state'] == 'Очистить заметки':
        session = Session()
        session.query(Photo).delete()
        session.commit()
        await update.message.reply_text('Заметки успешно удалены')
        session.close()
        return 1

    elif context.user_data['state'] == 'Создать напоминание':
        await update.message.reply_text('Введите текст напоминания')

    else:
        await update.message.reply_text('Выберите один из вариантов')
        return 1
    return 2


async def respond(update, context):
    session = Session()

    if context.user_data['state'] == 'Создать заметку':
        new_note = Photo(photo_id=update.message.photo[-1].file_id, caption=update.message.caption)
        if update.message.caption is None:
            await update.message.reply_text('Для создания заметки необходима подпись. Отправьте изображение ещё раз')
            return 2
        else:
            session.add(new_note)
            session.commit()
            await update.message.reply_text('Заметка "{}" успешно сохранена!'.format(update.message.caption))

    elif context.user_data['state'] == 'Открыть заметку':
        note = session.query(Photo).filter_by(caption=update.message.text).order_by(-Photo.id).first()
        if note is None:
            await update.message.reply_text('Такой записки не существет. Проверьте правильность написания названия')
            return 2
        else:
            await update.message.reply_photo(note.photo_id)

    elif context.user_data['state'] == 'Создать напоминание':
        await update.message.reply_text('Ф')

    session.close()
    return 1


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
