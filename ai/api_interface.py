#!/usr/bin/env python3
"""
AI API Interface
================
This script provides a command-line interface for the AI model
that can be called from the Express.js backend.
"""

import sys
import json
import os
from inference_silent import LLMInference

def main():
    try:
        # Suppress any remaining output to stderr
        import warnings
        warnings.filterwarnings("ignore")
        
        # Read input from stdin
        input_data = sys.stdin.read().strip()
        
        if not input_data:
            print(json.dumps({"error": "No input provided"}), flush=True)
            sys.exit(1)
        
        # Parse input JSON
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            # Fallback: treat as plain text message
            data = {"message": input_data}
        
        message = data.get("message", "")
        conversation_id = data.get("conversation_id")
        max_length = data.get("max_length", 150)
        temperature = data.get("temperature", 0.8)
        
        if not message:
            print(json.dumps({"error": "Message is required"}), flush=True)
            sys.exit(1)
        
        # Initialize AI model
        model_path = "./fine_tuned_model"
        if not os.path.exists(model_path):
            model_path = None  # Will use fallback model
        
        llm = LLMInference(model_path)
        
        # Generate response
        response = llm.generate_response(
            message,
            max_length=max_length,
            temperature=temperature
        )
        
        # Detect mode based on message content
        mode = detect_mode(message)
        
        # Output JSON response
        result = {
            "response": response,
            "mode": mode,
            "conversation_id": conversation_id,
            "success": True
        }
        
        print(json.dumps(result), flush=True)
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "success": False
        }
        print(json.dumps(error_result), flush=True)
        sys.exit(1)

def detect_mode(message):
    """Detect the mode based on message content"""
    message_lower = message.lower()
    
    # Coding keywords
    coding_keywords = ['code', 'program', 'function', 'debug', 'python', 'javascript', 
                      'html', 'css', 'react', 'node', 'api', 'database', 'sql',
                      'algorithm', 'class', 'method', 'variable', 'loop', 'if']
    
    # Creative keywords
    creative_keywords = ['story', 'creative', 'imagine', 'design', 'art', 'write',
                        'poem', 'song', 'character', 'plot', 'idea', 'brainstorm']
    
    # Analytical keywords
    analytical_keywords = ['analyze', 'explain', 'why', 'how', 'compare', 'evaluate',
                          'pros', 'cons', 'advantage', 'disadvantage', 'because',
                          'reason', 'cause', 'effect', 'impact', 'result']
    
    # Count matches
    coding_score = sum(1 for keyword in coding_keywords if keyword in message_lower)
    creative_score = sum(1 for keyword in creative_keywords if keyword in message_lower)
    analytical_score = sum(1 for keyword in analytical_keywords if keyword in message_lower)
    
    # Determine mode
    if coding_score > creative_score and coding_score > analytical_score:
        return "coding"
    elif creative_score > analytical_score:
        return "creative"
    elif analytical_score > 0:
        return "analytical"
    else:
        return "default"

if __name__ == "__main__":
    main()