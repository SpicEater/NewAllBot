import logging
import asyncio
import aiohttp

from telegram import Update, helpers, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def add_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # keybord_1 =InlineKeyboardButton(text='Ссылка')
    # keybord_2 =InlineKeyboardButton(text='Меню', callback_data=start)

    url = helpers.create_deep_linked_url('spicyeater_bot', "link", group=True)
    await update.message.reply_text(
        'Нажми на кнопку, чтобы добавить бота',
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text='Ссылка', url=url)], [InlineKeyboardButton(text='Меню', callback_data='hellp')]]
        ),
    )



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        ["Добавить людей", "Удалить уведомления"],
        ["Добавить бота", "Добавить тег"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard)
    await update.message.reply_text('⚙️ Меню ⚙️ \n\n'
                              '— /add_people - добавить людей в группу 👥\n'
                              '— /mute - удалить уведомления🔕\n'
                              '— /add_bot - добавить бота  🤖\n'
                              '— /add_tag - добавить тег для уведомления 🔔\n',
                                    reply_markup=markup)

async def hellp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text= '⚙️ Меню ⚙️ \n\n'
                              '— /add_people - добавить людей в группу 👥\n'
                              '— /mute - удалить уведомления🔕\n'
                              '— /add_bot - добавить бота  🤖\n'
                              '— /add_tag - добавить тег для уведомления 🔔\n')

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
    application = Application.builder().token("6572779723:AAGvYhji-PdqXZWj72E1lrAUjqOMYT5Tz0E").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(hellp, '^hellp$'))
    application.add_handler(MessageHandler(filters.Regex('^/add_people|Добавить людей$'), add_bot))
    application.add_handler(MessageHandler(filters.Regex('^/mute|Удалить уведомления$'), add_bot))
    application.add_handler(MessageHandler(filters.Regex('^/add_bot|Добавить бота$'), add_bot))
    application.add_handler(MessageHandler(filters.Regex('^/add_tag|Добавить тег$'), add_bot))
    application.add_handler(MessageHandler(filters.Regex('^/hellp|Меню$'), start))
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_internet_check(interval_hours=6))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()