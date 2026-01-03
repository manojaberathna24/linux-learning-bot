"""
Learning Content for Linux Bot
10 modules from basic to advanced
"""

LEARNING_MODULES = [
    {
        "id": 1,
        "title": "🐧 Linux Basics",
        "description": "Introduction to Linux and basic concepts",
        "lessons": [
            {
                "id": 1,
                "title": "What is Linux?",
                "content": """
Linux is a free, open-source operating system. It powers servers worldwide, Android phones, and is used by developers and system admins.

**Key Features:**
• Free and open source
• Secure and stable
• Used in servers, supercomputers, phones
• Large community support

**Popular Distributions:**
• Ubuntu - Beginner friendly
• Debian - Very stable
• CentOS/RHEL - Enterprise
• Arch - Advanced users
"""
            },
            {
                "id": 2,
                "title": "File System Structure",
                "content": """
Linux filesystem is hierarchical, starting from root (/).

**Key Directories:**
📂 /home - User home directories
📂 /etc - Configuration files
📂 /var - Variable data (logs)
📂 /bin - Essential binaries
📂 /usr - User programs
📂 /tmp - Temporary files

Try: `ls /` to see root directories!
"""
            },
            {
                "id": 3,
                "title": "Basic Navigation",
                "content": """
**Essential Commands:**

`pwd` - Print Working Directory
Shows your current location

`cd <dir>` - Change Directory
• `cd /home` - Go to /home
• `cd ..` - Go up one level
• `cd ~` - Go to your home

`ls` - List files
• `ls -l` - Long format
• `ls -la` - Show hidden files

**Try in terminal:**
```
pwd
ls
cd Documents
pwd
```
"""
            }
        ]
    },
    {
        "id": 2,
        "title": "📝 File Operations",
        "description": "Creating, copying, moving files",
        "lessons": [
            {
                "id": 1,
                "title": "Creating Files",
                "content": """
**touch** - Create empty file
```bash
touch myfile.txt
touch file1.txt file2.txt
```

**mkdir** - Create directory
```bash
mkdir myfolder
mkdir -p parent/child/grandchild
```

The `-p` flag creates parent directories!
"""
            },
            {
                "id": 2,
                "title": "Viewing Files",
                "content": """
**cat** - Display file contents
```bash
cat myfile.txt
cat file1 file2  # Multiple files
```

**head/tail** - First/last lines
```bash
head -n 5 file.txt  # First 5 lines
tail -n 10 file.txt # Last 10 lines
```

**less** - Scroll through files
```bash
less large_file.txt
# Press q to quit
```
"""
            },
            {
                "id": 3,
                "title": "Copying & Moving",
                "content": """
**cp** - Copy files
```bash
cp source.txt destination.txt
cp file.txt /home/user/Documents/
cp -r folder/ /backup/  # -r for directories
```

**mv** - Move or rename
```bash
mv oldname.txt newname.txt
mv file.txt /another/folder/
```

**rm** - Remove files
```bash
rm file.txt
rm -r folder/  # Remove directory
rm -rf folder/ # Force remove
```

⚠️ Be careful with `rm -rf` - no undo!
"""
            }
        ]
    },
    {
        "id": 3,
        "title": "👤 Users & Permissions",
        "description": "User management and file permissions",
        "lessons": [
            {
                "id": 1,
                "title": "Understanding Permissions",
                "content": """
Every file has permissions for:
• **User** (owner)
• **Group**
• **Others**

**Permission Types:**
`r` = Read (4)
`w` = Write (2)
`x` = Execute (1)

**Example:**
```
-rw-r--r--
│││ │││ │││
│││ │││ └──── Others: r--
│││ └──────── Group: r--
└──────────── User: rw-
```
"""
            },
            {
                "id": 2,
                "title": "Changing Permissions",
                "content": """
**chmod** - Change permissions

**Numeric mode:**
```bash
chmod 755 script.sh
# 7 = rwx (user)
# 5 = r-x (group)
# 5 = r-x (others)
```

**Common permissions:**
• `644` - Files (rw-r--r--)
• `755` - Executables (rwxr-xr-x)
• `700` - Private (rwx------)

**Example:**
```bash
touch script.sh
chmod 755 script.sh
ls -l script.sh
```
"""
            }
        ]
    },
    {
        "id": 4,
        "title": "🔍 Text Processing",
        "description": "grep, sed, awk, and pipes",
        "lessons": [
            {
                "id": 1,
                "title": "grep - Search Text",
                "content": """
**grep** finds patterns in files

```bash
grep "error" logfile.txt
grep -i "error" file.txt    # Case insensitive
grep -r "TODO" ./           # Recursive search
grep -n "pattern" file.txt  # Show line numbers
```

**Examples:**
```bash
# Find all .txt files
ls | grep ".txt"

# Search for errors
cat app.log | grep "ERROR"
```
"""
            },
            {
                "id": 2,
                "title": "Pipes and Redirection",
                "content": """
**Pipes (|)** - Connect commands
```bash
ls -l | grep ".txt"
cat file.txt | wc -l  # Count lines
```

**Redirection:**
```bash
echo "Hello" > file.txt      # Overwrite
echo "World" >> file.txt     # Append
command 2> errors.txt        # Redirect errors
```

**Examples:**
```bash
ls -l > filelist.txt
cat file1.txt file2.txt > combined.txt
```
"""
            }
        ]
    },
    {
        "id": 5,
        "title": "📦 Package Management",
        "description": "Installing software on Linux",
        "lessons": [
            {
                "id": 1,
                "title": "apt (Ubuntu/Debian)",
                "content": """
**apt** - Package manager for Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Upgrade packages
sudo apt upgrade

# Install package
sudo apt install nginx

# Remove package
sudo apt remove nginx

# Search for package
apt search python3
```

Always run `apt update` before installing!
"""
            },
            {
                "id": 2,
                "title": "yum/dnf (RHEL/CentOS)",
                "content": """
**yum/dnf** - For Red Hat based systems

```bash
# Install package
sudo yum install httpd
sudo dnf install httpd

# Update all
sudo yum update

# Remove package
sudo yum remove httpd

# Search
yum search nginx
```

dnf is the newer replacement for yum.
"""
            }
        ]
    },
    {
        "id": 6,
        "title": "🌐 Networking",
        "description": "Network configuration and tools",
        "lessons": [
            {
                "id": 1,
                "title": "Network Commands",
                "content": """
**ip** - Network configuration
```bash
ip addr show       # Show IP addresses
ip route show      # Show routing table
```

**ping** - Test connectivity
```bash
ping google.com
ping -c 4 8.8.8.8  # Send 4 packets
```

**netstat** - Network statistics
```bash
netstat -tuln      # Show listening ports
```

**ss** - Socket statistics (newer)
```bash
ss -tuln
```
"""
            },
            {
                "id": 2,
                "title": "Remote Access - SSH",
                "content": """
**ssh** - Secure Shell

```bash
# Connect to remote server
ssh user@hostname

# Examples
ssh john@192.168.1.100
ssh admin@example.com

# With specific port
ssh -p 2222 user@host

# Copy files with scp
scp file.txt user@host:/path/
```

**SSH Keys:**
```bash
# Generate key pair
ssh-keygen -t rsa -b 4096

# Copy public key to server
ssh-copy-id user@host
```
"""
            }
        ]
    },
    {
        "id": 7,
        "title": "⚡ Process Management",
        "description": "Managing running processes",
        "lessons": [
            {
                "id": 1,
                "title": "Viewing Processes",
                "content": """
**ps** - Process status
```bash
ps aux             # All processes
ps aux | grep nginx
```

**top** - Interactive process viewer
```bash
top
# Press q to quit
# Press k to kill process
```

**htop** - Better top (if installed)
```bash
htop
```
"""
            },
            {
                "id": 2,
                "title": "Controlling Processes",
                "content": """
**kill** - Terminate process
```bash
kill 1234          # Graceful stop
kill -9 1234       # Force kill
killall nginx      # Kill by name
```

**Background & Foreground:**
```bash
command &          # Run in background
jobs               # List background jobs
fg %1              # Bring job 1 to foreground
bg %2              # Resume job 2 in background
```

**Ctrl+Z** - Suspend current process
**Ctrl+C** - Terminate current process
"""
            }
        ]
    },
    {
        "id": 8,
        "title": "📜 Shell Scripting",
        "description": "Writing bash scripts",
        "lessons": [
            {
                "id": 1,
                "title": "First Script",
                "content": """
**Creating a bash script:**

1. Create file:
```bash
touch myscript.sh
```

2. Add shebang and code:
```bash
#!/bin/bash

echo "Hello, World!"
echo "Current directory: $(pwd)"
```

3. Make executable:
```bash
chmod +x myscript.sh
```

4. Run it:
```bash
./myscript.sh
```
"""
            },
            {
                "id": 2,
                "title": "Variables & Conditions",
                "content": """
**Variables:**
```bash
#!/bin/bash

NAME="Linux"
echo "Hello, $NAME"

# Command output in variable
FILES=$(ls -1 | wc -l)
echo "Files: $FILES"
```

**If Statements:**
```bash
if [ -f "file.txt" ]; then
    echo "File exists"
else
    echo "File not found"
fi
```

**Loops:**
```bash
for i in 1 2 3 4 5; do
    echo "Number: $i"
done
```
"""
            }
        ]
    },
    {
        "id": 9,
        "title": "🔒 Security Basics",
        "description": "Linux security fundamentals",
        "lessons": [
            {
                "id": 1,
                "title": "User Security",
                "content": """
**sudo** - Run as superuser
```bash
sudo command        # Run single command
sudo -i            # Become root
```

**File permissions for security:**
```bash
# Private file
chmod 600 private.key

# Public readable
chmod 644 document.txt

# Executable script
chmod 755 script.sh
```

**Check who's logged in:**
```bash
who
w
last
```
"""
            },
            {
                "id": 2,
                "title": "Firewall - ufw",
                "content": """
**ufw** - Uncomplicated Firewall

```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Check status
sudo ufw status

# Deny port
sudo ufw deny 3306
```

Always allow SSH before enabling firewall!
"""
            }
        ]
    },
    {
        "id": 10,
        "title": "💾 Disk & System",
        "description": "Disk management and system info",
        "lessons": [
            {
                "id": 1,
                "title": "Disk Usage",
                "content": """
**df** - Disk Free
```bash
df -h              # Human readable
df -h /home        # Specific partition
```

**du** - Disk Usage
```bash
du -sh *           # Size of each item
du -sh /var/log    # Size of directory
du -h --max-depth=1
```

**Find large files:**
```bash
find / -type f -size +100M 2>/dev/null
```
"""
            },
            {
                "id": 2,
                "title": "System Information",
                "content": """
**uname** - System info
```bash
uname -a           # All info
uname -r           # Kernel version
```

**System monitoring:**
```bash
free -h            # Memory usage
uptime             # System uptime
cat /proc/cpuinfo  # CPU info
lscpu              # CPU details
```

**System logs:**
```bash
journalctl         # System logs
tail -f /var/log/syslog
```
"""
            }
        ]
    }
]


def get_module(module_id: int) -> dict:
    """Get a specific module by ID"""
    for module in LEARNING_MODULES:
        if module["id"] == module_id:
            return module
    return None


def get_lesson(module_id: int, lesson_id: int) -> dict:
    """Get a specific lesson"""
    module = get_module(module_id)
    if module:
        for lesson in module["lessons"]:
            if lesson["id"] == lesson_id:
                return lesson
    return None


def get_modules_summary() -> str:
    """Get a summary of all modules"""
    summary = "📚 **Linux Learning Modules**\n\n"
    for module in LEARNING_MODULES:
        lesson_count = len(module["lessons"])
        summary += f"{module['title']}\n"
        summary += f"   {module['description']}\n"
        summary += f"   📝 {lesson_count} lessons\n\n"
    return summary
