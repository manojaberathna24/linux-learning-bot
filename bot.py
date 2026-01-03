"""
Linux Learning Telegram Bot
Main bot file - Entry point
"""
import logging
from telegram.ext import Application
import config
from handlers import (
    setup_start_handlers,
    setup_settings_handlers,
    setup_admin_handlers,
    setup_terminal_handlers,
    setup_learn_handlers,
    setup_ask_handlers,
    setup_labsheet_handlers,
    setup_quiz_handlers,
    setup_cheatsheet_handlers
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def error_handler(update, context):
    """Log errors caused by updates"""
    logger.error(f"Exception while handling an update: {context.error}")


def main():
    """Start the bot"""
    # Validate configuration
    errors = config.validate_config()
    if errors:
        logger.error("Configuration errors:")
        for error in errors:
            logger.error(f"  - {error}")
        logger.error("\nPlease set up your .env file correctly.")
        logger.error("See .env.example for reference.")
        return
    
    logger.info("🐧 Starting Linux Learning Bot...")
    
    # Create application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Register all handlers
    logger.info("Registering handlers...")
    setup_start_handlers(application)
    setup_settings_handlers(application)
    setup_admin_handlers(application)
    setup_terminal_handlers(application)
    setup_learn_handlers(application)
    setup_ask_handlers(application)
    setup_labsheet_handlers(application)
    setup_quiz_handlers(application)
    setup_cheatsheet_handlers(application)
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    logger.info("✅ Bot is ready!")
    logger.info(f"👑 Admin ID: {config.ADMIN_TELEGRAM_ID}")
    logger.info(f"🌐 Piston API: {config.PISTON_API_URL}")
    logger.info("🚀 Starting polling...")
    
    # Start the bot
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
