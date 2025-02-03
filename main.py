import requests
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# params
steam_api_key = ""
telegram_token = ""
chat_id = None  # The chat ID will be obtained via the command /start
steam_id = None  # steam_id will be provided by the user


# Function to check Steam status
def get_steam_status(api_key, steam_id):
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["response"]["players"]:
            player = data["response"]["players"][0]
            status = player["personastate"]
            return status
        else:
            return None
    else:
        return None


# Function of sending a message in Telegram
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": message
    }
    requests.get(url, params=params)


# Function to handle the /start command
async def start(update: Update, context):
    global chat_id, steam_id

    chat_id = update.message.chat_id
    message = "Send your SteamID to track status"

    # Checking if there is already a steam_id sent
    if steam_id:
        message = f"\nCurrent Tracked SteamID: {steam_id}"

    await send_telegram_message(telegram_token, chat_id, message)


# Function for processing messages from the user
def handle_message(update: Update, context):
    global steam_id

    if not steam_id:
        steam_id = update.message.text.strip()  # Getting SteamID from the user
        send_telegram_message(telegram_token, update.message.chat_id, f"Starting to track account status with SteamID: {steam_id}")

        track_status()

    else:
        send_telegram_message(telegram_token, update.message.chat_id, "SteamID is already installed. Starting tracking")

        track_status()


def track_status():
    previous_status = None
    while True:
        current_status = get_steam_status(steam_api_key, steam_id)
        if current_status is not None:
            if current_status != previous_status:
                status_text = "Online" if current_status != 0 else "Offline"
                message = f"Account status ({steam_id}) has been changed: *{status_text}*"
                send_telegram_message(telegram_token, chat_id, message)
                print(message)
                previous_status = current_status

        time.sleep(10)


def main():
    global telegram_token, steam_api_key

    # Request the bot token and Steam API Key if they are not already set
    if not telegram_token:
        telegram_token = input("Your Telegram bot token (tg: @BotFather): ")

    if not steam_api_key:
        steam_api_key = input("Your Steam API Key (https://steamcommunity.com/dev/apikey): ")

    # Create and launch the application
    application = Application.builder().token(telegram_token).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Processing all text messages

    # Running a bot
    application.run_polling()

    # Start tracking account status
    track_status()




if __name__ == "__main__":
    main()



