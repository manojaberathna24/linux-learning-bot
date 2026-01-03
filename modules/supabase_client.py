"""
Supabase Database Client
Handles all database operations for users, progress, terminal accounts, and virtual filesystem
"""
from supabase import create_client, Client
from datetime import datetime, timezone
import hashlib
import config


class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    
    # ==================== USER OPERATIONS ====================
    
    async def get_or_create_user(self, telegram_id: int, username: str = None) -> dict:
        """Get existing user or create new one"""
        # Try to find existing user
        result = self.client.table("users").select("*").eq("telegram_id", telegram_id).execute()
        
        if result.data:
            # Update last seen
            self.client.table("users").update({
                "last_seen": datetime.now(timezone.utc).isoformat()
            }).eq("telegram_id", telegram_id).execute()
            return result.data[0]
        
        # Create new user
        new_user = {
            "telegram_id": telegram_id,
            "username": username,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_seen": datetime.now(timezone.utc).isoformat(),
            "total_time_seconds": 0
        }
        result = self.client.table("users").insert(new_user).execute()
        return result.data[0] if result.data else None
    
    async def update_user_api_key(self, telegram_id: int, api_key: str) -> bool:
        """Save user's OpenRouter API key"""
        result = self.client.table("users").update({
            "openrouter_key": api_key
        }).eq("telegram_id", telegram_id).execute()
        return len(result.data) > 0
    
    async def update_user_model(self, telegram_id: int, model_id: str) -> bool:
        """Save user's selected AI model"""
        result = self.client.table("users").update({
            "selected_model": model_id
        }).eq("telegram_id", telegram_id).execute()
        return len(result.data) > 0
    
    async def get_user_settings(self, telegram_id: int) -> dict:
        """Get user's API key and model settings"""
        result = self.client.table("users").select("openrouter_key, selected_model").eq("telegram_id", telegram_id).execute()
        if result.data:
            return result.data[0]
        return {"openrouter_key": None, "selected_model": None}
    
    async def update_user_time(self, telegram_id: int, seconds: int) -> bool:
        """Add time to user's total usage time"""
        # Get current time
        result = self.client.table("users").select("total_time_seconds").eq("telegram_id", telegram_id).execute()
        current_time = result.data[0].get("total_time_seconds", 0) if result.data else 0
        
        # Update with new time
        self.client.table("users").update({
            "total_time_seconds": current_time + seconds,
            "last_seen": datetime.now(timezone.utc).isoformat()
        }).eq("telegram_id", telegram_id).execute()
        return True
    
    # ==================== ADMIN OPERATIONS ====================
    
    async def get_all_users(self) -> list:
        """Get all users for admin dashboard"""
        result = self.client.table("users").select("*").order("created_at", desc=True).execute()
        return result.data if result.data else []
    
    async def get_user_stats(self) -> dict:
        """Get overall statistics for admin"""
        users = await self.get_all_users()
        total_users = len(users)
        
        # Calculate active today
        today = datetime.now(timezone.utc).date()
        active_today = sum(1 for u in users if u.get("last_seen") and 
                         datetime.fromisoformat(u["last_seen"].replace("Z", "+00:00")).date() == today)
        
        # Total time across all users
        total_time = sum(u.get("total_time_seconds", 0) for u in users)
        
        return {
            "total_users": total_users,
            "active_today": active_today,
            "total_time_hours": round(total_time / 3600, 1)
        }
    
    async def get_user_activity(self, telegram_id: int) -> list:
        """Get activity log for a specific user"""
        result = self.client.table("activity_log").select("*").eq("telegram_id", telegram_id).order("created_at", desc=True).limit(50).execute()
        return result.data if result.data else []
    
    async def log_activity(self, telegram_id: int, activity_type: str, details: str = None):
        """Log user activity for admin tracking"""
        self.client.table("activity_log").insert({
            "telegram_id": telegram_id,
            "activity_type": activity_type,
            "details": details,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
    
    # ==================== TERMINAL ACCOUNT OPERATIONS ====================
    
    async def get_terminal_account(self, telegram_id: int) -> dict:
        """Get user's terminal account"""
        result = self.client.table("terminal_accounts").select("*").eq("telegram_id", telegram_id).execute()
        return result.data[0] if result.data else None
    
    async def create_terminal_account(self, telegram_id: int, linux_username: str, password: str) -> dict:
        """Create a new terminal account for user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        account = {
            "telegram_id": telegram_id,
            "linux_username": linux_username,
            "password_hash": password_hash,
            "current_dir": f"/home/{linux_username}",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = self.client.table("terminal_accounts").insert(account).execute()
        return result.data[0] if result.data else None
    
    async def verify_terminal_password(self, telegram_id: int, password: str) -> bool:
        """Verify terminal account password"""
        account = await self.get_terminal_account(telegram_id)
        if not account:
            return False
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return account["password_hash"] == password_hash
    
    async def update_current_dir(self, telegram_id: int, new_dir: str):
        """Update user's current working directory"""
        self.client.table("terminal_accounts").update({
            "current_dir": new_dir
        }).eq("telegram_id", telegram_id).execute()
    
    # ==================== VIRTUAL FILESYSTEM OPERATIONS ====================
    
    async def create_default_directories(self, telegram_id: int, linux_username: str):
        """Create default home directory structure for new user"""
        directories = [
            f"/home/{linux_username}",
            f"/home/{linux_username}/Desktop",
            f"/home/{linux_username}/Documents",
            f"/home/{linux_username}/Downloads",
            f"/home/{linux_username}/Pictures",
            f"/home/{linux_username}/Projects",
        ]
        
        for dir_path in directories:
            await self.create_file_entry(telegram_id, dir_path, is_directory=True)
    
    async def create_file_entry(self, telegram_id: int, path: str, is_directory: bool = False, 
                                content: str = None, permissions: str = "755"):
        """Create a file or directory entry in virtual filesystem"""
        name = path.split("/")[-1]
        parent_path = "/".join(path.split("/")[:-1]) or "/"
        
        entry = {
            "telegram_id": telegram_id,
            "path": path,
            "parent_path": parent_path,
            "name": name,
            "is_directory": is_directory,
            "content": content,
            "permissions": permissions,
            "size": len(content) if content else 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "modified_at": datetime.now(timezone.utc).isoformat()
        }
        self.client.table("virtual_files").insert(entry).execute()
    
    async def get_directory_contents(self, telegram_id: int, path: str) -> list:
        """List contents of a directory"""
        result = self.client.table("virtual_files").select("*").eq("telegram_id", telegram_id).eq("parent_path", path).execute()
        return result.data if result.data else []
    
    async def get_file(self, telegram_id: int, path: str) -> dict:
        """Get a specific file or directory"""
        result = self.client.table("virtual_files").select("*").eq("telegram_id", telegram_id).eq("path", path).execute()
        return result.data[0] if result.data else None
    
    async def update_file_content(self, telegram_id: int, path: str, content: str):
        """Update file content"""
        self.client.table("virtual_files").update({
            "content": content,
            "size": len(content),
            "modified_at": datetime.now(timezone.utc).isoformat()
        }).eq("telegram_id", telegram_id).eq("path", path).execute()
    
    async def delete_file(self, telegram_id: int, path: str):
        """Delete a file or directory"""
        # Delete the file/directory and all children if directory
        self.client.table("virtual_files").delete().eq("telegram_id", telegram_id).like("path", f"{path}%").execute()
    
    async def update_file_permissions(self, telegram_id: int, path: str, permissions: str):
        """Update file permissions"""
        self.client.table("virtual_files").update({
            "permissions": permissions,
            "modified_at": datetime.now(timezone.utc).isoformat()
        }).eq("telegram_id", telegram_id).eq("path", path).execute()
    
    # ==================== PROGRESS TRACKING ====================
    
    async def get_user_progress(self, telegram_id: int) -> list:
        """Get user's learning progress"""
        result = self.client.table("progress").select("*").eq("telegram_id", telegram_id).execute()
        return result.data if result.data else []
    
    async def update_progress(self, telegram_id: int, module_id: int, lesson_id: int, completed: bool = True):
        """Update user's progress on a lesson"""
        # Check if entry exists
        result = self.client.table("progress").select("*").eq("telegram_id", telegram_id).eq("module_id", module_id).eq("lesson_id", lesson_id).execute()
        
        if result.data:
            self.client.table("progress").update({
                "completed": completed,
                "completed_at": datetime.now(timezone.utc).isoformat() if completed else None
            }).eq("telegram_id", telegram_id).eq("module_id", module_id).eq("lesson_id", lesson_id).execute()
        else:
            self.client.table("progress").insert({
                "telegram_id": telegram_id,
                "module_id": module_id,
                "lesson_id": lesson_id,
                "completed": completed,
                "completed_at": datetime.now(timezone.utc).isoformat() if completed else None
            }).execute()
    
    async def update_quiz_score(self, telegram_id: int, module_id: int, score: int):
        """Update quiz score for a module"""
        result = self.client.table("progress").select("*").eq("telegram_id", telegram_id).eq("module_id", module_id).eq("lesson_id", 0).execute()
        
        if result.data:
            self.client.table("progress").update({
                "quiz_score": score
            }).eq("telegram_id", telegram_id).eq("module_id", module_id).eq("lesson_id", 0).execute()
        else:
            self.client.table("progress").insert({
                "telegram_id": telegram_id,
                "module_id": module_id,
                "lesson_id": 0,
                "quiz_score": score
            }).execute()


# Global instance
db = SupabaseClient()
