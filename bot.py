from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    ReplyKeyboardMarkup,
    BotCommand,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from math import ceil
import data, yt
import asyncio, time
from lyricsgenius import Genius


# Create a Client instance
BOT_TOKEN = "8454304817:AAGo94UPi4q7-60adyFqAntB5trVDhF-PPQ"
API_ID = 25678641
API_HASH = "c8f1cd4b42e98374785a2f96fc74e175"
app = Client("meowtune_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

genius = Genius("0GJ93kMmUCFmWspsmYkfbz062eauuoLEAGwyfBppAGTYN2R2-op08jTONcAxhLYE")

ITEMS_PER_PAGE = 8
def list_items(items: list[tuple[str, str]], page: int, menu: str = "search"):
    random_thing = time.time() % 1
    if items == []:
        return [
            [
                InlineKeyboardButton(
                    "Nothing found (try again?)",
                    callback_data=f"{menu}.retry.{random_thing}",
                )
            ]
        ]

    start = page * ITEMS_PER_PAGE
    end = min(start + ITEMS_PER_PAGE, len(items) - 1)
    buttons = []

    item_page = [
        [InlineKeyboardButton(item[0], callback_data=f"{menu}.{item[1]}")]
        for item in items[start:end]
    ]

    if page > 0:
        buttons.append(InlineKeyboardButton("<", callback_data=f"{menu}.{page - 1}"))
    else:
        buttons.append(InlineKeyboardButton(" ", callback_data=f"{menu}.{page}"))

    buttons.append(
        InlineKeyboardButton(
            f"{page+1}/{ceil(len(items)/ITEMS_PER_PAGE)}",
            callback_data=f"{menu}.{page}.{random_thing}",
        )
    )

    if (page + 1) * ITEMS_PER_PAGE < len(items):
        buttons.append(InlineKeyboardButton(">", callback_data=f"{menu}.{page + 1}"))
    else:
        buttons.append(InlineKeyboardButton(" ", callback_data=f"{menu}.{page}"))

    return [buttons] + item_page


@app.on_callback_query()
async def handle_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    call_data = callback_query.data.split(".")

    if call_data[0] == "search":
        if call_data[1] == "retry":
            page = 0
            global search_items
            msg = await callback_query.message.reply_text("Retrying...")
            search_items = await yt.search(search_text, msg)
        else:
            page = int(call_data[1])

        keyboard = InlineKeyboardMarkup(list_items(search_items, page))
        await callback_query.message.edit_text(
            f"Search results for {search_text} {page+1}/{ceil(len(search_items)/ITEMS_PER_PAGE)}",
            reply_markup=keyboard,
        )

    elif call_data[0] == "item":
        videoId = call_data[1]

        msg = await callback_query.message.reply_text("Downloading: 0% [this might take a while...]")
        path = await yt.download(videoId, msg)

        is_liked = data.get_user_data(user_id)["likes"].contains(str(videoId))
        keyboard = InlineKeyboardMarkup(
            [
                InlineKeyboardButton(
                    "Like?" if not is_liked else "Liked!",
                    callback_data=f"like.{videoId}",
                ),
                InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{videoId}"),
            ],
        )
        await client.send_audio(user_id, audio=path, reply_markup=keyboard)

    elif call_data[0] == "like":
        liked_tracks = data.get_user_data(user_id)["favorite_tracks"]
        data.update_user_data(user_id, likes=liked_tracks + "," + str(call_data[1]))

    elif call_data[0] == "lyrics":
        msg = await client.send_message(user_id, "Fetching lyrics...")
        info = await yt.get_info(call_data[1])
        await msg.edit_text("Fetching lyrics from genius.com...")
        callback_query.message.reply_text(
            genius.search_song(info["videoDetails"]["title"], info["videoDetails"]["author"]).lyrics
        )
        await msg.delete()

    elif call_data[0] == "collection":
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Favorite tracks", callback_data="tracks.0")],
                # [InlineKeyboardButton("Favorite albums", callback_data="albums.0")],
                # [InlineKeyboardButton("Favorite artists", callback_data="artists.0")],
            ]
        )
        await callback_query.message.edit_text("My collection", reply_markup=keyboard)

    elif call_data[0] == "tracks":
        if call_data[1] == "retry" or call_data[1] == "0":
            page = 0
            msg = await client.send_message(user_id, "Loading favorites...")
            tracks = data.get_user_data(user_id)["favorite_tracks"]

            global liked_items
            liked_items = []
            for i in range(len(tracks)):
                item = await yt.get_info(tracks[i], msg)
                if item == []:
                    await msg.edit_text("Could not load the song")
                    break
                liked_items.append(
                    (
                        f"{i+1} | {item.get('title', 'Unknown')} | {item.get('artists', 'Unknown')[0].get("name", "Unknown")} | {item.get('duration', 'Unknown')}",
                        tracks[i],
                    )
                )
        else:
            page = call_data[1]


        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("< Back", callback_data="collection")]] + list_items(liked_items, page, "tracks")
        )
        await msg.delete()
        await callback_query.edit_message_text("Favorite songs", reply_markup=keyboard)



# search for music
async def search(message: Message, text: str = None):
        if text == None:
            text = message.text

        msg = await app.send_message(message.from_user.id, "Searching...")
        global search_text
        global search_items
        search_text = text
        search_items = await yt.search(text, msg)

        keyboard = InlineKeyboardMarkup(list_items(search_items, 0))
        if type(search_items) == list:
            await message.reply_text(
                f"Search results for {search_text}", reply_markup=keyboard
            )
        else:
            await message.reply_text("Error: " + str(search_items), reply_markup=keyboard)



























# handler for /start
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await app.set_bot_commands(
        commands=[
            BotCommand("start", "Start the bot"),
            BotCommand("help", "List available commands"),
            BotCommand("search", "Search for song (requires 1 argument for query)"),
            BotCommand("collection", "Open collection menu"),
        ]
    )

    data.update_user_data(message.from_user.id)

    keyboard = ReplyKeyboardMarkup(
        [
            ["🔍 Search music", "📦 My collection"],
            # ["🌊 My vibe", "🔥 Trending"],
            # ["⚙️ Settings"]],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )

    await message.reply_text(
        """Hi! you can use this bot to find and download music from youtube.\n
		use menu for navigation""",
        reply_markup=keyboard,
    )


# handler for /help
@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply_text(
        """Availible commands:
		/start - start bot
		/help  - list availible commands

		use menu for navigation
	"""
    )


# handler for /search
@app.on_message(filters.command("search"))
async def search_command(client: Client, message: Message):
    if message.command:
        if len(message.command) > 1:
            await search(message, message.command[1])
        else:
            await message.reply_text("No query")
    else:
        await message.reply_text(
            "Send me a name of a song/album/artist that you are searching for"
        )
    data.update_user_data(message.from_user.id, state="search")


# handler for /collection
@app.on_message(filters.command("collection"))
async def collection_command(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Favorite tracks", callback_data="tracks.0")],
            # [InlineKeyboardButton("Favorite albums", callback_data="albums.0")],
            # [InlineKeyboardButton("Favorite artists", callback_data="artists.0")],
        ]
    )

    await message.reply_text("My collection", reply_markup=keyboard)


# plain text message
@app.on_message(filters.text & ~filters.command(["help", "start"]))
async def text_message(client: Client, message: Message):
    if message.text == "🔍 Search music":
        await search_command(client, message)
    elif message.text == "📦 My collection":
        await collection_command(client, message)
    else:
        await search(message)


# Start the bot
if __name__ == "__main__":
    print("Bot is running...")
    data.init_db()
    app.run()
