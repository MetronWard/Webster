import logging
import shelve
from functools import wraps

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from webster_scrape import Webster

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


def send_action(self):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        async def command_func(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=self.action)
            return await func(update, context, *args, **kwargs)

        return command_func

    return decorator


class Bot:

    def __init__(self):
        name = shelve.open('keys/api_keys')
        self.api_key = name['telegram_api']
        self.webster = Webster()
        self.action = 'typing'
        logging.info('Telegram bot has been created')

    @staticmethod
    def send_action(action):
        """Sends `action` while processing func command."""

        def decorator(func):
            @wraps(func)
            async def command_func(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
                await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
                return await func(self, update, context, *args, **kwargs)

            return command_func

        return decorator

    @send_action('typing')
    async def dictionary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        result = self.webster.get_dict(context.args)
        if result:
            for entry in result[0]:
                await update.message.reply_html(entry)
                logging.info('Response to command sent')
            await update.message.reply_text(f'You can read more on {result[1]}')
            logging.info('Reference link sent')
        else:
            await update.message.reply_text('Could Not find anything relating to the word searched')

    @send_action('typing')
    async def thesa(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        result = self.webster.get_thes(context.args)
        if result:
            for k, v in result[0].items():
                await update.message.reply_text(k)
                await update.message.reply_text(', '.join(v))
            await update.message.reply_text(f'You can read more at {result[1]}')
        else:
            await update.message.reply_text('Could Not find anything relating to the word searched')

    def main(self):
        app = Application.builder().token(token=self.api_key).build()
        diction = CommandHandler('d', self.dictionary)
        thes = CommandHandler('t', self.thesa)
        app.add_handler(diction)
        app.add_handler(thes)
        app.run_polling()


if __name__ == "__main__":
    bot = Bot()
    bot.main()
