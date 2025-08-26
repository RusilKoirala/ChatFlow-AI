"""
Silent Inference Script for API Use
===================================
This script provides text generation without debug output for API integration.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import random
import numpy as np
import sys
import os

# Suppress warnings and info messages
import warnings
warnings.filterwarnings("ignore")
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

# Set random seeds for reproducible generation
def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

class LLMInference:
    def __init__(self, model_path="./fine_tuned_model", fallback_model="distilgpt2"):
        """
        Initialize inference engine silently
        
        Args:
            model_path: Path to fine-tuned model
            fallback_model: Fallback model if fine-tuned model not found
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(model_path)
        except Exception as e:
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