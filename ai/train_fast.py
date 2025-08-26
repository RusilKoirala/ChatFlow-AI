"""
Ultra-Fast Training Script
==========================
This script provides minimal training for immediate testing and development.
Perfect for quick iterations and testing the pipeline.
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
import os

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

set_seed(42)

def ultra_fast_train():
    """
    Ultra-fast training for immediate testing
    """
    print("🚀 Ultra-Fast Training Mode")
    print("This will do minimal training just to test the pipeline.")
    
    model_name = "distilgpt2"
    output_dir = "./fine_tuned_model"
    
    # Load model and tokenizer
    print(f"Loading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Minimal dataset
    conversations = [
        "Human: Hi AI: Hello there!",
        "Human: How are you? AI: I'm doing well, thanks!",
        "Human: What can you do? AI: I can chat and help with questions.",
        "Human: Tell me about AI. AI: AI helps computers think and solve problems.",
    ]
    
    # Tokenize
    def tokenize_function(examples):
        texts = [f"<|startoftext|>{conv}<|endoftext|>" for conv in examples["text"]]
        return tokenizer(
            texts,
            truncation=True,
            padding=False,
            max_length=128,  # Very short sequences
            return_overflowing_tokens=False,
        )
    
    dataset = Dataset.from_dict({"text": conversations})
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names,
    )
    
    # Ultra-fast training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=1,  # Just 1 epoch
        per_device_train_batch_size=2,
        save_steps=1000,
        save_total_limit=1,
        prediction_loss_only=True,
        learning_rate=1e-3,  # High learning rate
        warmup_steps=0,  # No warmup
        logging_steps=1,  # Log every step
        logging_dir=f"{output_dir}/logs",
        report_to=None,
        dataloader_num_workers=0,
        fp16=torch.cuda.is_available(),
        max_steps=10,  # Stop after just 10 steps!
    )
    
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=tokenized_dataset,
    )
    
    print("Starting ultra-fast training (10 steps only)...")
    trainer.train()
    
    # Save model
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)
    
    print(f"✅ Ultra-fast training completed! Model saved to {output_dir}")
    print("This model is minimally trained but ready for testing the pipeline.")

if __name__ == "__main__":
    ultra_fast_train()