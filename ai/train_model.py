"""
Fine-tuning Script for Small Language Model
===========================================
This script fine-tunes a pre-trained model (DistilGPT-2) on custom conversational data.
"""

import torch
import random
import numpy as np
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import json
import os

# Set random seeds for reproducibility
def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

set_seed(42)

class LLMTrainer:
    def __init__(self, model_name="distilgpt2", output_dir="./fine_tuned_model"):
        """
        Initialize the trainer with a base model
        
        Args:
            model_name: Hugging Face model name (distilgpt2, gpt2, microsoft/DialoGPT-small)
            output_dir: Directory to save the fine-tuned model
        """
        self.model_name = model_name
        self.output_dir = output_dir
        
        print(f"Loading tokenizer and model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Add padding token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
    def prepare_dataset(self, conversations):
        """
        Prepare conversational data for training
        
        Args:
            conversations: List of conversation strings
        """
        print("Preparing dataset...")
        
        # Tokenize conversations
        def tokenize_function(examples):
            # Add special tokens to mark conversation boundaries
            texts = [f"<|startoftext|>{conv}<|endoftext|>" for conv in examples["text"]]
            return self.tokenizer(
                texts,
                truncation=True,
                padding=False,
                max_length=256,  # Reduced from 512 for faster training
                return_overflowing_tokens=False,
            )
        
        # Create dataset
        dataset = Dataset.from_dict({"text": conversations})
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names,
        )
        
        return tokenized_dataset
    
    def train(self, dataset, epochs=2, batch_size=8, learning_rate=1e-4):
        """
        Fine-tune the model on the prepared dataset
        """
        print("Starting training...")
        
        # Training arguments - optimized for speed
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            save_steps=1000,  # Save less frequently
            save_total_limit=1,  # Keep only 1 checkpoint
            prediction_loss_only=True,
            learning_rate=learning_rate,
            warmup_steps=10,  # Reduced warmup
            logging_steps=10,  # Log more frequently to show progress
            logging_dir=f"{self.output_dir}/logs",
            report_to=None,  # Disable wandb/tensorboard
            dataloader_num_workers=0,  # Disable multiprocessing for stability
            fp16=torch.cuda.is_available(),  # Use mixed precision if GPU available
        )
        
        # Data collator for language modeling
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # We're doing causal LM, not masked LM
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=dataset,
        )
        
        # Train the model
        trainer.train()
        
        # Save the final model
        trainer.save_model()
        self.tokenizer.save_pretrained(self.output_dir)
        
        print(f"Model saved to {self.output_dir}")

def create_sample_dataset():
    """
    Create a small sample conversational dataset for fast training
    You can replace this with your own data
    """
    conversations = [
        "Human: Hello, how are you? AI: I'm doing well, thanks! How can I help you today?",
        "Human: What is machine learning? AI: Machine learning is when computers learn patterns from data to make predictions.",
        "Human: Can you help me code? AI: Yes, I'd be happy to help you with coding! What do you need assistance with?",
        "Human: How do neural networks work? AI: Neural networks use interconnected nodes to process information, similar to brain neurons.",
        "Human: What's Python good for? AI: Python is great for data science, web development, automation, and AI applications.",
        "Human: Explain AI simply. AI: AI is making computers smart enough to solve problems and make decisions like humans do.",
        "Human: How do I learn programming? AI: Start with basics, practice daily, build small projects, and don't fear making mistakes!",
        "Human: What can you do? AI: I can help with coding, answer questions, explain concepts, and have conversations.",
    ]
    
    # Small dataset for fast training - only duplicate once
    extended_conversations = conversations * 2
    
    return extended_conversations

def main():
    """
    Main training function
    """
    print("=== LLM Fine-tuning Script ===")
    
    # Initialize trainer
    trainer = LLMTrainer(model_name="distilgpt2")
    
    # Create or load dataset
    conversations = create_sample_dataset()
    print(f"Dataset size: {len(conversations)} conversations")
    
    # Prepare dataset
    dataset = trainer.prepare_dataset(conversations)
    
    # Train the model - fast settings
    trainer.train(
        dataset=dataset,
        epochs=2,  # Reduced epochs for speed
        batch_size=4,  # Slightly larger batch for efficiency
        learning_rate=1e-4  # Higher learning rate for faster convergence
    )
    
    print("Training completed!")

if __name__ == "__main__":
    main()