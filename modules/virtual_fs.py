"""
Virtual Filesystem Module
Handles all virtual filesystem operations for the Linux terminal
"""
from modules.supabase_client import db
import re


class VirtualFileSystem:
    def __init__(self, telegram_id: int, linux_username: str):
        self.telegram_id = telegram_id
        self.username = linux_username
        self.home_dir = f"/home/{linux_username}"
    
    async def get_current_dir(self) -> str:
        """Get user's current working directory"""
        account = await db.get_terminal_account(self.telegram_id)
        return account["current_dir"] if account else self.home_dir
    
    async def execute_command(self, command: str, current_dir: str) -> tuple:
        """
        Execute a filesystem command on the virtual filesystem
        
        Returns:
            tuple: (output_string, new_current_dir)
        """
        command = command.strip()
        if not command:
            return ("", current_dir)
        
        # Parse command and arguments
        parts = self._parse_command(command)
        if not parts:
            return ("", current_dir)
        
        cmd = parts[0]
        args = parts[1:]
        
        # Route to appropriate handler
        handlers = {
            "pwd": self._cmd_pwd,
            "cd": self._cmd_cd,
            "ls": self._cmd_ls,
            "mkdir": self._cmd_mkdir,
            "touch": self._cmd_touch,
            "cat": self._cmd_cat,
            "echo": self._cmd_echo,
            "rm": self._cmd_rm,
            "cp": self._cmd_cp,
            "mv": self._cmd_mv,
            "chmod": self._cmd_chmod,
            "whoami": self._cmd_whoami,
            "clear": self._cmd_clear,
            "help": self._cmd_help,
        }
        
        handler = handlers.get(cmd)
        if handler:
            return await handler(args, current_dir)
        else:
            return (f"bash: {cmd}: command not found", current_dir)
    
    def _parse_command(self, command: str) -> list:
        """Parse command into parts, handling quotes"""
        # Simple parsing - split by space, respecting quotes
        parts = []
        current = ""
        in_quotes = False
        quote_char = None
        
        for char in command:
            if char in '"\'':
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                else:
                    current += char
            elif char == ' ' and not in_quotes:
                if current:
                    parts.append(current)
                    current = ""
            else:
                current += char
        
        if current:
            parts.append(current)
        
        return parts
    
    def _resolve_path(self, path: str, current_dir: str) -> str:
        """Resolve a path to absolute path"""
        if path.startswith("/"):
            resolved = path
        elif path.startswith("~"):
            resolved = path.replace("~", self.home_dir, 1)
        else:
            resolved = f"{current_dir}/{path}"
        
        # Normalize path (handle .. and .)
        parts = []
        for part in resolved.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part and part != ".":
                parts.append(part)
        
        return "/" + "/".join(parts) if parts else "/"
    
    # ==================== COMMAND HANDLERS ====================
    
    async def _cmd_pwd(self, args: list, current_dir: str) -> tuple:
        """Print working directory"""
        return (current_dir, current_dir)
    
    async def _cmd_cd(self, args: list, current_dir: str) -> tuple:
        """Change directory"""
        if not args:
            # cd with no args goes to home
            await db.update_current_dir(self.telegram_id, self.home_dir)
            return ("", self.home_dir)
        
        target = args[0]
        new_path = self._resolve_path(target, current_dir)
        
        # Check if directory exists
        file_entry = await db.get_file(self.telegram_id, new_path)
        
        if not file_entry:
            return (f"bash: cd: {target}: No such file or directory", current_dir)
        
        if not file_entry["is_directory"]:
            return (f"bash: cd: {target}: Not a directory", current_dir)
        
        await db.update_current_dir(self.telegram_id, new_path)
        return ("", new_path)
    
    async def _cmd_ls(self, args: list, current_dir: str) -> tuple:
        """List directory contents"""
        show_long = "-l" in args or "-la" in args or "-al" in args
        show_all = "-a" in args or "-la" in args or "-al" in args
        
        # Get target directory
        target_dir = current_dir
        for arg in args:
            if not arg.startswith("-"):
                target_dir = self._resolve_path(arg, current_dir)
                break
        
        # Get files in directory
        files = await db.get_directory_contents(self.telegram_id, target_dir)
        
        if not files and target_dir != current_dir:
            # Check if path exists
            entry = await db.get_file(self.telegram_id, target_dir)
            if not entry:
                return (f"ls: cannot access '{args[-1]}': No such file or directory", current_dir)
        
        if show_long:
            lines = []
            total_size = 0
            
            # Add . and .. if showing all
            if show_all:
                lines.append(f"drwxr-xr-x 2 {self.username} {self.username}  4096 Jan  3 21:45 .")
                lines.append(f"drwxr-xr-x 2 {self.username} {self.username}  4096 Jan  3 21:45 ..")
            
            for f in files:
                if not show_all and f["name"].startswith("."):
                    continue
                
                perms = self._format_permissions(f["permissions"], f["is_directory"])
                size = f.get("size", 4096 if f["is_directory"] else 0)
                total_size += size
                name = f["name"]
                
                lines.append(f"{perms} 1 {self.username} {self.username} {size:>5} Jan  3 21:45 {name}")
            
            output = f"total {len(files)}\n" + "\n".join(lines) if lines else ""
            return (output, current_dir)
        else:
            names = []
            for f in files:
                if not show_all and f["name"].startswith("."):
                    continue
                names.append(f["name"])
            
            return ("  ".join(names), current_dir)
    
    async def _cmd_mkdir(self, args: list, current_dir: str) -> tuple:
        """Create directory"""
        if not args:
            return ("mkdir: missing operand", current_dir)
        
        create_parents = "-p" in args
        dirs_to_create = [a for a in args if not a.startswith("-")]
        
        for dir_name in dirs_to_create:
            path = self._resolve_path(dir_name, current_dir)
            
            # Check if already exists
            existing = await db.get_file(self.telegram_id, path)
            if existing:
                if not create_parents:
                    return (f"mkdir: cannot create directory '{dir_name}': File exists", current_dir)
                continue
            
            # Create parent directories if -p
            if create_parents:
                parts = path.split("/")
                for i in range(2, len(parts) + 1):
                    parent_path = "/".join(parts[:i])
                    if not await db.get_file(self.telegram_id, parent_path):
                        await db.create_file_entry(self.telegram_id, parent_path, is_directory=True)
            else:
                # Check parent exists
                parent_path = "/".join(path.split("/")[:-1]) or "/"
                if not await db.get_file(self.telegram_id, parent_path):
                    return (f"mkdir: cannot create directory '{dir_name}': No such file or directory", current_dir)
                
                await db.create_file_entry(self.telegram_id, path, is_directory=True)
        
        return ("", current_dir)
    
    async def _cmd_touch(self, args: list, current_dir: str) -> tuple:
        """Create empty file or update timestamp"""
        if not args:
            return ("touch: missing file operand", current_dir)
        
        for filename in args:
            path = self._resolve_path(filename, current_dir)
            
            existing = await db.get_file(self.telegram_id, path)
            if existing:
                # Just update timestamp (already done by get)
                continue
            
            # Create new empty file
            await db.create_file_entry(self.telegram_id, path, is_directory=False, content="")
        
        return ("", current_dir)
    
    async def _cmd_cat(self, args: list, current_dir: str) -> tuple:
        """Display file contents"""
        if not args:
            return ("", current_dir)  # cat without args reads stdin
        
        outputs = []
        for filename in args:
            path = self._resolve_path(filename, current_dir)
            file_entry = await db.get_file(self.telegram_id, path)
            
            if not file_entry:
                return (f"cat: {filename}: No such file or directory", current_dir)
            
            if file_entry["is_directory"]:
                return (f"cat: {filename}: Is a directory", current_dir)
            
            outputs.append(file_entry.get("content", ""))
        
        return ("\n".join(outputs), current_dir)
    
    async def _cmd_echo(self, args: list, current_dir: str) -> tuple:
        """Echo text or redirect to file"""
        if not args:
            return ("", current_dir)
        
        # Check for redirection
        text = " ".join(args)
        
        if " > " in text:
            parts = text.split(" > ", 1)
            content = parts[0].strip().strip('"\'')
            filename = parts[1].strip()
            
            path = self._resolve_path(filename, current_dir)
            
            # Create or overwrite file
            existing = await db.get_file(self.telegram_id, path)
            if existing:
                await db.update_file_content(self.telegram_id, path, content)
            else:
                await db.create_file_entry(self.telegram_id, path, is_directory=False, content=content)
            
            return ("", current_dir)
        
        elif " >> " in text:
            parts = text.split(" >> ", 1)
            content = parts[0].strip().strip('"\'')
            filename = parts[1].strip()
            
            path = self._resolve_path(filename, current_dir)
            
            # Append to file
            existing = await db.get_file(self.telegram_id, path)
            if existing:
                new_content = (existing.get("content", "") or "") + "\n" + content
                await db.update_file_content(self.telegram_id, path, new_content)
            else:
                await db.create_file_entry(self.telegram_id, path, is_directory=False, content=content)
            
            return ("", current_dir)
        
        # Just echo
        return (text.strip('"\''), current_dir)
    
    async def _cmd_rm(self, args: list, current_dir: str) -> tuple:
        """Remove files or directories"""
        if not args:
            return ("rm: missing operand", current_dir)
        
        recursive = "-r" in args or "-rf" in args or "-fr" in args
        force = "-f" in args or "-rf" in args or "-fr" in args
        
        targets = [a for a in args if not a.startswith("-")]
        
        for target in targets:
            path = self._resolve_path(target, current_dir)
            
            file_entry = await db.get_file(self.telegram_id, path)
            
            if not file_entry:
                if not force:
                    return (f"rm: cannot remove '{target}': No such file or directory", current_dir)
                continue
            
            if file_entry["is_directory"] and not recursive:
                return (f"rm: cannot remove '{target}': Is a directory", current_dir)
            
            await db.delete_file(self.telegram_id, path)
        
        return ("", current_dir)
    
    async def _cmd_cp(self, args: list, current_dir: str) -> tuple:
        """Copy files"""
        if len(args) < 2:
            return ("cp: missing destination file operand", current_dir)
        
        source = self._resolve_path(args[0], current_dir)
        dest = self._resolve_path(args[1], current_dir)
        
        source_file = await db.get_file(self.telegram_id, source)
        if not source_file:
            return (f"cp: cannot stat '{args[0]}': No such file or directory", current_dir)
        
        if source_file["is_directory"]:
            return ("cp: -r not specified; omitting directory", current_dir)
        
        # Create copy
        await db.create_file_entry(
            self.telegram_id, dest, 
            is_directory=False, 
            content=source_file.get("content", ""),
            permissions=source_file.get("permissions", "644")
        )
        
        return ("", current_dir)
    
    async def _cmd_mv(self, args: list, current_dir: str) -> tuple:
        """Move/rename files"""
        if len(args) < 2:
            return ("mv: missing destination file operand", current_dir)
        
        source = self._resolve_path(args[0], current_dir)
        dest = self._resolve_path(args[1], current_dir)
        
        source_file = await db.get_file(self.telegram_id, source)
        if not source_file:
            return (f"mv: cannot stat '{args[0]}': No such file or directory", current_dir)
        
        # Create at new location
        await db.create_file_entry(
            self.telegram_id, dest,
            is_directory=source_file["is_directory"],
            content=source_file.get("content"),
            permissions=source_file.get("permissions", "644")
        )
        
        # Delete original
        await db.delete_file(self.telegram_id, source)
        
        return ("", current_dir)
    
    async def _cmd_chmod(self, args: list, current_dir: str) -> tuple:
        """Change file permissions"""
        if len(args) < 2:
            return ("chmod: missing operand", current_dir)
        
        mode = args[0]
        targets = args[1:]
        
        # Validate mode (simple numeric only for now)
        if not re.match(r'^[0-7]{3}$', mode):
            return (f"chmod: invalid mode: '{mode}'", current_dir)
        
        for target in targets:
            path = self._resolve_path(target, current_dir)
            
            file_entry = await db.get_file(self.telegram_id, path)
            if not file_entry:
                return (f"chmod: cannot access '{target}': No such file or directory", current_dir)
            
            await db.update_file_permissions(self.telegram_id, path, mode)
        
        return ("", current_dir)
    
    async def _cmd_whoami(self, args: list, current_dir: str) -> tuple:
        """Print current username"""
        return (self.username, current_dir)
    
    async def _cmd_clear(self, args: list, current_dir: str) -> tuple:
        """Clear screen (returns special marker)"""
        return ("__CLEAR__", current_dir)
    
    async def _cmd_help(self, args: list, current_dir: str) -> tuple:
        """Show available commands"""
        help_text = """📚 Available Commands:

📂 Navigation:
  pwd          - Print current directory
  cd <dir>     - Change directory
  ls [-la]     - List files

📝 File Operations:
  touch <file> - Create empty file
  cat <file>   - Show file contents
  echo <text>  - Print text or redirect to file
  mkdir <dir>  - Create directory
  rm [-rf]     - Remove files/directories
  cp <s> <d>   - Copy file
  mv <s> <d>   - Move/rename file

🔐 Permissions:
  chmod <mode> <file> - Change permissions

ℹ️ Other:
  whoami       - Print username
  clear        - Clear screen
  help         - Show this help
  exit         - Exit terminal mode"""
        
        return (help_text, current_dir)
    
    def _format_permissions(self, perm_num: str, is_dir: bool) -> str:
        """Convert numeric permissions to rwx format"""
        perm_map = {
            "7": "rwx", "6": "rw-", "5": "r-x", "4": "r--",
            "3": "-wx", "2": "-w-", "1": "--x", "0": "---"
        }
        
        prefix = "d" if is_dir else "-"
        perm_str = str(perm_num).zfill(3)
        
        result = prefix
        for digit in perm_str:
            result += perm_map.get(digit, "---")
        
        return result
