import logging
import asyncio
import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from bot.user_state import get_user_model, set_user_model
from ai.model_router import route_request
from generator.project_generator import generate_project
from bot.api_key_manager import api_key_manager

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load master prompt from file
MASTER_PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "MASTER_PROMPT.txt")

def load_master_prompt():
    """Load the master prompt from file"""
    try:
        with open(MASTER_PROMPT_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"MASTER_PROMPT.txt not found at {MASTER_PROMPT_PATH}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message and model selection buttons"""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Local Model (Colab)", callback_data="model_local")],
        [InlineKeyboardButton("GPT-3.5 Turbo (OpenRouter)", callback_data="model_openrouter")],
        [InlineKeyboardButton("Auto Mode", callback_data="model_auto")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Welcome {user.first_name}! Select a model to generate projects:\n"
        "• Local Model (Colab): Small local model (may fallback to OpenRouter)\n"
        "• GPT-3.5 Turbo (OpenRouter): Fast and reliable via OpenRouter API\n"
        "• Auto Mode: Tries GPT-3.5, Gemini, Claude, Llama models\n\n"
        "🔑 **Manage API Keys:** Use `/apikey` to add, list, select, or test your OpenRouter API keys.",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle model selection button clicks"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    model_choice = query.data

    if model_choice == "model_local":
        set_user_model(user_id, "local_mistral")
        await query.edit_message_text(text="✅ Selected: Local Model (Colab). Send your project request!")
    elif model_choice == "model_openrouter":
        set_user_model(user_id, "openrouter_mistral")
        await query.edit_message_text(text="✅ Selected: GPT-3.5 Turbo (OpenRouter). Send your project request!")
    elif model_choice == "model_auto":
        set_user_model(user_id, "auto")
        await query.edit_message_text(text="✅ Selected: Auto Mode. Send your project request!")

async def handle_project_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user project requests, generate project, send zip"""
    user_id = update.effective_user.id
    user_prompt = update.message.text
    
    # Get user's selected API key if available, otherwise use global key
    user_api_key = api_key_manager.get_selected_key(user_id)
    openrouter_key = user_api_key or context.bot_data.get("openrouter_key")
    
    # Get master prompt from bot data
    master_prompt_template = context.bot_data.get("master_prompt")
    
    if not master_prompt_template:
        await update.message.reply_text("❌ Error: Master prompt not loaded. Please contact admin.")
        return
    
    # Replace placeholder with actual user input
    full_prompt = master_prompt_template.replace("{USER_INPUT_HERE}", user_prompt)
    
    await update.message.reply_text("⏳ Generating your project... This may take a few minutes.")

    try:
        # Run synchronous model routing in a thread to avoid blocking
        raw_response = await asyncio.to_thread(route_request, user_id, full_prompt, openrouter_key)
        # Run synchronous project generation in a thread
        project_info = await asyncio.to_thread(generate_project, raw_response)
        
        # Send the generated zip file
        zip_path = project_info["zip_path"]
        await update.message.reply_text(f"✅ Project {project_info['project_name']} generated! Sending zip file...")
        
        with open(zip_path, "rb") as f:
            await context.bot.send_document(
                chat_id=user_id,
                document=f,
                filename=f"{project_info['project_name']}.zip"
            )
        await update.message.reply_text("🎉 Project sent successfully! Unzip and follow the README to run.")
    except Exception as e:
        logger.error(f"Project generation failed: {e}")
        await update.message.reply_text(f"❌ Failed to generate project: {str(e)}")

async def apikey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /apikey command for API key management"""
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        # Show help if no arguments
        help_text = """
🔑 **API Key Management Commands:**

• `/apikey add <name> <key>` - Add a new API key
  Example: `/apikey add primary sk-or-v1-abc123...`

• `/apikey list` - List all your API keys

• `/apikey select <name>` - Select which key to use
  Example: `/apikey select primary`

• `/apikey test [name]` - Test an API key (or selected one)

• `/apikey remove <name>` - Remove an API key

• `/apikey status` - Show current key status

**Note:** Your API keys are stored locally and only you can access them.
        """
        await update.message.reply_text(help_text)
        return
    
    command = args[0].lower()
    
    if command == "add" and len(args) >= 3:
        # /apikey add <name> <key>
        key_name = args[1]
        api_key = " ".join(args[2:])
        
        success = api_key_manager.add_key(user_id, key_name, api_key, "openrouter")
        if success:
            await update.message.reply_text(f"✅ API key '{key_name}' added successfully!")
            
            # Show summary
            summary = api_key_manager.get_user_summary(user_id)
            if summary["has_keys"]:
                await update.message.reply_text(
                    f"📊 Status: {summary['total_keys']} keys, "
                    f"selected: {summary['selected_key_name'] or 'None'}"
                )
        else:
            await update.message.reply_text(f"❌ Failed to add key '{key_name}'. Key with this name may already exist.")
    
    elif command == "list":
        # /apikey list
        keys = api_key_manager.list_keys(user_id)
        
        if not keys:
            await update.message.reply_text("📭 You have no API keys stored. Use `/apikey add` to add one.")
            return
        
        selected_name = api_key_manager.get_selected_key_info(user_id)
        selected_name = selected_name["name"] if selected_name else None
        
        key_list = []
        for i, key in enumerate(keys, 1):
            prefix = "✅ " if key["name"] == selected_name else "  "
            masked_key = key["key"][:10] + "..." + key["key"][-10:] if len(key["key"]) > 20 else key["key"]
            key_list.append(f"{prefix}{i}. **{key['name']}** ({key['type']})\n   `{masked_key}`")
        
        await update.message.reply_text(
            f"🔑 **Your API Keys** ({len(keys)} total):\n\n" + "\n\n".join(key_list)
        )
    
    elif command == "select" and len(args) >= 2:
        # /apikey select <name>
        key_name = args[1]
        
        success = api_key_manager.select_key(user_id, key_name)
        if success:
            await update.message.reply_text(f"✅ Selected API key: **{key_name}**")
        else:
            await update.message.reply_text(f"❌ Key '{key_name}' not found. Use `/apikey list` to see available keys.")
    
    elif command == "test":
        # /apikey test [name]
        key_name = args[1] if len(args) >= 2 else None
        
        await update.message.reply_text("🔍 Testing API key...")
        
        result = api_key_manager.test_key(user_id, key_name)
        
        if result["success"]:
            await update.message.reply_text(
                f"✅ {result['message']}\n"
                f"Preview: {result.get('response_preview', 'N/A')}"
            )
        else:
            await update.message.reply_text(f"❌ {result['message']}")
    
    elif command == "remove" and len(args) >= 2:
        # /apikey remove <name>
        key_name = args[1]
        
        success = api_key_manager.remove_key(user_id, key_name)
        if success:
            await update.message.reply_text(f"✅ API key '{key_name}' removed successfully!")
            
            # Show updated status
            summary = api_key_manager.get_user_summary(user_id)
            if summary["has_keys"]:
                await update.message.reply_text(
                    f"📊 Status: {summary['total_keys']} keys, "
                    f"selected: {summary['selected_key_name'] or 'None'}"
                )
            else:
                await update.message.reply_text("📭 You have no API keys remaining.")
        else:
            await update.message.reply_text(f"❌ Key '{key_name}' not found.")
    
    elif command == "status":
        # /apikey status
        summary = api_key_manager.get_user_summary(user_id)
        
        if summary["has_keys"]:
            status_text = (
                f"📊 **API Key Status**\n\n"
                f"• Total keys: {summary['total_keys']}\n"
                f"• Selected key: **{summary['selected_key_name']}**\n"
                f"• Key preview: `{summary['selected_key']}`\n\n"
                f"Use `/apikey list` to see all keys."
            )
        else:
            status_text = (
                "📭 **No API Keys Stored**\n\n"
                "You haven't added any API keys yet.\n"
                "Use `/apikey add <name> <key>` to add your first key."
            )
        
        await update.message.reply_text(status_text)
    
    else:
        await update.message.reply_text(
            "❌ Invalid command. Use `/apikey` without arguments to see help."
        )

def setup_bot(telegram_token, openrouter_key):
    """Initialize and configure the Telegram bot application"""
    application = Application.builder().token(telegram_token).build()
    
    # Store OpenRouter key in bot data for access in handlers
    application.bot_data["openrouter_key"] = openrouter_key
    
    # Load and store master prompt
    master_prompt = load_master_prompt()
    if master_prompt:
        application.bot_data["master_prompt"] = master_prompt
        logger.info("Master prompt loaded successfully")
    else:
        logger.error("Failed to load master prompt")
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("apikey", apikey_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_project_request))
    
    return application

def run_bot(application):
    """Start the bot polling"""
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
