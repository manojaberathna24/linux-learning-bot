"""
Admin Dashboard Handler
Only accessible to bot owner (ADMIN_TELEGRAM_ID)
"""
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from modules.supabase_client import db
import config
from datetime import datetime, timezone


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == config.ADMIN_TELEGRAM_ID


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin dashboard"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ Access denied. This command is for the bot owner only.")
        return
    
    # Get statistics
    stats = await db.get_user_stats()
    all_users = await db.get_all_users()
    
    # Format top users by time
    sorted_users = sorted(all_users, key=lambda u: u.get("total_time_seconds", 0), reverse=True)[:5]
    
    top_users_text = ""
    for i, u in enumerate(sorted_users, 1):
        username = u.get("username") or f"User{u['telegram_id']}"
        time_seconds = u.get("total_time_seconds", 0)
        hours = time_seconds // 3600
        minutes = (time_seconds % 3600) // 60
        top_users_text += f"{i}. @{username} - {hours}h {minutes}m\n"
    
    if not top_users_text:
        top_users_text = "No users yet"
    
    dashboard_text = f"""
👑 **ADMIN DASHBOARD**
━━━━━━━━━━━━━━━━━━

📊 **Statistics:**
• Total Users: {stats['total_users']}
• Active Today: {stats['active_today']}
• Total Usage Time: {stats['total_time_hours']}h

🏆 **Top Users (by time):**
{top_users_text}

**Commands:**
/admin users - List all users
/admin user <telegram_id> - View specific user
/admin stats - Detailed statistics
"""
    
    await update.message.reply_text(dashboard_text, parse_mode="Markdown")


async def admin_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all users"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ Access denied.")
        return
    
    all_users = await db.get_all_users()
    
    if not all_users:
        await update.message.reply_text("No users found.")
        return
    
    # Create user list (max 20 at a time)
    user_list = "👥 **All Users:**\n\n"
    for u in all_users[:20]:
        username = u.get("username") or "No username"
        telegram_id = u["telegram_id"]
        created = u.get("created_at", "Unknown")
        
        # Parse date
        try:
            date_obj = datetime.fromisoformat(created.replace("Z", "+00:00"))
            date_str = date_obj.strftime("%Y-%m-%d")
        except:
            date_str = "Unknown"
        
        user_list += f"• @{username} (ID: {telegram_id})\n"
        user_list += f"  Joined: {date_str}\n\n"
    
    if len(all_users) > 20:
        user_list += f"\n... and {len(all_users) - 20} more users"
    
    await update.message.reply_text(user_list, parse_mode="Markdown")


async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detailed statistics"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ Access denied.")
        return
    
    all_users = await db.get_all_users()
    
    # Calculate stats
    total_users = len(all_users)
    users_with_api_key = sum(1 for u in all_users if u.get("openrouter_key"))
    
    # Count active in different time periods
    now = datetime.now(timezone.utc)
    active_today = 0
    active_week = 0
    
    for u in all_users:
        last_seen = u.get("last_seen")
        if last_seen:
            try:
                last_seen_dt = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
                hours_ago = (now - last_seen_dt).total_seconds() / 3600
                
                if hours_ago < 24:
                    active_today += 1
                if hours_ago < 168:  # 7 days
                    active_week += 1
            except:
                pass
    
    total_time = sum(u.get("total_time_seconds", 0) for u in all_users)
    avg_time_per_user = (total_time / total_users) if total_users > 0 else 0
    
    stats_text = f"""
📊 **Detailed Statistics**

**User Metrics:**
• Total Users: {total_users}
• Users with API Key: {users_with_api_key}
• Active Today: {active_today}
• Active This Week: {active_week}
• Setup Rate: {(users_with_api_key/total_users*100) if total_users > 0 else 0:.1f}%

**Usage Metrics:**
• Total Time: {total_time/3600:.1f} hours
• Average per User: {avg_time_per_user/3600:.1f} hours

**Engagement:**
• Daily Active Rate: {(active_today/total_users*100) if total_users > 0 else 0:.1f}%
• Weekly Active Rate: {(active_week/total_users*100) if total_users > 0 else 0:.1f}%
"""
    
    await update.message.reply_text(stats_text, parse_mode="Markdown")


def setup_admin_handlers(application):
    """Register admin handlers"""
    application.add_handler(CommandHandler("admin", admin_command))
    # These can be triggered by /admin users or /admin stats
    # For simplicity, using separate commands
    application.add_handler(CommandHandler("adminusers", admin_users_command))
    application.add_handler(CommandHandler("adminstats", admin_stats_command))
