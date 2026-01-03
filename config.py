"""
Configuration module for Linux Learning Bot
Loads environment variables and provides config access
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Admin Configuration - Only this user ID can access admin features
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))

# Piston API (FREE - No API key needed!)
PISTON_API_URL = "https://emkc.org/api/v2/piston"

# OpenRouter API Base URL
OPENROUTER_API_URL = "https://openrouter.ai/api/v1"

# Available AI Models for users to choose
AVAILABLE_MODELS = [
    {"id": "meta-llama/llama-3.1-8b-instruct:free", "name": "Llama 3.1 8B (Free)"},
    {"id": "google/gemini-2.0-flash-exp:free", "name": "Gemini 2.0 Flash (Free)"},
    {"id": "qwen/qwen-2-7b-instruct:free", "name": "Qwen 2 7B (Free)"},
    {"id": "microsoft/phi-3-mini-128k-instruct:free", "name": "Phi-3 Mini (Free)"},
    {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini"},
    {"id": "anthropic/claude-3-haiku", "name": "Claude 3 Haiku"},
]

# Default model if user hasn't selected one
DEFAULT_MODEL = "meta-llama/llama-3.1-8b-instruct:free"


def validate_config():
    """Check if required configuration is set"""
    errors = []
    
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is not set")
    
    if not SUPABASE_URL:
        errors.append("SUPABASE_URL is not set")
    
    if not SUPABASE_KEY:
        errors.append("SUPABASE_KEY is not set")
    
    if ADMIN_TELEGRAM_ID == 0:
        errors.append("ADMIN_TELEGRAM_ID is not set")
    
    return errors
