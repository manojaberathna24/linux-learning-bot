# 🐧 Linux Learning Bot - Setup Guide

Complete step-by-step instructions to get your bot running!

---

## 📋 Prerequisites

- Python 3.9 or higher
- Internet connection
- 10 minutes of time  

---

## Step 1: Create Telegram Bot

### 1.1 Open Telegram
Open Telegram and search for **@BotFather**

### 1.2 Create Bot
Send these commands:
```
/newbot
```

### 1.3 Follow Instructions
- Enter bot name (e.g., "Linux Learning Bot")
- Enter username (must end with 'bot', e.g., "linux_learning_bot")

### 1.4 Save Token
BotFather will give you a token like:
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```
**Save this token! You'll need it later.**

### 1.5 Get Your Telegram ID
Search for **@userinfobot** and send `/start`  
It will show your Telegram ID (a number like `123456789`)  
**Save this ID - this makes you the admin!**

---

## Step 2: Create Supabase Database (FREE)

### 2.1 Sign Up
Go to: https://supabase.com  
Click "Start your project" → Sign up with GitHub/Google (FREE)

### 2.2 Create Project
- Click "New Project"
- Name: `linux-learning-bot`
- Database Password: Create a strong password (save it!)
- Region: Choose closest to you
- Click "Create new project" (wait 2-3 minutes)

### 2.3 Create Tables
Go to **SQL Editor** (left sidebar) and run these commands:

```sql
-- Users table
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  telegram_id BIGINT UNIQUE NOT NULL,
  username TEXT,
  openrouter_key TEXT,
  selected_model TEXT,
  total_time_seconds INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_seen TIMESTAMP WITH TIME ZONE
);

-- Terminal accounts table
CREATE TABLE terminal_accounts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  telegram_id BIGINT UNIQUE NOT NULL,
  linux_username TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  current_dir TEXT DEFAULT '/home',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Virtual files table
CREATE TABLE virtual_files (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  telegram_id BIGINT NOT NULL,
  path TEXT NOT NULL,
  parent_path TEXT NOT NULL,
  name TEXT NOT NULL,
  is_directory BOOLEAN DEFAULT FALSE,
  content TEXT,
  permissions TEXT DEFAULT '644',
  size INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  modified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Progress table
CREATE TABLE progress (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  telegram_id BIGINT NOT NULL,
  module_id INTEGER NOT NULL,
  lesson_id INTEGER NOT NULL,
  completed BOOLEAN DEFAULT FALSE,
  quiz_score INTEGER,
  completed_at TIMESTAMP WITH TIME ZONE
);

-- Activity log table
CREATE TABLE activity_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  telegram_id BIGINT NOT NULL,
  activity_type TEXT NOT NULL,
  details TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.4 Get Project URL and Key
- Go to **Settings** → **API**
- Copy **Project URL** (e.g., `https://abcdefghijk.supabase.co`)
- Copy **anon public** key (long string starting with `eyJ...`)
- **Save both!**

---

## Step 3: Get OpenRouter API Key (FREE Credits!)

This is for YOUR testing. Users will use their own keys.

### 3.1 Sign Up
Go to: https://openrouter.ai  
Click "Sign In" → Sign up with Google/GitHub (FREE)

### 3.2 Get Free Credits
New accounts get FREE credits to test!

### 3.3 Create API Key
- Go to **Keys** section
- Click "Create Key"
- Name it "Linux Bot Testing"
- Copy the key (starts with `sk-or-...`)
- **Save it!**

---

## Step 4: Install Bot

### 4.1 Install Python
**Windows:**
- Download from: https://www.python.org/downloads/
- During install, CHECK ✅ "Add Python to PATH"

**Check installation:**
```bash
python --version
```

### 4.2 Install Dependencies
Open terminal in bot folder:
```bash
cd "C:\Users\Manoj Aberathna\Desktop\teligrm bot"
pip install -r requirements.txt
```

Wait for installation to complete.

---

## Step 5: Configure Bot

### 5.1 Create .env File
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

### 5.2 Edit .env File
Open `.env` with Notepad and fill in:

```env
# Telegram Bot Token (from @BotFather)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Your Telegram ID (from @userinfobot)
ADMIN_TELEGRAM_ID=123456789
```

**Replace with YOUR actual values!**

Save and close.

---

## Step 6: Run Bot

### 6.1 Start Bot
```bash
python bot.py
```

You should see:
```
🐧 Starting Linux Learning Bot...
✅ Bot is ready!
👑 Admin ID: 123456789
🚀 Starting polling...
```

### 6.2 Test Bot
Open Telegram and find your bot, send:
```
/start
```

You should get a welcome message! 🎉

### 6.3 Setup Your Account
1. Send `/settings`
2. Click "Set API Key"
3. Send your OpenRouter API key
4. Select a FREE model (Llama or Gemini)

### 6.4 Try Terminal
Send `/terminal` and create your Linux account!

---

## 🚀 Deploying Bot (24/7 Hosting)

To keep bot running 24/7, use a FREE hosting service:

### Option 1: Render.com (Recommended - FREE)

1. Push code to GitHub
2. Go to: https://render.com
3. Sign up → New → Web Service
4. Connect your GitHub repo
5. Settings:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
6. Add Environment Variables (same as .env)
7. Click "Create Web Service"

### Option 2: Railway.app (FREE)

1. Go to: https://railway.app
2. Sign up → New Project → Deploy from GitHub
3. Select your repo
4. Add environment variables
5. Deploy!

### Option 3: Your Own PC (Always On)

Just keep the terminal running with `python bot.py`  
⚠️ PC must stay on and connected to internet!

---

## 📲 Share Your Bot

Once deployed, share your bot:
1. Get bot username (e.g., `@linux_learning_bot`)
2. Share link: `t.me/linux_learning_bot`
3. Anyone can search and use it!

---

## 🔧 Admin Commands (YOU ONLY)

As the admin, you have special commands:

```
/admin          - View dashboard
/adminusers     - List all users
/adminstats     - Detailed statistics
```

Regular users can't access these!

---

## 🐛 Troubleshooting

### Bot doesn't start
- Check `.env` file has correct values
- Make sure all dependencies installed: `pip install -r requirements.txt`

### "Invalid token" error
- Double-check TELEGRAM_BOT_TOKEN in `.env`
- No extra spaces or quotes

### Database errors
- Verify SUPABASE_URL and SUPABASE_KEY
- Check tables were created in Supabase SQL Editor

### API key errors (users)
- Users need their own OpenRouter API key
- Guide them to: https://openrouter.ai

---

## 🎯 Next Steps

1. ✅ Bot is running
2. Test all features:
   - `/terminal` - Try Linux commands
   - `/learn` - Browse modules
   - `/ask how to use ls command?`
   - Upload a lab sheet image
   - `/quiz` - Test knowledge
3. Share with students!
4. Monitor usage with `/admin`

---

## 💡 Tips

- **Free Models**: Recommend users use Gemini 2.0 Flash or Llama 3.1 (FREE!)
- **Backups**: Supabase auto-backups your data
- **Scaling**: FREE tier supports hundreds of users
- **Updates**: Pull latest code from GitHub and restart bot

---

## 📞 Support

If you have issues:
1. Check error messages in terminal
2. Verify configuration
3. Check Supabase dashboard for database issues

---

**Congratulations! Your Linux Learning Bot is ready! 🎉**

Share it with students and help them learn Linux! 🐧
