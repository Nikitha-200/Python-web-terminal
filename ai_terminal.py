#!/usr/bin/env python3

import os
import sys
import re
import shlex
from typing import List, Dict, Any, Optional, Tuple

# Import the base terminal functionality
from terminal import Terminal, Command

class NLPCommand(Command):
    """Natural language processing command"""
    def __init__(self, terminal):
        super().__init__("nlp", "Process natural language commands")
        self.terminal = terminal
        self.command_patterns = [
            # File operations
            (r"create (?:a )?(?:new )?(?:directory|folder)(?: called| named)? ([\w\s./\\-]+)", self._create_directory),
            (r"make (?:a )?(?:new )?(?:directory|folder)(?: called| named)? ([\w\s./\\-]+)", self._create_directory),
            (r"create (?:a )?(?:new )?(?:empty )?file(?: called| named)? ([\w\s./\\-]+)", self._create_file),
            (r"touch (?:a )?(?:new )?file(?: called| named)? ([\w\s./\\-]+)", self._create_file),
            (r"(?:show|list) (?:the )?(?:files|contents)(?: in| of)?(?: the)? ?(?:directory|folder)? ?([\w\s./\\-]*)", self._list_directory),
            (r"what (?:files|directories) are (?:in|inside) ?([\w\s./\\-]*)", self._list_directory),
            (r"show (?:me )?(?:the )?content(?:s)? of (?:file )?([\w\s./\\-]+)", self._show_file_content),
            (r"(?:read|cat|display|print) (?:file )?([\w\s./\\-]+)", self._show_file_content),
            (r"(?:delete|remove) (?:file |directory |folder )?([\w\s./\\-]+)", self._remove_item),
            (r"move (?:file |directory |folder )?([\w\s./\\-]+) to (?:directory |folder )?([\w\s./\\-]+)", self._move_item),
            (r"rename (?:file |directory |folder )?([\w\s./\\-]+) to ([\w\s./\\-]+)", self._rename_item),
            (r"copy (?:file |directory |folder )?([\w\s./\\-]+) to (?:directory |folder )?([\w\s./\\-]+)", self._copy_item),
            (r"change (?:to )?(?:directory|folder|dir) ([\w\s./\\-]+)", self._change_directory),
            (r"(?:go|navigate) to (?:directory|folder|dir)? ?([\w\s./\\-]+)", self._change_directory),
            (r"cd (?:to )?([\w\s./\\-]+)", self._change_directory),
            
            # System commands
            (r"(?:show|display|list) (?:running )?processes", self._list_processes),
            (r"(?:show|display) (?:system )?(?:resource )?usage", self._show_resource_usage),
            (r"(?:show|display) (?:disk|storage) (?:usage|space|info)", self._show_disk_usage),
            (r"(?:what|where) is (?:my )?current (?:directory|folder|location)", self._show_current_directory),
            (r"(?:show|display) (?:command )?history", self._show_history),
            
            # Help and exit
            (r"(?:show|list|display) (?:available )?commands", self._show_help),
            (r"(?:how to|help|help with) (.*)", self._show_command_help),
            (r"(?:exit|quit|close) (?:terminal|program|application)", self._exit_terminal),
            (r"clear (?:the )?(?:screen|terminal)", self._clear_screen),
        ]
    
    def execute(self, args: List[str]) -> str:
        # Join all arguments to form the natural language query
        query = " ".join(args)
        
        if not query:
            return "Please enter a natural language command. Type 'nlp help' for examples."
        
        if query.lower() in ["help", "examples"]:
            return self._show_examples()
        
        # Try to match the query against known patterns
        for pattern, handler in self.command_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return handler(*match.groups())
        
        return f"I don't understand '{query}'. Type 'nlp help' for examples of commands I understand."
    
    def help(self) -> str:
        return "nlp: Process natural language commands. Type 'nlp help' for examples."
    
    def _show_examples(self) -> str:
        examples = [
            "create a new folder called Projects",
            "make a new directory named Backup",
            "create a new file called notes.txt",
            "show files in Downloads",
            "list contents of the current directory",
            "what files are in Documents",
            "show content of file.txt",
            "read config.ini",
            "delete file temp.txt",
            "remove directory OldStuff",
            "move file report.pdf to Documents",
            "rename file old.txt to new.txt",
            "copy file important.docx to Backup",
            "change to directory Projects",
            "go to Documents",
            "show running processes",
            "display system usage",
            "show disk space",
            "where is my current location",
            "show command history",
            "list available commands",
            "help with creating files",
            "clear the screen",
            "exit terminal"
        ]
        
        return "Natural Language Command Examples:\n" + "\n".join(f"  - {example}" for example in examples)
    
    # Command handlers
    def _create_directory(self, directory_name: str) -> str:
        directory_name = directory_name.strip()
        return self.terminal.execute_command(f"mkdir {shlex.quote(directory_name)}")
    
    def _create_file(self, file_name: str) -> str:
        file_name = file_name.strip()
        return self.terminal.execute_command(f"touch {shlex.quote(file_name)}")
    
    def _list_directory(self, directory: str = "") -> str:
        directory = directory.strip() if directory else "."
        return self.terminal.execute_command(f"ls {shlex.quote(directory)}")
    
    def _show_file_content(self, file_name: str) -> str:
        file_name = file_name.strip()
        return self.terminal.execute_command(f"cat {shlex.quote(file_name)}")
    
    def _remove_item(self, item_name: str) -> str:
        item_name = item_name.strip()
        if os.path.isdir(item_name):
            return self.terminal.execute_command(f"rm -r {shlex.quote(item_name)}")
        else:
            return self.terminal.execute_command(f"rm {shlex.quote(item_name)}")
    
    def _move_item(self, source: str, destination: str) -> str:
        # In a real implementation, this would use a proper move command
        # For our terminal, we'll simulate it with a combination of copy and remove
        source = source.strip()
        destination = destination.strip()
        
        # Check if destination is a directory
        if os.path.isdir(destination):
            # If so, we're moving the file into that directory
            dest_path = os.path.join(destination, os.path.basename(source))
        else:
            # Otherwise, we're renaming/moving to a new path
            dest_path = destination
        
        try:
            import shutil
            shutil.move(source, dest_path)
            return f"Moved {source} to {destination}"
        except Exception as e:
            return f"Error moving {source} to {destination}: {str(e)}"
    
    def _rename_item(self, old_name: str, new_name: str) -> str:
        old_name = old_name.strip()
        new_name = new_name.strip()
        
        try:
            os.rename(old_name, new_name)
            return f"Renamed {old_name} to {new_name}"
        except Exception as e:
            return f"Error renaming {old_name} to {new_name}: {str(e)}"
    
    def _copy_item(self, source: str, destination: str) -> str:
        source = source.strip()
        destination = destination.strip()
        
        try:
            import shutil
            if os.path.isdir(source):
                if os.path.exists(destination):
                    # If destination exists, copy into it
                    dest_path = os.path.join(destination, os.path.basename(source))
                else:
                    # Otherwise, create a new directory with that name
                    dest_path = destination
                shutil.copytree(source, dest_path)
            else:
                if os.path.isdir(destination):
                    # If destination is a directory, copy into it
                    dest_path = os.path.join(destination, os.path.basename(source))
                else:
                    # Otherwise, copy to the new path
                    dest_path = destination
                shutil.copy2(source, dest_path)
            return f"Copied {source} to {destination}"
        except Exception as e:
            return f"Error copying {source} to {destination}: {str(e)}"
    
    def _change_directory(self, directory: str) -> str:
        directory = directory.strip()
        return self.terminal.execute_command(f"cd {shlex.quote(directory)}")
    
    def _list_processes(self) -> str:
        return self.terminal.execute_command("ps")
    
    def _show_resource_usage(self) -> str:
        return self.terminal.execute_command("top")
    
    def _show_disk_usage(self) -> str:
        return self.terminal.execute_command("df -h")
    
    def _show_current_directory(self) -> str:
        return self.terminal.execute_command("pwd")
    
    def _show_history(self) -> str:
        return self.terminal.execute_command("history")
    
    def _show_help(self) -> str:
        return self.terminal.execute_command("help")
    
    def _show_command_help(self, command: str) -> str:
        command = command.strip()
        # Try to extract the actual command from the query
        cmd_match = re.search(r"(\w+)", command)
        if cmd_match:
            cmd = cmd_match.group(1)
            return self.terminal.execute_command(f"help {cmd}")
        return self.terminal.execute_command("help")
    
    def _exit_terminal(self) -> str:
        return self.terminal.execute_command("exit")
    
    def _clear_screen(self) -> str:
        return self.terminal.execute_command("clear")

class AutoCompleteCommand(Command):
    """Command for auto-completion functionality"""
    def __init__(self, terminal):
        super().__init__("autocomplete", "Toggle auto-completion functionality")
        self.terminal = terminal
        self.enabled = False
    
    def execute(self, args: List[str]) -> str:
        if not args:
            self.enabled = not self.enabled
            status = "enabled" if self.enabled else "disabled"
            return f"Auto-completion is now {status}"
        
        if args[0].lower() in ["on", "enable", "true", "1"]:
            self.enabled = True
            return "Auto-completion is now enabled"
        elif args[0].lower() in ["off", "disable", "false", "0"]:
            self.enabled = False
            return "Auto-completion is now disabled"
        else:
            return "Invalid argument. Use 'on' or 'off'."
    
    def help(self) -> str:
        return "autocomplete: Toggle auto-completion functionality. Usage: autocomplete [on|off]"
    
    def get_completions(self, text: str) -> List[str]:
        """Get possible completions for the given text"""
        if not self.enabled:
            return []
        
        # Complete commands
        if not text.strip() or " " not in text:
            return [cmd for cmd in self.terminal.commands.keys() if cmd.startswith(text)]
        
        # Complete file/directory names for relevant commands
        parts = text.split()
        cmd = parts[0]
        
        # Only provide file/directory completion for certain commands
        if cmd in ["cd", "ls", "cat", "rm", "mkdir", "touch"]:
            # Get the partial path to complete
            partial_path = parts[-1] if len(parts) > 1 else ""
            
            # Get the directory to look in
            if os.path.isdir(partial_path):
                dir_to_check = partial_path
                partial_name = ""
            else:
                dir_to_check = os.path.dirname(partial_path) or "."
                partial_name = os.path.basename(partial_path)
            
            try:
                # Get all matching items in the directory
                items = os.listdir(dir_to_check)
                matches = [item for item in items if item.startswith(partial_name)]
                
                # Format the completions
                if dir_to_check == ".":
                    return matches
                else:
                    return [os.path.join(os.path.dirname(partial_path), item) for item in matches]
            except (FileNotFoundError, NotADirectoryError):
                return []
        
        return []

class AITerminal(Terminal):
    """Enhanced terminal with natural language processing and auto-completion"""
    def __init__(self):
        super().__init__()
        # Register additional commands
        self.register_command(NLPCommand(self))
        self.autocomplete_command = AutoCompleteCommand(self)
        self.register_command(self.autocomplete_command)
        
        # Command history index for up/down arrow navigation
        self.history_index = len(self.command_history)
        self.current_input = ""
    
    def run(self):
        """Run the terminal main loop with enhanced input handling"""
        try:
            # Try to import readline for better input handling
            import readline
            readline.parse_and_bind("tab: complete")
            
            # Set up tab completion
            def completer(text, state):
                # Get completions from our autocomplete command
                completions = self.autocomplete_command.get_completions(readline.get_line_buffer())
                if state < len(completions):
                    return completions[state]
                else:
                    return None
            
            readline.set_completer(completer)
            
            # Set up command history
            histfile = os.path.join(os.path.expanduser("~"), ".python_terminal_history")
            try:
                readline.read_history_file(histfile)
                readline.set_history_length(1000)
            except FileNotFoundError:
                pass
            
            def save_history():
                try:
                    readline.write_history_file(histfile)
                except Exception:
                    pass
            
            import atexit
            atexit.register(save_history)
            
        except ImportError:
            # If readline is not available, fall back to basic input
            pass
        
        print("AI-Enhanced Python Terminal v1.0")
        print("Type 'help' for a list of commands, 'nlp help' for natural language examples, 'exit' to quit.")
        
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
    terminal = AITerminal()
    terminal.run()