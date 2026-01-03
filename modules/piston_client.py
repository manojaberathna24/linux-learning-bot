"""
Piston API Client
Executes real Linux commands in a safe, isolated environment
FREE - No API key required!
"""
import httpx
import config


class PistonClient:
    def __init__(self):
        self.api_url = config.PISTON_API_URL
    
    async def execute_bash(self, script: str) -> dict:
        """
        Execute a bash script using Piston API
        
        Args:
            script: Bash script or command to execute
        
        Returns:
            dict with 'output', 'error', and 'exit_code'
        """
        payload = {
            "language": "bash",
            "version": "5.2.0",
            "files": [
                {
                    "name": "main.sh",
                    "content": script
                }
            ],
            "stdin": "",
            "args": [],
            "compile_timeout": 10000,
            "run_timeout": 5000,
            "compile_memory_limit": -1,
            "run_memory_limit": -1
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/execute",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    run_result = data.get("run", {})
                    return {
                        "output": run_result.get("stdout", ""),
                        "error": run_result.get("stderr", ""),
                        "exit_code": run_result.get("code", 0),
                        "success": True
                    }
                else:
                    return {
                        "output": "",
                        "error": f"API Error: {response.status_code}",
                        "exit_code": 1,
                        "success": False
                    }
        
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "exit_code": 1,
                "success": False
            }
    
    async def get_runtimes(self) -> list:
        """Get available runtimes from Piston"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_url}/runtimes")
                if response.status_code == 200:
                    return response.json()
        except:
            pass
        return []
    
    async def execute_for_learning(self, command: str) -> str:
        """
        Execute a command and format output for learning
        
        Args:
            command: Linux command to execute
        
        Returns:
            Formatted output string
        """
        result = await self.execute_bash(command)
        
        if result["success"]:
            output = result["output"].strip()
            error = result["error"].strip()
            
            response = ""
            if output:
                response += f"📤 Output:\n```\n{output}\n```"
            if error:
                response += f"\n⚠️ Stderr:\n```\n{error}\n```"
            if not output and not error:
                response = "✅ Command executed successfully (no output)"
            
            return response
        else:
            return f"❌ Error: {result['error']}"
    
    async def simulate_filesystem_command(self, command: str, file_list: list) -> str:
        """
        Simulate filesystem commands using virtual FS data
        This combines Piston execution with virtual file data
        
        Args:
            command: Command like 'ls', 'cat', etc.
            file_list: List of virtual files from database
        
        Returns:
            Simulated output
        """
        # Parse the command
        parts = command.strip().split()
        if not parts:
            return ""
        
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle 'ls' command
        if cmd == "ls":
            return self._format_ls_output(file_list, args)
        
        return None  # Let other commands be handled by virtual_fs
    
    def _format_ls_output(self, files: list, args: list) -> str:
        """Format ls command output"""
        if not files:
            return ""
        
        show_long = "-l" in args or "-la" in args or "-al" in args
        show_all = "-a" in args or "-la" in args or "-al" in args
        
        if show_long:
            lines = []
            for f in files:
                if not show_all and f["name"].startswith("."):
                    continue
                
                perms = self._format_permissions(f["permissions"], f["is_directory"])
                size = f.get("size", 0)
                name = f["name"]
                
                # Format: drwxr-xr-x 2 user user 4096 Jan 3 21:45 dirname
                lines.append(f"{perms} 1 user user {size:>5} Jan  3 21:45 {name}")
            
            return "\n".join(lines)
        else:
            names = [f["name"] for f in files if show_all or not f["name"].startswith(".")]
            return "  ".join(names)
    
    def _format_permissions(self, perm_num: str, is_dir: bool) -> str:
        """Convert numeric permissions to rwx format"""
        perm_map = {
            "7": "rwx",
            "6": "rw-",
            "5": "r-x",
            "4": "r--",
            "3": "-wx",
            "2": "-w-",
            "1": "--x",
            "0": "---"
        }
        
        prefix = "d" if is_dir else "-"
        perm_str = str(perm_num).zfill(3)
        
        result = prefix
        for digit in perm_str:
            result += perm_map.get(digit, "---")
        
        return result


# Global instance
piston = PistonClient()
