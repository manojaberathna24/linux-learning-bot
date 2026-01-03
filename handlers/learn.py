"""
Learn Handler
Browse and view learning modules
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from modules.learning_content import LEARNING_MODULES, get_module, get_lesson
from modules.supabase_client import db


async def learn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show learning modules"""
    keyboard = []
    
    for module in LEARNING_MODULES:
        button_text = f"{module['title']} ({len(module['lessons'])} lessons)"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"learn_module_{module['id']}")])
    
    text = "📚 **Linux Learning Modules**\n\nChoose a module to start learning:"
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def learn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle learning menu callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("learn_module_"):
        module_id = int(data.replace("learn_module_", ""))
        await show_module(query, module_id)
    
    elif data.startswith("learn_lesson_"):
        parts = data.replace("learn_lesson_", "").split("_")
        module_id = int(parts[0])
        lesson_id = int(parts[1])
        await show_lesson(query, module_id, lesson_id)
    
    elif data.startswith("learn_complete_"):
        parts = data.replace("learn_complete_", "").split("_")
        module_id = int(parts[0])
        lesson_id = int(parts[1])
        await mark_complete(query, module_id, lesson_id)
    
    elif data == "learn_back":
        await show_modules(query)


async def show_modules(query):
    """Show module list"""
    keyboard = []
    
    for module in LEARNING_MODULES:
        button_text = f"{module['title']} ({len(module['lessons'])} lessons)"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"learn_module_{module['id']}")])
    
    text = "📚 **Linux Learning Modules**\n\nChoose a module to start learning:"
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def show_module(query, module_id: int):
    """Show module details and lessons"""
    module = get_module(module_id)
    
    if not module:
        await query.edit_message_text("Module not found.")
        return
    
    text = f"{module['title']}\n\n{module['description']}\n\n**Lessons:**\n"
    
    keyboard = []
    for i, lesson in enumerate(module['lessons'], 1):
        button_text = f"{i}. {lesson['title']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"learn_lesson_{module_id}_{lesson['id']}")])
    
    keyboard.append([InlineKeyboardButton("« Back to Modules", callback_data="learn_back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def show_lesson(query, module_id: int, lesson_id: int):
    """Show lesson content"""
    lesson = get_lesson(module_id, lesson_id)
    module = get_module(module_id)
    
    if not lesson or not module:
        await query.edit_message_text("Lesson not found.")
        return
    
    text = f"**{module['title']}**\n\n**Lesson: {lesson['title']}**\n\n{lesson['content']}"
    
    keyboard = [
        [InlineKeyboardButton("✅ Mark as Complete", callback_data=f"learn_complete_{module_id}_{lesson_id}")],
        [InlineKeyboardButton("« Back to Module", callback_data=f"learn_module_{module_id}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Telegram message limit
    if len(text) > 4000:
        text = text[:3900] + "\n\n... (content truncated)"
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def mark_complete(query, module_id: int, lesson_id: int):
    """Mark lesson as complete"""
    user = query.from_user
    
    await db.update_progress(user.id, module_id, lesson_id, completed=True)
    await db.log_activity(user.id, "lesson_complete", f"Module {module_id}, Lesson {lesson_id}")
    
    await query.answer("✅ Marked as complete!")
    
    # Show next lesson or back to module
    module = get_module(module_id)
    if module:
        current_index = next((i for i, l in enumerate(module['lessons']) if l['id'] == lesson_id), -1)
        if current_index >= 0 and current_index < len(module['lessons']) - 1:
            next_lesson_id = module['lessons'][current_index + 1]['id']
            await show_lesson(query, module_id, next_lesson_id)
        else:
            await show_module(query, module_id)


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's learning progress"""
    user = update.effective_user
    
    progress = await db.get_user_progress(user.id)
    
    if not progress:
        await update.message.reply_text(
            "📊 **Your Progress**\n\n"
            "You haven't started any lessons yet.\n\n"
            "Use /learn to get started!",
            parse_mode="Markdown"
        )
        return
    
    # Count completed lessons per module
    module_progress = {}
    for p in progress:
        if p['completed']:
            module_id = p['module_id']
            if module_id not in module_progress:
                module_progress[module_id] = 0
            module_progress[module_id] += 1
    
    text = "📊 **Your Learning Progress**\n\n"
    
    for module in LEARNING_MODULES:
        completed = module_progress.get(module['id'], 0)
        total = len(module['lessons'])
        percentage = (completed / total * 100) if total > 0 else 0
        
        bar = "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10))
        
        text += f"{module['title']}\n"
        text += f"{bar} {completed}/{total} ({percentage:.0f}%)\n\n"
    
    text += f"\nTotal Completed: {sum(module_progress.values())}"
    
    await update.message.reply_text(text, parse_mode="Markdown")


def setup_learn_handlers(application):
    """Register learn handlers"""
    application.add_handler(CommandHandler("learn", learn_command))
    application.add_handler(CommandHandler("progress", progress_command))
    application.add_handler(CallbackQueryHandler(learn_callback, pattern="^learn_"))
