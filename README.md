# Python-Based Command Terminal

A fully functioning command terminal that mimics the behavior of a real system terminal, built with Python. This terminal supports standard commands for file operations, directory navigation, process monitoring, and more.

The project includes three versions:
1. **Basic Terminal** - A standard command-line terminal with traditional command syntax
2. **AI-Enhanced Terminal** - An advanced version with natural language processing and auto-completion features
3. **Web Terminal** - A browser-based interface for the terminal with a clean, modern UI

## Features

- Full-fledged file and directory operations (ls, cd, pwd, mkdir, rm, touch, cat)
- System monitoring tools (ps, top, df)
- Terminal control commands (clear, history, help, exit)
- Clean and responsive command-line interface
- Error handling for invalid commands

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Terminal
Run the standard terminal application:

```bash
python terminal.py
```

### AI-Enhanced Terminal
Run the AI-enhanced terminal with natural language support:

```bash
python ai_terminal.py
```

### Web-Based Terminal
Run the web-based terminal interface:

```bash
python web_terminal.py
```

Then open your browser and navigate to: http://localhost:5000

### Available Commands

- **File Operations**:
  - `pwd` - Print working directory
  - `ls` - List directory contents
  - `cd` - Change directory
  - `mkdir` - Create directories
  - `rm` - Remove files or directories
  - `touch` - Create empty files or update timestamps
  - `cat` - Display file contents

- **System Commands**:
  - `echo` - Display a line of text
  - `ps` - Report process status
  - `top` - Display system resource usage and processes
  - `df` - Report file system disk space usage

- **Terminal Control**:
  - `history` - Display command history
  - `clear` - Clear the terminal screen
  - `help` - Display help information
  - `exit` - Exit the terminal

### Command Options

Many commands support options similar to real terminal commands:

- `ls -a` - Show all files (including hidden)
- `ls -l` - Use long listing format
- `mkdir -p` - Create parent directories as needed
- `rm -r` - Remove directories and their contents recursively
- `rm -f` - Force removal without prompting
- `ps -a` - Show processes from all users
- `df -h` - Show sizes in human-readable format

## AI Features

### Natural Language Processing
The AI-enhanced terminal supports natural language commands such as:
- "create a new folder called Projects"
- "show files in Downloads"
- "read config.ini"
- "move file report.pdf to Documents"

To see all supported natural language commands, type `nlp help` in the AI terminal.

### Auto-Completion
The AI terminal includes command and file/directory auto-completion:
- Press Tab to complete commands and file paths
- Toggle auto-completion with the `autocomplete` command

## Future Enhancements

- More advanced natural language understanding
- Enhanced system monitoring capabilities
- Pipe and redirection support
- Custom command aliases
- Script execution support

## Requirements

- Python 3.6+
- psutil library