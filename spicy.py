import sqlite3 as sql
import logging

from telegram import Update, Bot
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def remember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.effective_user

DB = 'user.db'

async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Отлично, теперь дай мне права на чтение сообщений и я приступлю к работе')

async def remember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.name
    id_user = update.effective_user.id
    chat = update.effective_chat.id
    title = update.effective_chat.title
    con = sql.connect(DB)
    with con:
        cur = con.cursor()
        if not title: title = 'BOT'
        try:
            cur.execute("CREATE TABLE IF NOT EXISTS `user` (`name` STRING, `id_user` INTEGER, `title` STRING, `id_chat` INTEGER)")
            cur.execute(f"BEGIN TRANSACTION; ")
            cur.execute(f"SELECT COUNT(*) FROM user WHERE name = '{user}' AND title = '{title}';")
            cur.execute(f"INSERT INTO user VALUES ('{user}', {id_user}, '{title}', {chat});")
            cur.execute("COMMIT;")
            con.commit()
            cur.close()
        except: return

async def call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat.id
    text = sql.connect(DB).execute(f"SELECT name FROM user WHERE id_chat = {chat};").fetchall()
    mas = ''
    for f in text:
        mas += f[0] + " "
    await update.message.reply_text(mas, do_quote=False)

def main() -> None:
    application = Application.builder().token("6941947875:AAFVzXUviZAgmuZmV1p5dQVhSOtaVcuuEr8").build()

    application.add_handler(CommandHandler("start", link, filters.Regex('link')))
    application.add_handler(CommandHandler("remember", remember))
    application.add_handler(MessageHandler(
                            filters.Regex("@all|@все|@чурки"), call))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()