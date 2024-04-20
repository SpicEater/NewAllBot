import logging
import time

from telegram import Update, helpers, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot.username
    url = helpers.create_deep_linked_url('spicyeater_bot', "link", group=True)
    await update.message.edit_text(
        'Нажми на кнопку, чтобы добавить бота',
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text= 'Ссылка', url=url)]]
        )
    )

def main() -> None:
    application = Application.builder().token("6572779723:AAGvYhji-PdqXZWj72E1lrAUjqOMYT5Tz0E").build()

    application.add_handler(CommandHandler("start", start))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()