# SSAC (Steam Status Activity Check)

## Description

- This is an application that checks the online activity of a Steam profile by its corresponding SteamID.
- The application still works very poorly, so sometimes the Telegram bot may not show a message about changing the request in Telegram (if you run the script through main.py, then everything should work fine), but everything is displayed correctly in the terminal.

Note: Unfortunately, if the user has set the status to "Invisible", the application will count it as Offline.


## Get Started

- The script uses the `python telegram bot` library, so you need to install it before running.

```pip install python-telegram-bot --upgrade```

- To operate the bot, you need the bot itself, which can be created in Telegram using @BotFather, and its token, which can be obtained there. Also, to track activity, you need a Steam API key, which can be obtained at [link](https://steamcommunity.com/dev/apikey).

## Plans for the future

- Graphical interface in Telegram bot
- Change tracking account
- Fixing bugs and errors
- Code optimization
- More detailed information when tracking (example: replacing the account ID with its nickname in the message about the start of tracking, etc.)
