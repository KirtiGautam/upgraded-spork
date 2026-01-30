"""Telegram-specific bot implementation and handlers."""

import logging
import telebot
import os
from core import torrents


def initialize_bot():
    """Initialize and configure the Telegram bot."""
    token = os.environ["token"]
    bot = telebot.TeleBot(token)
    
    logger = telebot.logger
    telebot.logger.setLevel(logging.DEBUG)
    
    return bot


def register_handlers(bot):
    """Register all message and callback handlers for the bot."""
    
    @bot.message_handler(commands=["start"])
    def start_command(message):
        bot.send_message(message.chat.id, "Welcome !!")

    @bot.message_handler(commands=["categories"])
    def categories_command(message):
        bot.send_message(message.chat.id, torrents.get_categories(), parse_mode="Markdown")

    @bot.message_handler(commands=["help"])
    def help_command(message):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                "Message the developer", url="telegram.me/Kirti8c"
            )
        )
        bot.send_message(
            message.chat.id,
            "This bot returns the list of top 10 torrents for search term sorted by seeders \n"
            + "1) Send the following command in the same order and case: \n"
            + "torrent - <YOUR_SEARCH_TERM> - <CATEGORY> - <SUBCATEGORY>\n"
            + "If you don't send category and subcategory, it will return search in all categories\n"
            + "2) You will see top 10 items in reply in following format:\n"
            + "<Number of seeders> - <Title>\n"
            + "4) Click the relevant title from list. \n"
            + "5) You will recieve the magnet link for the item\n"
            + "For the list of available categories send /categories",
            reply_markup=keyboard,
        )

    @bot.message_handler(regexp="torrent - [A-Za-z0-9 _-]*")
    def torrent_command(message):
        keyboard = telebot.types.InlineKeyboardMarkup()
        data = torrents.handle_search(message.text.split("-", 1)[1])
        if not data:
            bot.send_message(
                message.chat.id,
                "Invalid category - subcategory combination",
                reply_markup=keyboard,
            )
        else:
            for x in data:
                keyboard.row(
                    telebot.types.InlineKeyboardButton(
                        f'{x["seeders"]} - {x["name"]}',
                        callback_data=f"get-torrent-{x['info_hash']}",
                    )
                )

            bot.send_message(
                message.chat.id,
                "Click on the item to get magnet link:\n Seeders - Title",
                reply_markup=keyboard,
            )

    @bot.callback_query_handler(func=lambda call: True)
    def iq_callback(query):
        data = query.data
        if data.startswith("get-torrent-"):
            bot.answer_callback_query(query.id)
            link = torrents.generate_magnet_link(query.data[12:])
            bot.send_chat_action(query.message.chat.id, "typing")
            bot.send_message(query.message.chat.id, link)
    
    return bot


# Initialize the bot
bot = initialize_bot()

# Register all handlers
bot = register_handlers(bot)

# Start polling
bot.polling(none_stop=True)
