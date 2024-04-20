import logging
import asyncio
import aiohttp

from telegram import Update, helpers, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = helpers.create_deep_linked_url('spicyeater_bot', "link", group=True)
    await update.message.reply_text(
        'Нажми на кнопку, чтобы добавить бота',
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text='Ссылка', url=url)]]
        )
    )


async def periodic_internet_check(interval_hours):
    while True:
        internet_connected = await check_internet_connection()
        if internet_connected:
            logger.info("Интернет-соединение установлено.")
        else:
            logger.warning("Отсутствует интернет-соединение.")

        # Ждем указанный интервал перед следующей проверкой
        await asyncio.sleep(interval_hours * 3600)


async def check_internet_connection():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://www.google.com') as response:
                return response.status == 200
    except aiohttp.ClientError:
        return False


def main() -> None:
    application = Application.builder().token("6572779723:AAGvYhji-PdqXZWj72E1lrAUjqOMYT5Tz0E").build()

    application.add_handler(CommandHandler("start", start))

    loop = asyncio.get_event_loop()
    loop.create_task(periodic_internet_check(interval_hours=6))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()