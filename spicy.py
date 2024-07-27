import sqlite3 as sql
import logging
import asyncio
import aiohttp
from cryptography.fernet import Fernet

from telegram import Update, Bot
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

DB = 'user.db'

async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Отлично, теперь дай мне права на чтение сообщений и я приступлю к работе')

async def start_remember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.name
    id_user = update.effective_user.id
    chat = update.effective_chat.id
    title = update.effective_chat.title
    remember(user, id_user, chat, title)

def load_key():
    return open("secret.key", "rb").read()

def encrypt_data(data):
    key = load_key()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data


# Расшифровка данных
def decrypt_data(encrypted_data):
    key = load_key()
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data
def remember (user, id_user, chat, title):
    title = encrypt_data(title)
    con = sql.connect(DB)
    with con:
        cur = con.cursor()
        if not title: title = 'BOT'
        try:
            cur.execute("CREATE TABLE IF NOT EXISTS `user` (`name` STRING, `id_user` INTEGER, `title` STRING, `id_chat` INTEGER, tags STRING, 'admin' INTEGER)")
            cur.execute(f"BEGIN TRANSACTION; ")
            cur.execute(f"SELECT COUNT(*) FROM user WHERE name = '{user}' AND title = '{title}';")
            if cur.fetchall():
                return False
            cur.execute(f"INSERT INTO user VALUES ('{user}', {id_user}, '{title}', {chat});")
            cur.execute("COMMIT;")
            con.commit()
            cur.close()
        except:
            pass

async def call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat.id
    text = sql.connect(DB).execute(f"SELECT name FROM user WHERE id_chat = {chat} and title != 'BOT';").fetchall()
    mas = ''
    for f in text:
        mas += f[0] + " "
    await update.message.reply_text(mas, do_quote=False)

async def periodic_internet_check(interval_hours):
    while True:
        internet_connected = await check_internet_connection()
        if internet_connected:
            logger.info("Интернет-соединение установлено.")
        else:
            logger.warning("Отсутствует интернет-соединение.")

        await asyncio.sleep(interval_hours * 3600)


async def check_internet_connection():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://www.google.com') as response:
                return response.status == 200
    except aiohttp.ClientError:
        return False

def main() -> None:
    application = Application.builder().token("6941947875:AAFVzXUviZAgmuZmV1p5dQVhSOtaVcuuEr8").build()

    application.add_handler(CommandHandler("start", link, filters.Regex('link')))
    application.add_handler(CommandHandler("remember", start_remember))
    application.add_handler(MessageHandler(
                            filters.Regex("@all|@все|@чурки|@гойда") | filters.CaptionRegex(r"@all|@все|@чурки|@гойда"), call))

    loop = asyncio.get_event_loop()
    loop.create_task(periodic_internet_check(interval_hours=6))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()