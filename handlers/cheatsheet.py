"""
Cheat Sheet Handler
Quick Linux command reference
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
import json
import os


async def cheatsheet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show cheat sheet categories"""
    try:
        # Load cheat sheets
        with open("data/cheatsheets.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        keyboard = []
        for category in data["categories"]:
            keyboard.append([InlineKeyboardButton(
                category["name"],
                callback_data=f"cheat_{data['categories'].index(category)}"
            )])
        
        text = "📖 **Linux Command Cheat Sheets**\n\nChoose a category:"
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Error loading cheat sheets: {str(e)}")


async def cheatsheet_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show commands for a category"""
    query = update.callback_query
    await query.answer()
    
    try:
        category_index = int(query.data.replace("cheat_", ""))
        
        with open("data/cheatsheets.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        category = data["categories"][category_index]
        
        text = f"{category['name']}\n\n"
        
        for cmd in category["commands"]:
            text += f"**{cmd['cmd']}** - {cmd['desc']}\n"
            text += f"`{cmd['example']}`\n\n"
        
        text += "\nUse /cheatsheet to see more categories"
        
        # Limit text length
        if len(text) > 4000:
            text = text[:3900] + "\n\n... (truncated)\n\nUse /cheatsheet"
        
        await query.edit_message_text(text, parse_mode="Markdown")
    
    except Exception as e:
        await query.edit_message_text(f"❌ Error: {str(e)}")


def setup_cheatsheet_handlers(application):
    """Register cheatsheet handlers"""
    application.add_handler(CommandHandler("cheatsheet", cheatsheet_command))
    application.add_handler(CallbackQueryHandler(cheatsheet_callback, pattern="^cheat_"))
