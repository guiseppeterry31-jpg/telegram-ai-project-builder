# Telegram AI Project Builder Bot

Production-ready Telegram bot that generates complete software projects using AI, with model selection, auto-rotation, and ZIP export.

## Features

- Telegram bot with inline model selection (Mistral Colab, Mistral OpenRouter, Auto Mode)
- Local Mistral 7B Instruct with 4-bit quantization (Colab compatible, low memory)
- OpenRouter API integration with multi-model fallback
- Automatic project generation (multi-file, proper folder structure)
- ZIP export of generated projects
- Error handling, retry logic, and safe JSON parsing

## Setup Instructions

1. **Get Tokens**:
   - Create a Telegram bot via @BotFather to get `TELEGRAM_BOT_TOKEN`
   - Get an OpenRouter API key from https://openrouter.ai to get `OPENROUTER_API_KEY`

2. **Configure Environment**:
   - Set environment variables or create a `.env` file:
     ```
     TELEGRAM_BOT_TOKEN=your_telegram_token_here
     OPENROUTER_API_KEY=your_openrouter_key_here
     ```

3. **Run Setup**:
   - Windows: Double-click `setup.bat` (installs dependencies and starts the bot)
   - Manual: `pip install -r requirements.txt` then `python main.py`

## Usage

1. Start a chat with your bot, send `/start`
2. Select your preferred model via inline buttons
3. Send your project request (e.g., "Create a Flask web app with login system")
4. Wait for the bot to generate the project and send the ZIP file
5. Unzip the project and follow the included README to run

## Notes

- Local Mistral model requires a GPU with 8GB+ VRAM (Colab compatible)
- Auto Mode tries 4 models via OpenRouter with automatic fallback
- Generated projects are saved in the `generated_projects/` directory
