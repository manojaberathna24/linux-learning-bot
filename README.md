# 🐧 Linux Learning Telegram Bot

An AI-powered Telegram bot that helps university students learn Linux system administration with a **real Linux terminal**, learning modules, quizzes, and lab sheet assistance.

## ✨ Features

- 🖥️ **Real Linux Terminal** - Execute actual Linux commands with persistent filesystem
- 📚 **10 Learning Modules** - From basics to advanced (25+ lessons)
- 💬 **AI Q&A** - Ask any Linux question
- 📄 **Lab Sheet Answers** - Upload PDF/images for solutions
- 🎮 **Interactive Quizzes** - Test your knowledge
- 📖 **Command Cheat Sheets** - Quick reference
- 📊 **Progress Tracking** - Monitor learning progress
- 👑 **Admin Dashboard** - For bot owner to monitor users

## 🚀 Quick Start

1. **Create Telegram Bot**
   - Message @BotFather on Telegram
   - `/newbot` → Follow instructions
   - Save bot token

2. **Create Supabase Database**
   - Sign up at [supabase.com](https://supabase.com) (FREE)
   - Create project
   - Run SQL from SETUP_GUIDE.md
   - Save URL and API key

3. **Install**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure**
   ```bash
   copy .env.example .env
   # Edit .env with your values
   ```

5. **Run**
   ```bash
   python bot.py
   ```

## 📖 Full Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup instructions
- **[Implementation Plan](https://github.com/...)** - Technical details

## 💡 Requirements

- Python 3.9+
- Telegram Bot Token
- Supabase account (FREE)
- OpenRouter API key for AI features (users provide their own)

## 🎯 For Students

```
/start      - Get started
/terminal   - Open Linux terminal
/learn      - Browse lessons
/ask <q>    - Ask Linux questions
/quiz       - Test knowledge
```

## 👑 For Admin (Bot Owner)

```
/admin         - View dashboard
/adminusers    - List all users
/adminstats    - See statistics
```

## 🌐 Deployment

Deploy for FREE on:
- Render.com (Recommended)
- Railway.app
- Your own PC

See SETUP_GUIDE.md for instructions.

## 📊 Tech Stack

- Python & python-telegram-bot
- Supabase (PostgreSQL)
- OpenRouter API (AI)
- Piston API (Command execution - FREE!)

## 📝 License

Free to use for educational purposes.

## 🤝 Contributing

Feel free to fork and improve!

---

**Built with ❤️ for Linux learners**

Share your bot: `t.me/your_bot_username`
