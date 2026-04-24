import os
from dotenv import load_dotenv
from bot.telegram_bot import setup_bot, run_bot

load_dotenv()

def main():
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY")
    
    if telegram_token == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Warning: TELEGRAM_BOT_TOKEN not set. Using placeholder.")
    if openrouter_key == "YOUR_OPENROUTER_API_KEY":
        print("Warning: OPENROUTER_API_KEY not set. Using placeholder.")
    
    bot_app = setup_bot(telegram_token, openrouter_key)
    run_bot(bot_app)

if __name__ == "__main__":
    main()
