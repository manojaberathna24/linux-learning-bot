"""
Settings Handler
API key and model configuration
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from modules.supabase_client import db
import config

# Conversation states
WAITING_API_KEY = 1


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings menu"""
    user = update.effective_user
    user_settings = await db.get_user_settings(user.id)
    
    has_key = "✅" if user_settings.get("openrouter_key") else "❌"
    current_model = user_settings.get("selected_model") or "Not set"
    
    # Find model name
    model_name = current_model
    for model in config.AVAILABLE_MODELS:
        if model["id"] == current_model:
            model_name = model["name"]
            break
    
    settings_text = f"""
⚙️ **Settings**

**API Key:** {has_key}
**Selected Model:** {model_name}

Choose an option below:
"""
    
    keyboard = [
        [InlineKeyboardButton("🔑 Set API Key", callback_data="settings_api_key")],
        [InlineKeyboardButton("🤖 Select Model", callback_data="settings_model")],
        [InlineKeyboardButton("ℹ️ Get Free API Key", callback_data="settings_help")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(settings_text, reply_markup=reply_markup, parse_mode="Markdown")


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings menu callbacks"""
    query = update.callback_query
    await query.answer()
    
    action = query.data.replace("settings_", "")
    
    if action == "api_key":
        await query.edit_message_text(
            "🔑 **Set OpenRouter API Key**\n\n"
            "Please send me your OpenRouter API key.\n\n"
            "⚠️ Keep this private! Delete your message after I confirm.\n\n"
            "Type /cancel to abort.",
            parse_mode="Markdown"
        )
        return WAITING_API_KEY
    
    elif action == "model":
        await show_model_selection(query)
    
    elif action == "help":
        help_text = """
ℹ️ **How to Get Free OpenRouter API Key**

1. Go to: https://openrouter.ai
2. Sign up for a free account
3. Go to Keys section
4. Create a new API key
5. Copy the key and send it here

**Free Credits:**
New accounts get free credits to try models!

**Free Models Available:**
• Llama 3.1 8B
• Gemini 2.0 Flash
• Qwen 2 7B
• Phi-3 Mini

Back to settings: /settings
"""
        await query.edit_message_text(help_text, parse_mode="Markdown")


async def show_model_selection(query_or_update):
    """Show model selection menu"""
    keyboard = []
    for model in config.AVAILABLE_MODELS:
        name = model["name"]
        if "(Free)" in name:
            name = f"🆓 {name}"
        keyboard.append([InlineKeyboardButton(name, callback_data=f"model_{model['id']}")])
    
    keyboard.append([InlineKeyboardButton("« Back", callback_data="settings_back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🤖 **Select AI Model**\n\nChoose your preferred model:"
    
    if hasattr(query_or_update, 'edit_message_text'):
        await query_or_update.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await query_or_update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def model_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle model selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "settings_back":
        # Return to settings menu
        await query.message.delete()
        context_update = type('obj', (object,), {'effective_user': query.from_user, 'message': query.message})()
        context_update.message.reply_text = query.message.reply_text
        await settings_command(context_update, context)
        return
    
    model_id = query.data.replace("model_", "")
    user = query.from_user
    
    # Save model selection
    success = await db.update_user_model(user.id, model_id)
    
    if success:
        # Find model name
        model_name = model_id
        for model in config.AVAILABLE_MODELS:
            if model["id"] == model_id:
                model_name = model["name"]
                break
        
        await query.edit_message_text(
            f"✅ **Model Updated**\n\nYour selected model: {model_name}\n\n"
            f"Use /ask to test it out!",
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text("❌ Failed to update model. Please try again.")


async def receive_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save API key"""
    user = update.effective_user
    api_key = update.message.text.strip()
    
    # Basic validation
    if len(api_key) < 20:
        await update.message.reply_text(
            "❌ That doesn't look like a valid API key.\n\n"
            "Please send a valid OpenRouter API key or /cancel"
        )
        return WAITING_API_KEY
    
    # Save API key
    success = await db.update_user_api_key(user.id, api_key)
    
    if success:
        await update.message.reply_text(
            "✅ **API Key Saved Successfully!**\n\n"
            "⚠️ Please delete your message containing the key for security.\n\n"
            "Next, select a model: /settings",
            parse_mode="Markdown"
        )
        
        # Try to delete user's message with API key
        try:
            await update.message.delete()
        except:
            pass
        
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ Failed to save API key.try again.")
        return WAITING_API_KEY


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    await update.message.reply_text("❌ Cancelled. Use /settings to try again.")
    return ConversationHandler.END


def setup_settings_handlers(application):
    """Register settings handlers"""
    # Settings conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(settings_callback, pattern="^settings_api_key$")],
        states={
            WAITING_API_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_api_key),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
    )
    
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CallbackQueryHandler(settings_callback, pattern="^settings_"))
    application.add_handler(CallbackQueryHandler(model_callback, pattern="^model_"))
    application.add_handler(conv_handler)
