#!/usr/bin/env python3
"""
DigiWe Coordinator - Backend Server
Manages state, routes between AI systems, serves web UI
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
STATE_FILE = Path.home() / "digiwe_state.json"
CONVERSATION_LOG = Path.home() / "digiwe_conversations.json"

class DigiWeCoordinator:
    def __init__(self):
        self.state = self.load_state()
        self.conversations = self.load_conversations()
        
    def load_state(self):
        """Load persistent state from disk"""
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {
            "session_count": 0,
            "current_context": [],
            "active_ai": "claude",
            "preferences": {},
            "patterns": []
        }
    
    def save_state(self):
        """Save state to disk"""
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def load_conversations(self):
        """Load conversation history"""
        if CONVERSATION_LOG.exists():
            with open(CONVERSATION_LOG, 'r') as f:
                return json.load(f)
        return []
    
    def save_conversation(self, message, response, ai_used):
        """Save a conversation exchange"""
        self.conversations.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "ai": ai_used
        })
        with open(CONVERSATION_LOG, 'w') as f:
            json.dump(self.conversations, f, indent=2)
    
    def route_message(self, message):
        """Decide which AI system should handle this message"""
        # Simple routing logic for now - can expand later
        message_lower = message.lower()
        
        # Technical/coding questions -> Claude Code
        if any(word in message_lower for word in ['code', 'python', 'debug', 'error', 'install']):
            return 'claude'
        
        # For now, default to Claude
        return 'claude'
    
    def call_claude(self, message):
        """Call Claude Code with the message"""
        try:
            # Build context from recent conversations
            context = self.build_context()
            full_prompt = f"{context}\n\nUser: {message}"
            
            # Call Claude Code
            result = subprocess.run(
                ['claude', '--message', full_prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error calling Claude: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Request timed out. Please try again."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def build_context(self):
        """Build context from recent conversations and state"""
        context_parts = []
        
        # Add recent conversation history (last 5 exchanges)
        recent = self.conversations[-5:] if len(self.conversations) > 5 else self.conversations
        if recent:
            context_parts.append("Recent conversation history:")
            for conv in recent:
                context_parts.append(f"User: {conv['message']}")
                context_parts.append(f"Assistant: {conv['response'][:200]}...")  # Truncate long responses
        
        # Add important patterns/context from state
        if self.state.get('patterns'):
            context_parts.append("\nImportant patterns:")
            for pattern in self.state['patterns'][-3:]:  # Last 3 patterns
                context_parts.append(f"- {pattern}")
        
        return "\n".join(context_parts)
    
    def process_message(self, message):
        """Main message processing pipeline"""
        # Route to appropriate AI
        ai_to_use = self.route_message(message)
        
        # Call the AI
        if ai_to_use == 'claude':
            response = self.call_claude(message)
        else:
            response = f"Routing to {ai_to_use} not yet implemented"
        
        # Save the exchange
        self.save_conversation(message, response, ai_to_use)
        
        # Update state
        self.state['session_count'] += 1
        self.state['active_ai'] = ai_to_use
        self.save_state()
        
        return {
            'response': response,
            'ai_used': ai_to_use,
            'session_count': self.state['session_count']
        }

# Initialize coordinator
coordinator = DigiWeCoordinator()

# Routes
@app.route('/')
def index():
    """Serve the main UI"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    result = coordinator.process_message(message)
    return jsonify(result)

@app.route('/api/state', methods=['GET'])
def get_state():
    """Get current coordinator state"""
    return jsonify(coordinator.state)

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get conversation history"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify(coordinator.conversations[-limit:])

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    coordinator.conversations = []
    coordinator.save_conversation("System", "History cleared", "system")
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    print("DigiWe Coordinator starting...")
    print(f"State file: {STATE_FILE}")
    print(f"Conversations: {CONVERSATION_LOG}")
    print("\nOpen http://localhost:5000 in your browser")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
