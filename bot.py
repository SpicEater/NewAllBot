from spicy import remember, encrypt_data, decrypt_data
import logging
import asyncio
import aiohttp
import telegram
import sqlite3 as sql
import requests
from telegram import Update, helpers, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, ChatInviteLink
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler

## создание логов
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

DB = 'user.db' ##путь к БД

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE): ##оброботчик команды /mute
    chat_id = update.effective_chat.id
    user_name = update.effective_user.name
    user_id = update.effective_user.id
    con = sql.connect(DB)
    with con:
        cur = con.cursor()
        try:
            cur.execute(f"SELECT DISTINCT title FROM user WHERE NOT id_user = '{user_id}' or name = '{user_name}';") ##провекрка в БД
        except:
            await context.bot.send_message(chat_id, "Не нашел вас ни в одном чате.")
            return False
        cur.execute("DELETE FROM user WHERE")
async def add_bot(update: Update, context: ContextTypes.DEFAULT_TYPE): ##оброботчик команды /add_bot
    url = helpers.create_deep_linked_url('spicyeater_bot', "link", group=True)
    url += '&admin=post_messages'
    query = update.callback_query
    try:
        await query.edit_message_text(
            'Нажми на кнопку, чтобы добавить бота',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Ссылка', url=url)], [InlineKeyboardButton(text='Меню', callback_data='hellp')]]))
    except:
        await update.message.reply_text(
            'Нажми на кнопку, чтобы добавить бота',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Ссылка', url=url)], [InlineKeyboardButton(text='Меню', callback_data='hellp')]]))

async def add_people_1(update: Update, context: ContextTypes.DEFAULT_TYPE): ##оброботчик команды /add_people
    user_id= str(update.effective_user.id)
    chat_id = update.effective_chat.id
    user_name = update.effective_user.name
    con = sql.connect(DB)

    with con:
        cur = con.cursor()
        try:
            cur.execute(f"SELECT DISTINCT title FROM user WHERE NOT id_user = '{user_id}' or name = '{user_name}';")##
            # print(cur.fetchall())
        except:
            await context.bot.send_message(chat_id, "Не нашел вас ни в одном чате. Попробуйте перелогиниться, прописав команду /remember в чате")
            return False
        w = []
        for i in cur.fetchall():
            w.append(i[0])
        masage = 'Выберите группу в которую хотите добавить человека'
        button = [[InlineKeyboardButton(i, callback_data=f'add_people_2 {i}')] for i in w] ##

        mark = InlineKeyboardMarkup(button)
        try:
            await update.callback_query.edit_message_text(masage, reply_markup=mark)
        except:
            await update.message.reply_text(masage, reply_markup=mark)

    # await update.message.reply_text("Напиши название группы в которую хочешь ")
async def add_people_2(update: Update, context: ContextTypes.DEFAULT_TYPE): ##оброботчик команды /mute
    args = update.callback_query.data[13::]
    args = [k if k != " " else "_" for k in list(args)]
    args = "".join(args)
    con = sql.connect(DB)

    if args:
        with con:
            cur = con.cursor()
            try:
                cur.execute(f"SELECT DISTINCT id_chat FROM user WHERE title = '{args}';")
                chat = cur.fetchall()
            except:
                await context.bot.send_message(update.effective_chat.id,
                                               "Для того чтобы пригласить когото нужно чтобы хотябы у одного человека были включены уведомления. Попробуйте перелогиниться, прописав команду /remember в чате")
    link = context.bot.link + f'?start={args}_{chat[0][0]}'
    await update.callback_query.edit_message_text(f"Поделитесь этой ссылкой для присоединения других пользователей: {link}", reply_markup =
                                                  InlineKeyboardMarkup([[InlineKeyboardButton(text='Назад', callback_data='start')]]))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): ##оброботчик команды /start
    args = context.args
    user = update.effective_user.name
    user_id = update.effective_user.id

    if args:
        args = args[0].split('_')
        chat = args[1]
        title = args[0]
        if not remember(user, user_id, chat, title):
            await context.bot.send_message(update.effective_chat.id,
                                           "Вы уже состоите в этом чате")
        return
    masage = '⚙️ Меню ⚙️ \n\n' \
             '— /add_people - добавить людей в группу 👥\n'\
            '— /mute - удалить уведомления🔕\n'\
            '— /add_bot - добавить бота  🤖\n'\
            '— /add_tag - добавить тег для уведомления 🔔\n'
    mark = InlineKeyboardMarkup([[InlineKeyboardButton(text='Добавить людей', callback_data='add_people'), InlineKeyboardButton(text='Удалить уведомления', callback_data='mute')],
                                   [InlineKeyboardButton(text='Добавить бота', callback_data='add_bot'), InlineKeyboardButton(text='Добавить тег', callback_data='add_tag')]])
    try:
        await update.callback_query.edit_message_text(masage,reply_markup= mark)
    except:
        await update.message.reply_text(masage, reply_markup=mark)

async def periodic_internet_check(interval_hours): ##запуск команды проверки соеденения
    while True:
        internet_connected = await check_internet_connection()
        if internet_connected:
            logger.info("Интернет-соединение установлено.")
        else:
            logger.warning("Отсутствует интернет-соединение.")

        await asyncio.sleep(interval_hours * 3600)


async def check_internet_connection(): ##проверка соедениния с интернетом
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://www.google.com') as response: ##обращение к google
                return response.status == 200
    except aiohttp.ClientError:
        return False


def main() -> None:
    application = Application.builder().token("6572779723:AAGvYhji-PdqXZWj72E1lrAUjqOMYT5Tz0E").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, pattern='^start$'))

    application.add_handler(MessageHandler(filters.Regex('^/add_people|Добавить людей$'), add_people_1))
    application.add_handler(CallbackQueryHandler(add_people_1, '^add_people$'))

    application.add_handler(CallbackQueryHandler(add_people_2, pattern = 'add_people_2'))

    application.add_handler(MessageHandler(filters.Regex('^/mute|Удалить уведомления$'), add_bot))
    application.add_handler(CallbackQueryHandler(add_bot, '^mute$'))

    application.add_handler(MessageHandler(filters.Regex('^/add_bot|Добавить бота$'), add_bot))
    application.add_handler(CallbackQueryHandler(add_bot, '^add_bot$'))

    application.add_handler(MessageHandler(filters.Regex('^/add_tag|Добавить тег$'), add_bot))
    application.add_handler(CallbackQueryHandler(add_bot, '^add_tag$'))

    application.add_handler(MessageHandler(filters.Regex('^/hellp|Меню$'), start))
    application.add_handler(CallbackQueryHandler(start, '^hellp$'))

    loop = asyncio.get_event_loop()
    # loop.create_task(delete_mess(interval_hours=12)
    loop.create_task(periodic_internet_check(interval_hours=6)) ##выполнение команды проверки интернета каждые 6 часов

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()