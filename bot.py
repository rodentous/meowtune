from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message,
    MessageEntity,
    ReplyKeyboardMarkup,
    BotCommand,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from math import ceil
import data
import meta
from meta import Track
import asyncio, time
from lyricsgenius import Genius


# Create a Client instance
BOT_TOKEN = "8454304817:AAGo94UPi4q7-60adyFqAntB5trVDhF-PPQ"
API_ID = 25678641
API_HASH = "c8f1cd4b42e98374785a2f96fc74e175"
app = Client("meowtune_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

genius = Genius("0GJ93kMmUCFmWspsmYkfbz062eauuoLEAGwyfBppAGTYN2R2-op08jTONcAxhLYE")


def list_items(items: list[(str, str)], page: int, menu: str = "search"):
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

    ITEMS_PER_PAGE = 6
    pages = ceil(len(items) / ITEMS_PER_PAGE)
    start = page * ITEMS_PER_PAGE
    end = min(start + ITEMS_PER_PAGE, len(items))

    item_page = [
        [InlineKeyboardButton(item[0], callback_data=f"item.{item[1]}")]
        for item in items[start:end]
    ]

    if pages == 1:
        return item_page

    # Page navigation bar
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("<", callback_data=f"{menu}.{page - 1}"))
    else:
        buttons.append(InlineKeyboardButton(" ", callback_data=f"{menu}.{page}"))

    buttons.append(
        InlineKeyboardButton(
            f"{page + 1}/{pages}",
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
    user_id: str = callback_query.from_user.id
    call_data: list[str] = callback_query.data.split(".")

    # Searching
    if call_data[0] == "search":
        page: int = 0
        global search_query
        global search_results

        if call_data[1] == "retry":
            progress_message = await callback_query.message.reply_text("Searching...")
            search_results = meta.search_tracks(search_query)
        else:
            page = int(call_data[1])

        items = [
            (f"{t.title} | {t.artist} | {t.show_duration()}", t.track_id)
            for t in search_results
        ]

        keyboard = InlineKeyboardMarkup(list_items(items, page))
        await callback_query.message.edit_text(
            f"Search results for {search_query}",
            reply_markup=keyboard,
        )
        if progress_message:
            await progress_message.delete()

    # Item selected
    elif call_data[0] == "item":
        track_id = call_data[1]

        progress_message = await callback_query.message.reply_text("Downloading...")
        path = meta.download_track(track_id)

        favorite = track_id in data.get_user_data(user_id)["favorite_tracks"]
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Like?" if not favorite else "Liked!",
                        callback_data=f"like.{track_id}",
                    ),
                    InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{track_id}"),
                ]
            ]
        )
        await client.send_audio(user_id, audio=path, reply_markup=keyboard)
        await progress_message.delete()

    elif call_data[0] == "like":
        track_id = call_data[1]
        favorite = track_id in data.get_user_data(user_id)["favorite_tracks"]
        favorite_tracks = data.get_user_data(user_id)["favorite_tracks"]

        if not favorite:
            favorite_tracks.insert(0, track_id)
            favorite = True
        else:
            favorite_tracks.remove(track_id)
            favorite = False
        data.update_user_data(user_id, favorite_tracks=",".join(favorite_tracks))

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Like?" if not favorite else "Liked!",
                        callback_data=f"like.{track_id}.{time.time() % 1}",
                    ),
                    InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{track_id}"),
                ]
            ]
        )
        await callback_query.message.edit_caption("", reply_markup=keyboard)

    elif call_data[0] == "lyrics":
        progress_message = await client.send_message(user_id, "Getting info...")
        track = meta.get_track(call_data[1])

        await progress_message.edit_text(
            f"Fetching lyrics for {track.title} - {track.artist}"
        )
        lyrics = genius.search_song(track.title, track.artist).lyrics

        quote_entity = [
            MessageEntity(
                type=enums.MessageEntityType.BLOCKQUOTE,
                offset=0,
                length=len(lyrics),
                expandable=True,
            )
        ]
        await callback_query.message.reply_text(lyrics, entities=quote_entity)
        await progress_message.delete()

    elif call_data[0] == "collection":
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Favorite tracks", callback_data="tracks")],
                # [InlineKeyboardButton("Favorite albums", callback_data="albums")],
                # [InlineKeyboardButton("Favorite artists", callback_data="artists")],
            ]
        )
        await callback_query.message.edit_text("My collection", reply_markup=keyboard)

    elif call_data[0] == "tracks":
        page: int = 0
        if len(call_data) == 1 or call_data[1] == "retry":
            progress_message = await client.send_message(
                user_id, "Loading favorites..."
            )
            tracks = data.get_user_data(user_id)["favorite_tracks"]
            if "" in tracks:
                tracks.remove("")

            global favorite_results
            favorite_results = []
            for track in tracks:
                t = meta.get_track(track)

                favorite_results.append(
                    (
                        f"{t.title} | {t.artist} | {t.show_duration()}",
                        t.track_id,
                    )
                )
        else:
            page = int(call_data[1])

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("< Back", callback_data="collection")]]
            + list_items(favorite_results, page, "tracks")
        )
        await callback_query.edit_message_text("Favorite songs", reply_markup=keyboard)
        await progress_message.delete()


# search for music
async def search(message: Message, query: str = None):
    if query == None:
        query = message.text

    progress_message = await app.send_message(message.from_user.id, "Searching...")

    global search_query
    search_query = query

    global search_results
    search_results = meta.search_tracks(query)

    items = [
        (f"{t.title} | {t.artist} | {t.show_duration()}", t.track_id)
        for t in search_results
    ]

    keyboard = InlineKeyboardMarkup(list_items(items, 0))
    await message.reply_text(
        f"Search results for {search_query}", reply_markup=keyboard
    )
    await progress_message.delete()


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
		/search <query> - search for query
		/collection - open collection menu

		use menu for navigation
	"""
    )
    lyrics = genius.search_song("Альтернатива", "Дайте танк(!)").lyrics

    quote_entity = [
        MessageEntity(
            type=enums.MessageEntityType.BLOCKQUOTE,
            offset=0,
            length=len(lyrics),
            expandable=True,
        )
    ]
    await message.reply_text(lyrics, entities=quote_entity)


# handler for /search
@app.on_message(filters.command("search"))
async def search_command(client: Client, message: Message):
    if len(message.command) > 1:
        await search(message, message.command[1])
    else:
        await message.reply_text("No query")


# handler for /collection
@app.on_message(filters.command("collection"))
async def collection_command(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Favorite tracks", callback_data="tracks")],
            # [InlineKeyboardButton("Favorite albums", callback_data="albums")],
            # [InlineKeyboardButton("Favorite artists", callback_data="artists")],
        ]
    )

    await message.reply_text("My collection", reply_markup=keyboard)


# plain text message
@app.on_message(filters.text & ~filters.command(["help", "start"]))
async def text_message(client: Client, message: Message):
    if message.text == "🔍 Search music":
        await message.reply_text(
            "Send me a name of a song/album/artist that you are searching for"
        )
    elif message.text == "📦 My collection":
        await collection_command(client, message)
    else:
        await search(message)


# Start the bot
if __name__ == "__main__":
    print("Bot is running...")
    data.init_db()
    app.run()
