"""
Inference Script for Fine-tuned Language Model
==============================================
This script loads a fine-tuned model and provides text generation capabilities.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import random
import numpy as np

# Set random seeds for reproducible generation
def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

class LLMInference:
    def __init__(self, model_path="./fine_tuned_model", fallback_model="distilgpt2"):
        """
        Initialize inference engine
        
        Args:
            model_path: Path to fine-tuned model
            fallback_model: Fallback model if fine-tuned model not found
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        try:
            print(f"Loading fine-tuned model from {model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(model_path)
            print("Fine-tuned model loaded successfully!")
        except Exception as e:
            print(f"Could not load fine-tuned model: {e}")
            print(f"Falling back to base model: {fallback_model}")
            self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            self.model = AutoModelForCausalLM.from_pretrained(fallback_model)
        
        self.model.to(self.device)
        self.model.eval()
        
        # Set pad token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def generate_response(self, prompt, max_length=100, temperature=0.8, top_p=0.9, top_k=50):
        """
        Generate text response given a prompt
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature (higher = more random)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
        """
        # Format prompt for conversation
        formatted_prompt = f"<|startoftext|>Human: {prompt} AI:"
        
        # Tokenize input
        inputs = self.tokenizer.encode(formatted_prompt, return_tensors="pt").to(self.device)
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=len(inputs[0]) + max_length,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1,
            )
        
        # Decode and clean response
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract AI response
        if "AI:" in generated_text:
            response = generated_text.split("AI:")[-1].strip()
            # Clean up response (remove potential Human: continuation)
            if "Human:" in response:
                response = response.split("Human:")[0].strip()
        else:
            response = generated_text[len(formatted_prompt):].strip()
        
        return response
    
    def generate_creative_text(self, prompt, max_length=150, temperature=1.0):
        """
        Generate creative text with higher temperature
        """
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=len(inputs[0]) + max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.95,
                repetition_penalty=1.2,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text[len(prompt):].strip()

def test_model():
    """
    Test the model with sample prompts
    """
    print("=== Testing Model ===")
    
    # Initialize inference
    llm = LLMInference()
    
    # Test prompts
    test_prompts = [
        "What is machine learning?",
        "How do I learn programming?",
        "Explain neural networks",
        "What can you help me with?",
        "Tell me about artificial intelligence"
    ]
    
    print("\n--- Sample Responses ---")
    for prompt in test_prompts:
        print(f"\nHuman: {prompt}")
        response = llm.generate_response(prompt, max_length=80, temperature=0.7)
        print(f"AI: {response}")
    
    return llm

def main():
    """
    Main inference function with interactive mode
    """
    set_seed(42)
    
    # Test the model first
    llm = test_model()
    
    # Interactive chat loop
    print("\n" + "="*50)
    print("Interactive Chat Mode")
    print("Type 'quit' to exit, 'creative' for creative mode")
    print("="*50)
    
    creative_mode = False
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'creative':
            creative_mode = not creative_mode
            mode_status = "ON" if creative_mode else "OFF"
            print(f"Creative mode: {mode_status}")
            continue
        elif user_input == '':
            continue
        
        try:
            if creative_mode:
                response = llm.generate_creative_text(user_input, max_length=100, temperature=1.1)
                print(f"AI (Creative): {response}")
            else:
                response = llm.generate_response(user_input, temperature=0.8)
                print(f"AI: {response}")
        except Exception as e:
            print(f"Error generating response: {e}")

if __name__ == "__main__":
    main()