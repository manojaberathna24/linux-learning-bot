"""
Quiz Handler
Test Linux knowledge with MCQs
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from modules.supabase_client import db
import random

# Quiz questions database
QUIZ_QUESTIONS = [
    {
        "question": "Which command lists files in a directory?",
        "options": ["ls", "cd", "pwd", "mkdir"],
        "correct": 0
    },
    {
        "question": "What does 'cd ..' do?",
        "options": ["Create directory", "Go to home", "Go up one level", "List files"],
        "correct": 2
    },
    {
        "question": "Which command creates an empty file?",
        "options": ["mkdir", "rm", "touch", "cat"],
        "correct": 2
    },
    {
        "question": "What does 'chmod 755' mean?",
        "options": ["Delete file", "rwxr-xr-x permissions", "rw-r--r-- permissions", "Change owner"],
        "correct": 1
    },
    {
        "question": "Which command shows disk space usage?",
        "options": ["du", "df", "free", "all of above"],
        "correct": 1
    },
    {
        "question": "What is the purpose of 'grep'?",
        "options": ["Delete files", "Search text", "Change permissions", "Copy files"],
        "correct": 1
    },
    {
        "question": "Which command removes a directory?",
        "options": ["rm -r", "rmdir", "rm -rf", "all of above"],
        "correct": 3
    },
    {
        "question": "What does 'sudo' do?",
        "options": ["Super user do", "System update", "Show disk", "Stop daemon"],
        "correct": 0
    },
    {
        "question": "Which file contains user passwords?",
        "options": ["/etc/passwd", "/etc/shadow", "/etc/group", "/etc/hosts"],
        "correct": 1
    },
    {
        "question": "What command shows running processes?",
        "options": ["ls", "ps", "top", "both b and c"],
        "correct": 3
    }
]

# Store active quiz sessions
quiz_sessions = {}


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a quiz"""
    user = update.effective_user
    
    # Initialize quiz session
    questions = random.sample(QUIZ_QUESTIONS, min(5, len(QUIZ_QUESTIONS)))
    quiz_sessions[user.id] = {
        "questions": questions,
        "current": 0,
        "score": 0
    }
    
    await show_question(update.message, user.id)


async def show_question(message, user_id: int):
    """Show current quiz question"""
    session = quiz_sessions.get(user_id)
    
    if not session:
        await message.reply_text("❌ No active quiz. Use /quiz to start!")
        return
    
    current = session["current"]
    questions = session["questions"]
    
    if current >= len(questions):
        # Quiz finished
        await finish_quiz(message, user_id)
        return
    
    question = questions[current]
    
    text = f"🎮 **Quiz Question {current + 1}/{len(questions)}**\n\n"
    text += f"{question['question']}\n\n"
    text += f"Score: {session['score']}/{current}"
    
    keyboard = []
    for i, option in enumerate(question['options']):
        keyboard.append([InlineKeyboardButton(
            f"{chr(65+i)}. {option}",
            callback_data=f"quiz_answer_{i}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle quiz answer"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    session = quiz_sessions.get(user.id)
    
    if not session:
        await query.edit_message_text("❌ Quiz session expired. Use /quiz to start again!")
        return
    
    answer = int(query.data.replace("quiz_answer_", ""))
    current = session["current"]
    question = session["questions"][current]
    
    is_correct = (answer == question["correct"])
    
    if is_correct:
        session["score"] += 1
        result_text = "✅ Correct!"
    else:
        correct_answer = question["options"][question["correct"]]
        result_text = f"❌ Wrong! Correct answer: {correct_answer}"
    
    # Move to next question
    session["current"] += 1
    
    await query.edit_message_text(
        f"{result_text}\n\nScore: {session['score']}/{current+1}",
        parse_mode="Markdown"
    )
    
    # Show next question after a short delay
    import asyncio
    await asyncio.sleep(1.5)
    await show_question(query.message, user.id)


async def finish_quiz(message, user_id: int):
    """Finish quiz and show results"""
    session = quiz_sessions.pop(user_id, None)
    
    if not session:
        return
    
    score = session["score"]
    total = len(session["questions"])
    percentage = (score / total * 100) if total > 0 else 0
    
    # Save quiz score
    await db.update_quiz_score(user_id, 0, score)  # Module 0 = general quiz
    await db.log_activity(user_id, "quiz_complete", f"Score: {score}/{total}")
    
    # Determine grade
    if percentage >= 80:
        grade = "🌟 Excellent!"
    elif percentage >= 60:
        grade = "👍 Good!"
    elif percentage >= 40:
        grade = "📚 Keep learning!"
    else:
        grade = "💪 Practice more!"
    
    result_text = f"""
🎮 **Quiz Completed!**

Score: {score}/{total} ({percentage:.0f}%)

{grade}

Use /quiz to try again!
Use /learn to improve your knowledge.
"""
    
    await message.reply_text(result_text, parse_mode="Markdown")


def setup_quiz_handlers(application):
    """Register quiz handlers"""
    application.add_handler(CommandHandler("quiz", quiz_command))
    application.add_handler(CallbackQueryHandler(quiz_callback, pattern="^quiz_answer_"))
