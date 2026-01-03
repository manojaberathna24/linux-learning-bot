"""
Start Command Handler
Welcome message and main menu
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from modules.supabase_client import db


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Register/update user in database
    await db.get_or_create_user(user.id, user.username)
    
    welcome_text = f"""
🐧 **Welcome to Linux Learning Bot!**

Hi {user.first_name}! I'm your Linux System Administration learning assistant.

**What I can help you with:**
🖥️ Practice real Linux commands in a safe terminal
📚 Learn from Basic to Advanced modules
💬 Ask any Linux question (AI powered)
📄 Get answers for lab sheets
🎮 Test your knowledge with quizzes
📖 Quick command references

**Get Started:**
1. First, set up your API key: /settings
2. Then explore: /learn or /terminal

Need help? Type /help
"""
    
    keyboard = [
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")],
        [InlineKeyboardButton("🖥️ Terminal", callback_data="menu_terminal"),
         InlineKeyboardButton("📚 Learn", callback_data="menu_learn")],
        [InlineKeyboardButton("💬 Ask AI", callback_data="menu_ask"),
         InlineKeyboardButton("📖 Cheat Sheets", callback_data="menu_cheatsheet")],
        [InlineKeyboardButton("🎮 Quiz", callback_data="menu_quiz"),
         InlineKeyboardButton("📊 My Progress", callback_data="menu_progress")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📖 **Bot Commands Guide**

**Main Commands:**
/start - Start the bot and show main menu
/settings - Configure API key and AI model
/terminal - Open Linux terminal
/learn - Browse learning modules
/ask <question> - Ask Linux question
/quiz - Test your knowledge
/cheat sheet - Quick command reference
/progress - View your learning progress

**Terminal Commands:**
Once in terminal mode, you can use real Linux commands like:
• ls, cd, pwd, mkdir, touch
• cat, echo, chmod, cp, mv, rm
• And many more!

Type `help` in terminal for full command list.
Type `exit` to leave terminal mode.

**Admin Commands (Owner Only):**
/admin - View admin dashboard

Need more help? Just ask me any Linux question!
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu button callbacks"""
    query = update.callback_query
    await query.answer()
    
    action = query.data.replace("menu_", "")
    
    responses = {
        "settings": "⚙️ Use /settings to configure your API key and model",
        "terminal": "🖥️ Use /terminal to start terminal mode",
        "learn": "📚 Use /learn to browse learning modules",
        "ask": "💬 Use /ask <question> to ask anything about Linux",
        "cheatsheet": "📖 Use /cheatsheet to view command references",
        "quiz": "🎮 Use /quiz to test your knowledge",
        "progress": "📊 Use /progress to view your progress"
    }
    
    response = responses.get(action, "Use the command to access this feature")
    await query.edit_message_text(response)


def setup_start_handlers(application):
    """Register start-related handlers"""
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
