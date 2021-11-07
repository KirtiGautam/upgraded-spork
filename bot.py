import logging
import telebot
import os
from torrent import main

token = os.environ["token"]
bot = telebot.TeleBot(token)

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=["start"])
def start_command(message):
    bot.send_message(message.chat.id, "Welcome !!")


@bot.message_handler(commands=["categories"])
def start_command(message):
    bot.send_message(message.chat.id, main.get_categories(), parse_mode="Markdown")


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
        + "If you don't send category and subcategory, it will return search in all categories"
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
    data = main.handle_search(message.text.split("-", 1)[1])
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


def send_magnet_link(query):
    bot.answer_callback_query(query.id)
    link = main.generate_magnet_link(query.data[12:])
    bot.send_chat_action(query.message.chat.id, "typing")
    bot.send_message(query.message.chat.id, link)


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data.startswith("get-torrent-"):
        send_magnet_link(query)


bot.polling(none_stop=True)
