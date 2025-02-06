import aiohttp
import asyncio
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

CONFIG_FILE = "config.json"
steam_api_key = ""
telegram_token = ""
chat_id = None
steam_id = None
tracking = False

def load_config():
    global telegram_token, steam_api_key
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)
                telegram_token = config.get("telegram_token", "")
                steam_api_key = config.get("steam_api_key", "")
        except (json.JSONDecodeError, FileNotFoundError):
            print("Error reading config, requesting new data...")
    else:
        print("Config not found, requesting new data...")

    if not telegram_token:
        telegram_token = input("Enter your Telegram Bot Token: ")
    if not steam_api_key:
        steam_api_key = input("Enter your Steam API Key: ")

    save_config()

def save_config():
    config = {
        "telegram_token": telegram_token,
        "steam_api_key": steam_api_key
    }
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

async def validate_steam_id(steam_id):
    """Проверяет валидность SteamID64 или custom URL"""
    if steam_id.isdigit() and len(steam_id) == 17:
        return True
    url = f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={steam_api_key}&vanityurl={steam_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return "response" in data and "steamid" in data["response"]
    return False

async def get_steam_status(api_key, steam_id):
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data["response"]["players"]:
                    player = data["response"]["players"][0]
                    return player.get("personastate"), player.get("personaname")
    return None, None

async def send_telegram_message(token, chat_id, message, reply_markup=None):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    if reply_markup:
        params["reply_markup"] = json.dumps(reply_markup.to_dict())  # Преобразуем клавиатуру в JSON

    async with aiohttp.ClientSession() as session:
        await session.get(url, params=params)


async def start(update: Update, context):
    global chat_id, steam_id
    chat_id = update.message.chat_id
    message = "Send your SteamID for tracking."
    if steam_id:
        message += f"\nCurrent tracked SteamID: {steam_id}"
    await send_telegram_message(telegram_token, chat_id, message)

async def handle_message(update: Update, context):
    global steam_id, tracking
    user_steam_id = update.message.text.strip()

    if not await validate_steam_id(user_steam_id):
        await send_telegram_message(telegram_token, update.message.chat_id, "⚠️ Incorrect SteamID. Try again.")
        return

    steam_id = user_steam_id
    tracking = True
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_tracking")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await send_telegram_message(telegram_token, chat_id, "🔍 Tracking started", reply_markup)
    asyncio.create_task(track_status())

async def cancel_tracking(update: Update, context):
    global tracking, steam_id
    tracking = False
    steam_id = None
    await send_telegram_message(telegram_token, chat_id, "⛔ Tracking canceled.\n\n🔄 Submit a new SteamID for tracking.")

async def track_status():
    """Цикл отслеживания статуса Steam"""
    global tracking
    previous_status = None
    while tracking:
        if steam_id:
            current_status, user_name = await get_steam_status(steam_api_key, steam_id)
            if current_status is not None and current_status != previous_status:
                status_text = "🟢 Online" if current_status != 0 else "🔴 Offline"
                message = f"⚡ Account status ({user_name}) has  been changed: *{status_text}*"
                await send_telegram_message(telegram_token, chat_id, message)
                previous_status = current_status
        await asyncio.sleep(10)

def main():
    global telegram_token, steam_api_key
    load_config()
    application = Application.builder().token(telegram_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(cancel_tracking, pattern="cancel_tracking"))
    print("Bot started")
    application.run_polling()

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
