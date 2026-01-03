"""
Terminal Handler
Real Linux terminal with virtual filesystem
"""
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
from modules.supabase_client import db
from modules.virtual_fs import VirtualFileSystem
from datetime import datetime

# Store active terminal sessions
active_sessions = {}


async def terminal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start terminal mode"""
    user = update.effective_user
    
    # Check if user has terminal account
    account = await db.get_terminal_account(user.id)
    
    if not account:
        await update.message.reply_text(
            "🖥️ **Welcome to Linux Terminal!**\n\n"
            "You don't have a terminal account yet.\n"
            "Let's create one!\n\n"
            "Send me a username (lowercase, no spaces):",
            parse_mode="Markdown"
        )
        context.user_data['terminal_setup_stage'] = 'waiting_username'
        return
    
    # Start terminal session
    active_sessions[user.id] = {
        'start_time': datetime.now(),
        'username': account['linux_username']
    }
    
    current_dir = account['current_dir']
    username = account['linux_username']
    
    welcome = f"""
🖥️ **Linux Terminal Active**

Welcome back, {username}!

You're in: {current_dir}

Type any Linux command to get started.
Type `help` to see available commands.
Type `exit` to leave terminal mode.
"""
    
    await update.message.reply_text(welcome, parse_mode="Markdown")
    await db.log_activity(user.id, "terminal_start", f"Started terminal session")


async def handle_terminal_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle terminal account setup"""
    user = update.effective_user
    stage = context.user_data.get('terminal_setup_stage')
    
    if stage == 'waiting_username':
        username = update.message.text.strip().lower()
        
        # Validate username
        if not username.isalnum() or len(username) < 3:
            await update.message.reply_text(
                "❌ Invalid username. Use 3+ alphanumeric characters.\n"
                "Try again:"
            )
            return
        
        context.user_data['terminal_username'] = username
        context.user_data['terminal_setup_stage'] = 'waiting_password'
        
        await update.message.reply_text(
            f"✅ Username: {username}\n\n"
            f"Now send me a password (min 4 characters):"
        )
    
    elif stage == 'waiting_password':
        password = update.message.text.strip()
        
        if len(password) < 4:
            await update.message.reply_text(
                "❌ Password too short. Min 4 characters.\n"
                "Try again:"
            )
            return
        
        username = context.user_data['terminal_username']
        
        # Create terminal account and filesystem
        account = await db.create_terminal_account(user.id, username, password)
        await db.create_default_directories(user.id, username)
        
        # Delete password message
        try:
            await update.message.delete()
        except:
            pass
        
        # Clear setup data
        context.user_data.pop('terminal_setup_stage', None)
        context.user_data.pop('terminal_username', None)
        
        # Start terminal
        active_sessions[user.id] = {
            'start_time': datetime.now(),
            'username': username
        }
        
        await update.message.reply_text(
            f"✅ **Terminal Account Created!**\n\n"
            f"Username: {username}\n"
            f"Home: /home/{username}\n\n"
            f"🖥️ Terminal mode is now ACTIVE.\n"
            f"Type commands to get started!\n\n"
            f"Try: `ls -la`",
            parse_mode="Markdown"
        )
        
        await db.log_activity(user.id, "terminal_created", f"Created account: {username}")


async def handle_terminal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle commands in terminal mode"""
    user = update.effective_user
    
    # Check if in setup mode
    if user.id not in active_sessions and context.user_data.get('terminal_setup_stage'):
        await handle_terminal_setup(update, context)
        return
    
    # Check if in terminal mode
    if user.id not in active_sessions:
        return  # Not in terminal mode, ignore
    
    command = update.message.text.strip()
    
    # Check for exit
    if command.lower() == 'exit':
        session = active_sessions.pop(user.id)
        
        # Calculate session time
        duration = (datetime.now() - session['start_time']).total_seconds()
        await db.update_user_time(user.id, int(duration))
        
        await update.message.reply_text(
            "🖥️ Terminal session ended.\n"
            f"Session time: {int (duration/60)} minutes\n\n"
            f"Use /terminal to start again.",
            parse_mode="Markdown"
        )
        await db.log_activity(user.id, "terminal_end", f"Session duration: {int(duration)}s")
        return
    
    # Get user's terminal account
    account = await db.get_terminal_account(user.id)
    current_dir = account['current_dir']
    username = account['linux_username']
    
    # Execute command
    vfs = VirtualFileSystem(user.id, username)
    output, new_dir = await vfs.execute_command(command, current_dir)
    
    # Update current directory if changed
    if new_dir != current_dir:
        await db.update_current_dir(user.id, new_dir)
    
    # Check for clear command
    if output == "__CLEAR__":
        await update.message.reply_text(
            f"🖥️ **Terminal Cleared**\n\n"
            f"{username}@linux:{new_dir}$ ",
            parse_mode="Markdown"
        )
    elif output:
        # Send output
        response = f"```\n{output}\n```\n{username}@linux:{new_dir}$ "
        
        # Telegram message limit is 4096 chars
        if len(response) > 4000:
            response = f"```\n{output[:3900]}\n... (truncated)\n```\n{username}@linux:{new_dir}$ "
        
        await update.message.reply_text(response, parse_mode="Markdown")
    else:
        # No output, just show prompt
        await update.message.reply_text(
            f"{username}@linux:{new_dir}$ ",
            parse_mode="Markdown"
        )
    
    # Log activity every 5 commands
    if not hasattr(context.user_data, 'cmd_count'):
        context.user_data['cmd_count'] = 0
    context.user_data['cmd_count'] += 1
    
    if context.user_data['cmd_count'] % 5 == 0:
        await db.log_activity(user.id, "terminal_commands", f"Executed {context.user_data['cmd_count']} commands")


def setup_terminal_handlers(application):
    """Register terminal handlers"""
    application.add_handler(CommandHandler("terminal", terminal_command))
    
    # Handle all text messages when in terminal mode
    # This needs to be added with lower priority
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_terminal_command
        ),
        group=10  # Lower priority so other handlers run first
    )
