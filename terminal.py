#!/usr/bin/env python3

import os
import sys
import shutil
import platform
import psutil
import subprocess
import datetime
import re
from typing import List, Dict, Any, Optional, Callable

class Command:
    """Base class for all terminal commands"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, args: List[str]) -> str:
        """Execute the command with the given arguments"""
        raise NotImplementedError("Subclasses must implement execute()")

    def help(self) -> str:
        """Return help information for the command"""
        return f"{self.name}: {self.description}"

class FileSystemCommand(Command):
    """Base class for file system related commands"""
    def __init__(self, name: str, description: str):
        super().__init__(name, description)

class PwdCommand(FileSystemCommand):
    """Print working directory command"""
    def __init__(self):
        super().__init__("pwd", "Print the current working directory")
    
    def execute(self, args: List[str]) -> str:
        return os.getcwd()

class LsCommand(FileSystemCommand):
    """List directory contents command"""
    def __init__(self):
        super().__init__("ls", "List directory contents")
    
    def execute(self, args: List[str]) -> str:
        # Parse arguments
        show_hidden = "-a" in args or "--all" in args
        long_format = "-l" in args
        
        # Determine target directory
        target_dir = "."
        for arg in args:
            if not arg.startswith("-"):
                target_dir = arg
                break
        
        try:
            items = os.listdir(target_dir)
            
            # Filter hidden files if not showing all
            if not show_hidden:
                items = [item for item in items if not item.startswith(".")]
            
            # Sort items (directories first, then files)
            dirs = []
            files = []
            for item in items:
                full_path = os.path.join(target_dir, item)
                if os.path.isdir(full_path):
                    dirs.append(item)
                else:
                    files.append(item)
            
            dirs.sort()
            files.sort()
            sorted_items = dirs + files
            
            if long_format:
                result = []
                for item in sorted_items:
                    full_path = os.path.join(target_dir, item)
                    stats = os.stat(full_path)
                    # Format: permissions size last_modified name
                    file_type = "d" if os.path.isdir(full_path) else "-"
                    size = stats.st_size
                    mod_time = datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%b %d %H:%M")
                    result.append(f"{file_type} {size:8d} {mod_time} {item}{'/' if os.path.isdir(full_path) else ''}")
                return "\n".join(result)
            else:
                # Add trailing slash to directories
                formatted_items = [f"{item}/" if os.path.isdir(os.path.join(target_dir, item)) else item for item in sorted_items]
                return "  ".join(formatted_items)
        except FileNotFoundError:
            return f"ls: cannot access '{target_dir}': No such file or directory"
        except PermissionError:
            return f"ls: cannot open directory '{target_dir}': Permission denied"

class CdCommand(FileSystemCommand):
    """Change directory command"""
    def __init__(self):
        super().__init__("cd", "Change the current working directory")
    
    def execute(self, args: List[str]) -> str:
        # Default to home directory if no args
        target_dir = os.path.expanduser("~") if not args else args[0]
        
        try:
            os.chdir(target_dir)
            return ""  # cd typically doesn't output anything on success
        except FileNotFoundError:
            return f"cd: {target_dir}: No such file or directory"
        except NotADirectoryError:
            return f"cd: {target_dir}: Not a directory"
        except PermissionError:
            return f"cd: {target_dir}: Permission denied"

class MkdirCommand(FileSystemCommand):
    """Make directory command"""
    def __init__(self):
        super().__init__("mkdir", "Create new directories")
    
    def execute(self, args: List[str]) -> str:
        if not args:
            return "mkdir: missing operand"
        
        create_parents = "-p" in args or "--parents" in args
        if create_parents:
            args = [arg for arg in args if arg != "-p" and arg != "--parents"]
        
        errors = []
        for path in args:
            try:
                if create_parents:
                    os.makedirs(path, exist_ok=True)
                else:
                    os.mkdir(path)
            except FileExistsError:
                errors.append(f"mkdir: cannot create directory '{path}': File exists")
            except FileNotFoundError:
                errors.append(f"mkdir: cannot create directory '{path}': No such file or directory")
            except PermissionError:
                errors.append(f"mkdir: cannot create directory '{path}': Permission denied")
        
        return "\n".join(errors) if errors else ""

class RmCommand(FileSystemCommand):
    """Remove files or directories command"""
    def __init__(self):
        super().__init__("rm", "Remove files or directories")
    
    def execute(self, args: List[str]) -> str:
        if not args:
            return "rm: missing operand"
        
        recursive = "-r" in args or "--recursive" in args
        force = "-f" in args or "--force" in args
        
        # Filter out options
        paths = [arg for arg in args if not arg.startswith("-")]
        
        errors = []
        for path in paths:
            try:
                if os.path.isdir(path):
                    if recursive:
                        shutil.rmtree(path)
                    else:
                        errors.append(f"rm: cannot remove '{path}': Is a directory")
                else:
                    os.remove(path)
            except FileNotFoundError:
                if not force:
                    errors.append(f"rm: cannot remove '{path}': No such file or directory")
            except PermissionError:
                errors.append(f"rm: cannot remove '{path}': Permission denied")
            except Exception as e:
                errors.append(f"rm: cannot remove '{path}': {str(e)}")
        
        return "\n".join(errors) if errors else ""

class TouchCommand(FileSystemCommand):
    """Create empty files or update timestamps command"""
    def __init__(self):
        super().__init__("touch", "Create empty files or update file timestamps")
    
    def execute(self, args: List[str]) -> str:
        if not args:
            return "touch: missing file operand"
        
        errors = []
        for path in args:
            try:
                # If file exists, update timestamp; otherwise create it
                with open(path, 'a'):
                    os.utime(path, None)
            except FileNotFoundError:
                # This might happen if parent directory doesn't exist
                errors.append(f"touch: cannot touch '{path}': No such file or directory")
            except PermissionError:
                errors.append(f"touch: cannot touch '{path}': Permission denied")
            except Exception as e:
                errors.append(f"touch: {str(e)}")
        
        return "\n".join(errors) if errors else ""

class CatCommand(FileSystemCommand):
    """Concatenate and print files command"""
    def __init__(self):
        super().__init__("cat", "Concatenate and print files")
    
    def execute(self, args: List[str]) -> str:
        if not args:
            return "cat: missing file operand"
        
        results = []
        for path in args:
            try:
                with open(path, 'r') as f:
                    content = f.read()
                    results.append(content)
            except FileNotFoundError:
                results.append(f"cat: {path}: No such file or directory")
            except IsADirectoryError:
                results.append(f"cat: {path}: Is a directory")
            except PermissionError:
                results.append(f"cat: {path}: Permission denied")
            except UnicodeDecodeError:
                results.append(f"cat: {path}: Binary file")
            except Exception as e:
                results.append(f"cat: {path}: {str(e)}")
        
        return "\n".join(results)

class EchoCommand(Command):
    """Echo arguments command"""
    def __init__(self):
        super().__init__("echo", "Display a line of text")
    
    def execute(self, args: List[str]) -> str:
        return " ".join(args)

class SystemCommand(Command):
    """Base class for system related commands"""
    def __init__(self, name: str, description: str):
        super().__init__(name, description)

class PsCommand(SystemCommand):
    """Process status command"""
    def __init__(self):
        super().__init__("ps", "Report process status")
    
    def execute(self, args: List[str]) -> str:
        show_all = "-a" in args or "--all" in args
        
        header = "PID\tCPU%\tMEM%\tCOMMAND"
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                # Skip processes not owned by current user unless -a is specified
                if not show_all and proc.info['username'] != os.getlogin():
                    continue
                
                processes.append(f"{proc.info['pid']}\t{proc.info['cpu_percent']:.1f}\t{proc.info['memory_percent']:.1f}\t{proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        return header + "\n" + "\n".join(processes)

class TopCommand(SystemCommand):
    """Display system resource usage and processes"""
    def __init__(self):
        super().__init__("top", "Display system resource usage and processes")
    
    def execute(self, args: List[str]) -> str:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Format system information
        system_info = [
            f"CPU Usage: {cpu_percent}%",
            f"Memory: {memory.percent}% used ({memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB)",
            f"Swap: {swap.percent}% used ({swap.used / (1024**3):.1f}GB / {swap.total / (1024**3):.1f}GB)"
        ]
        
        # Get process information (top 10 by CPU usage)
        processes = []
        for proc in sorted(psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']), 
                          key=lambda p: p.info['cpu_percent'], reverse=True)[:10]:
            try:
                processes.append(f"{proc.info['pid']:5d} {proc.info['username']:10s} {proc.info['cpu_percent']:5.1f} {proc.info['memory_percent']:5.1f} {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Format output
        header = "PID     USER       CPU%  MEM%  COMMAND"
        return "\n".join(system_info) + "\n\n" + header + "\n" + "\n".join(processes)

class DfCommand(SystemCommand):
    """Report file system disk space usage"""
    def __init__(self):
        super().__init__("df", "Report file system disk space usage")
    
    def execute(self, args: List[str]) -> str:
        human_readable = "-h" in args or "--human-readable" in args
        
        header = "Filesystem\tSize\tUsed\tAvail\tUse%\tMounted on"
        partitions = []
        
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                
                if human_readable:
                    size = self._human_readable_size(usage.total)
                    used = self._human_readable_size(usage.used)
                    free = self._human_readable_size(usage.free)
                else:
                    size = str(usage.total)
                    used = str(usage.used)
                    free = str(usage.free)
                
                partitions.append(f"{part.device}\t{size}\t{used}\t{free}\t{usage.percent}%\t{part.mountpoint}")
            except (PermissionError, FileNotFoundError):
                pass
        
        return header + "\n" + "\n".join(partitions)
    
    def _human_readable_size(self, size_bytes):
        """Convert size in bytes to human readable format"""
        for unit in ['B', 'K', 'M', 'G', 'T', 'P']:
            if size_bytes < 1024 or unit == 'P':
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024

class HistoryCommand(Command):
    """Display command history"""
    def __init__(self, terminal):
        super().__init__("history", "Display command history")
        self.terminal = terminal
    
    def execute(self, args: List[str]) -> str:
        # Get the number of entries to show
        count = None
        if args and args[0].isdigit():
            count = int(args[0])
        
        history = self.terminal.command_history
        if count is not None:
            history = history[-count:]
        
        # Format history with line numbers
        result = []
        for i, cmd in enumerate(history, 1):
            result.append(f"{i:4d}  {cmd}")
        
        return "\n".join(result)

class ClearCommand(Command):
    """Clear the terminal screen"""
    def __init__(self):
        super().__init__("clear", "Clear the terminal screen")
    
    def execute(self, args: List[str]) -> str:
        # Special return value that will be handled by the terminal
        return "__CLEAR__"

class ExitCommand(Command):
    """Exit the terminal"""
    def __init__(self):
        super().__init__("exit", "Exit the terminal")
    
    def execute(self, args: List[str]) -> str:
        # Special return value that will be handled by the terminal
        return "__EXIT__"

class HelpCommand(Command):
    """Display help information"""
    def __init__(self, terminal):
        super().__init__("help", "Display help information for commands")
        self.terminal = terminal
    
    def execute(self, args: List[str]) -> str:
        if not args:
            # List all commands
            commands = sorted(self.terminal.commands.keys())
            return "Available commands:\n" + "\n".join(f"  {cmd}" for cmd in commands) + "\n\nType 'help <command>' for more information on a specific command."
        else:
            # Show help for specific command
            cmd_name = args[0]
            if cmd_name in self.terminal.commands:
                return self.terminal.commands[cmd_name].help()
            else:
                return f"Unknown command: {cmd_name}"

class Terminal:
    """Python-based command terminal"""
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.command_history: List[str] = []
        self.running = True
        self.current_dir = os.getcwd()
        self.register_commands()
    
    def register_commands(self):
        """Register all available commands"""
        # File system commands
        self.register_command(PwdCommand())
        self.register_command(LsCommand())
        self.register_command(CdCommand())
        self.register_command(MkdirCommand())
        self.register_command(RmCommand())
        self.register_command(TouchCommand())
        self.register_command(CatCommand())
        
        # System commands
        self.register_command(EchoCommand())
        self.register_command(PsCommand())
        self.register_command(TopCommand())
        self.register_command(DfCommand())
        
        # Terminal control commands
        self.register_command(HistoryCommand(self))
        self.register_command(ClearCommand())
        self.register_command(ExitCommand())
        self.register_command(HelpCommand(self))
    
    def register_command(self, command: Command):
        """Register a command with the terminal"""
        self.commands[command.name] = command
    
    def parse_command(self, input_line: str) -> tuple[str, List[str]]:
        """Parse a command line into command and arguments"""
        parts = input_line.strip().split()
        if not parts:
            return "", []
        
        command = parts[0]
        args = parts[1:]
        
        return command, args
    
    def execute_command(self, input_line: str) -> str:
        """Execute a command and return the output"""
        if not input_line.strip():
            return ""
        
        # Add to history
        self.command_history.append(input_line)
        
        # Parse the command
        cmd_name, args = self.parse_command(input_line)
        
        # Execute the command if it exists
        if cmd_name in self.commands:
            return self.commands[cmd_name].execute(args)
        else:
            return f"{cmd_name}: command not found"
    
    def get_prompt(self) -> str:
        """Get the terminal prompt"""
        username = os.environ.get("USER", "user")
        hostname = platform.node()
        cwd = os.getcwd()
        home = os.path.expanduser("~")
        
        # Replace home directory with ~
        if cwd.startswith(home):
            cwd = "~" + cwd[len(home):]
        
        return f"{username}@{hostname}:{cwd}$ "
    
    def run(self):
        """Run the terminal main loop"""
        print("Python Terminal v1.0")
        print("Type 'help' for a list of commands, 'exit' to quit.")
        
        while self.running:
            try:
                # Display prompt and get input
                prompt = self.get_prompt()
                user_input = input(prompt)
                
                # Execute the command
                output = self.execute_command(user_input)
                
                # Handle special return values
                if output == "__EXIT__":
                    self.running = False
                    print("Goodbye!")
                elif output == "__CLEAR__":
                    # Clear the screen (platform dependent)
                    os.system('cls' if os.name == 'nt' else 'clear')
                elif output:
                    print(output)
            
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit the terminal.")
            except EOFError:
                self.running = False
                print("\nGoodbye!")
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    terminal = Terminal()
    terminal.run()