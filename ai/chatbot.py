"""
Simple Chatbot Interface
========================
A clean chatbot interface that wraps the fine-tuned model.
"""

import sys
import os
from datetime import datetime
from inference import LLMInference

class SimpleChatbot:
    def __init__(self, model_path="./fine_tuned_model"):
        """
        Initialize the chatbot with the fine-tuned model
        """
        print("🤖 Initializing chatbot...")
        self.llm = LLMInference(model_path)
        self.conversation_history = []
        
    def add_to_history(self, user_input, ai_response):
        """Add conversation to history"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.conversation_history.append({
            "timestamp": timestamp,
            "user": user_input,
            "ai": ai_response
        })
    
    def save_conversation(self, filename=None):
        """Save conversation history to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Chatbot Conversation Log\n")
            f.write("=" * 30 + "\n\n")
            
            for entry in self.conversation_history:
                f.write(f"[{entry['timestamp']}]\n")
                f.write(f"User: {entry['user']}\n")
                f.write(f"AI: {entry['ai']}\n\n")
        
        print(f"💾 Conversation saved to {filename}")
    
    def print_help(self):
        """Print available commands"""
        help_text = """
Available commands:
  /help     - Show this help message
  /save     - Save conversation to file
  /clear    - Clear conversation history
  /history  - Show conversation history
  /quit     - Exit the chatbot
  
Just type normally to chat with the AI!
        """
        print(help_text)
    
    def show_history(self):
        """Display conversation history"""
        if not self.conversation_history:
            print("📝 No conversation history yet.")
            return
        
        print("\n📝 Conversation History:")
        print("-" * 40)
        for entry in self.conversation_history[-10:]:  # Show last 10 exchanges
            print(f"[{entry['timestamp']}] You: {entry['user']}")
            print(f"[{entry['timestamp']}] AI: {entry['ai']}")
            print()
    
    def run(self):
        """
        Main chatbot loop
        """
        print("\n" + "🤖" * 20)
        print("   Welcome to Your Personal AI Chatbot!")
        print("🤖" * 20)
        print("\nType '/help' for commands or just start chatting!")
        print("Type '/quit' to exit.\n")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                # Handle empty input
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    command = user_input.lower()
                    
                    if command == '/quit':
                        print("\n👋 Thanks for chatting! Goodbye!")
                        break
                    elif command == '/help':
                        self.print_help()
                        continue
                    elif command == '/save':
                        self.save_conversation()
                        continue
                    elif command == '/clear':
                        self.conversation_history.clear()
                        print("🗑️ Conversation history cleared.")
                        continue
                    elif command == '/history':
                        self.show_history()
                        continue
                    else:
                        print("❓ Unknown command. Type '/help' for available commands.")
                        continue
                
                # Generate AI response
                print("🤔 Thinking...", end="", flush=True)
                response = self.llm.generate_response(
                    user_input, 
                    max_length=100, 
                    temperature=0.8
                )
                print("\r" + " " * 15 + "\r", end="")  # Clear "Thinking..."
                
                # Display response
                print(f"🤖 AI: {response}")
                
                # Add to history
                self.add_to_history(user_input, response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again or type '/quit' to exit.")

def main():
    """
    Main function to run the chatbot
    """
    try:
        chatbot = SimpleChatbot()
        chatbot.run()
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        print("Make sure you have trained a model first by running: python train_model.py")
        sys.exit(1)

if __name__ == "__main__":
    main()