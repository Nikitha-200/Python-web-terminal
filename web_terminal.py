#!/usr/bin/env python3

import os
import sys
import json
from flask import Flask, render_template, request, jsonify
# Import AITerminal instead of Terminal
from ai_terminal import AITerminal

app = Flask(__name__)

# Create an AITerminal instance instead of Terminal
terminal = AITerminal()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
    command = data.get('command', '')
    
    # Check if this looks like a natural language command
    if command and not command.split()[0] in terminal.commands and not command.startswith('nlp '):
        # If it looks like natural language, prepend 'nlp '
        command = 'nlp ' + command
    
    # Execute the command
    output = terminal.execute_command(command)
    
    # Handle special commands
    if output == "__EXIT__":
        return jsonify({'output': 'Terminal session ended. Refresh the page to start a new session.', 'prompt': ''})
    elif output == "__CLEAR__":
        return jsonify({'output': '', 'prompt': terminal.get_prompt()})
    else:
        return jsonify({'output': output, 'prompt': terminal.get_prompt()})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the HTML template
    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Web Terminal</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background-color: #1e1e1e;
            color: #f0f0f0;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        #terminal {
            flex-grow: 1;
            overflow-y: auto;
            background-color: #0c0c0c;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        #input-line {
            display: flex;
            margin-bottom: 10px;
        }
        #prompt {
            color: #4CAF50;
            margin-right: 5px;
        }
        #command-input {
            flex-grow: 1;
            background-color: #0c0c0c;
            border: none;
            color: #f0f0f0;
            font-family: 'Courier New', monospace;
            font-size: 1em;
            outline: none;
        }
        .output-text {
            margin: 0;
            padding: 0;
        }
        .command-text {
            color: #4CAF50;
            margin: 0;
            padding: 0;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 {
            color: #4CAF50;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Python Web Terminal</h1>
        <p>A web-based interface for the Python command terminal</p>
    </div>
    
    <div id="terminal">
        <p class="output-text">Python Web Terminal v1.0</p>
        <p class="output-text">Type 'help' for a list of commands, 'exit' to end the session.</p>
    </div>
    
    <div id="input-line">
        <span id="prompt"></span>
        <input type="text" id="command-input" autofocus>
    </div>
    
    <script>
        const terminal = document.getElementById('terminal');
        const promptSpan = document.getElementById('prompt');
        const commandInput = document.getElementById('command-input');
        
        // Command history
        let commandHistory = [];
        let historyIndex = -1;
        let currentInput = '';
        
        // Initialize the prompt
        fetch('/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: '' }),
        })
        .then(response => response.json())
        .then(data => {
            promptSpan.textContent = data.prompt;
        });
        
        // Handle command execution
        commandInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                const command = commandInput.value;
                
                // Add command to terminal
                const commandElement = document.createElement('p');
                commandElement.className = 'command-text';
                commandElement.textContent = promptSpan.textContent + ' ' + command;
                terminal.appendChild(commandElement);
                
                // Add to history
                if (command.trim() !== '') {
                    commandHistory.push(command);
                    historyIndex = commandHistory.length;
                }
                
                // Clear input
                commandInput.value = '';
                
                // Execute command
                fetch('/execute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ command: command }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.output) {
                        const outputElement = document.createElement('p');
                        outputElement.className = 'output-text';
                        outputElement.textContent = data.output;
                        terminal.appendChild(outputElement);
                    }
                    
                    if (data.prompt) {
                        promptSpan.textContent = data.prompt;
                    }
                    
                    // Scroll to bottom
                    terminal.scrollTop = terminal.scrollHeight;
                });
            }
            else if (event.key === 'ArrowUp') {
                // Navigate command history (up)
                if (historyIndex > 0) {
                    if (historyIndex === commandHistory.length) {
                        currentInput = commandInput.value;
                    }
                    historyIndex--;
                    commandInput.value = commandHistory[historyIndex];
                }
                event.preventDefault();
            }
            else if (event.key === 'ArrowDown') {
                // Navigate command history (down)
                if (historyIndex < commandHistory.length - 1) {
                    historyIndex++;
                    commandInput.value = commandHistory[historyIndex];
                }
                else if (historyIndex === commandHistory.length - 1) {
                    historyIndex++;
                    commandInput.value = currentInput;
                }
                event.preventDefault();
            }
        });
        
        // Focus input when clicking anywhere in the terminal
        document.addEventListener('click', function() {
            commandInput.focus();
        });
        
        // Scroll to bottom initially
        terminal.scrollTop = terminal.scrollHeight;
    </script>
</body>
</html>
''')
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=8080)