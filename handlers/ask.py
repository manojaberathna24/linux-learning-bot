"""
Ask Handler
AI-powered Linux Q&A
"""
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from modules.supabase_client import db
from modules.ai_client import ai


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ask command"""
    user = update.effective_user
    
    # Check if user provided a question
    if not context.args:
        await update.message.reply_text(
            "💬 **Ask Linux Questions**\n\n"
            "Usage: `/ask <your question>`\n\n"
            "Example:\n"
            "`/ask how do I list hidden files in Linux?`\n"
            "`/ask what is chmod command?`\n"
            "`/ask how to check disk space?`",
            parse_mode="Markdown"
        )
        return
    
    question = " ".join(context.args)
    
    # Get user settings
    settings = await db.get_user_settings(user.id)
    api_key = settings.get("openrouter_key")
    model = settings.get("selected_model")
    
    if not api_key:
        await update.message.reply_text(
            "❌ Please set up your API key first.\n\n"
            "Use /settings to configure your OpenRouter API key.",
            parse_mode="Markdown"
        )
        return
    
    # Send thinking message
    thinking_msg = await update.message.reply_text("🤔 Thinking...")
    
    # Get AI response
    response = await ai.ask_linux(api_key, model, question)
    
    # Delete thinking message
    await thinking_msg.delete()
    
    # Send response
    await update.message.reply_text(response, parse_mode="Markdown")
    
    # Log activity
    await db.log_activity(user.id, "ai_question", question[:100])


def setup_ask_handlers(application):
    """Register ask handlers"""
    application.add_handler(CommandHandler("ask", ask_command))
