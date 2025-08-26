# toy_lm.py — Very small word-level next-word predictor using PyTorch
# Requirements: pip install torch tqdm

import torch
import torch.nn as nn
import random
from tqdm import trange

# -----------------------
# 1) Prepare toy dataset
# -----------------------
raw_text = """
hello how are you doing today
i hope you are doing well
hello i like machine learning
machine learning is fun and powerful
you can build models that predict the next word
this is a tiny dataset to learn patterns

the weather is nice today
i am going to the park later
would you like to come with me
it is a sunny and beautiful day
let's enjoy the outdoors while we can

artificial intelligence is changing the world
neural networks are inspired by the human brain
language models can generate realistic text
deep learning is a powerful tool for many tasks

programming in python is enjoyable and productive
pytorch makes building models easier
you can train a model on your own data
the model learns patterns from the input
you can then use it to generate predictions

reading books can improve your vocabulary
writing regularly helps develop clear thinking
communication is an important life skill
learning new skills takes time and practice
"""

# Tokenize and build vocabulary
tokens = raw_text.lower().strip().split()
vocab = sorted(set(tokens))
stoi = {word: i for i, word in enumerate(vocab)}
itos = {i: word for word, i in stoi.items()}

# Convert tokens to integer indices
data = [stoi[word] for word in tokens]

# Create training data: context (N words) -> next word
context_size = 3
X, Y = [], []
for i in range(len(data) - context_size):
    X.append(data[i:i + context_size])
    Y.append(data[i + context_size])
X = torch.tensor(X, dtype=torch.long)  # (num_samples, context_size)
Y = torch.tensor(Y, dtype=torch.long)  # (num_samples,)

# -----------------------
# 2) Define the model
# -----------------------
class TinyLM(nn.Module):
    def __init__(self, vocab_size, emb_dim=32, hidden_dim=64):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, emb_dim)
        self.lstm = nn.LSTM(emb_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        # x: (batch_size, context_size)
        embedded = self.embedding(x)         # (batch_size, context_size, emb_dim)
        output, _ = self.lstm(embedded)      # (batch_size, context_size, hidden_dim)
        last_hidden = output[:, -1, :]       # (batch_size, hidden_dim)
        logits = self.fc(last_hidden)        # (batch_size, vocab_size)
        return logits

# -----------------------
# 3) Training setup
# -----------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = TinyLM(len(vocab)).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
loss_fn = nn.CrossEntropyLoss()

def train_model(epochs=500, batch_size=8):
    model.train()
    for epoch in trange(epochs):
        permutation = torch.randperm(X.size(0))
        batch_losses = []
        for i in range(0, X.size(0), batch_size):
            indices = permutation[i:i+batch_size]
            xb, yb = X[indices].to(device), Y[indices].to(device)

            optimizer.zero_grad()
            logits = model(xb)
            loss = loss_fn(logits, yb)
            loss.backward()
            optimizer.step()
            batch_losses.append(loss.item())

        if (epoch + 1) % 100 == 0:
            avg_loss = sum(batch_losses) / len(batch_losses)
            print(f"Epoch {epoch+1}: avg loss = {avg_loss:.4f}")

# -----------------------
# 4) Text generation
# -----------------------
def predict_next_word(context_words, top_k=5, temperature=1.0):
    model.eval()
    indices = [stoi.get(word, 0) for word in context_words[-context_size:]]
    xb = torch.tensor([indices], dtype=torch.long).to(device)

    with torch.no_grad():
        logits = model(xb)[0] / temperature
        probs = torch.softmax(logits, dim=-1).cpu().numpy()

    # Sample from top_k choices
    top_indices = probs.argsort()[-top_k:][::-1]
    top_probs = probs[top_indices]
    top_probs = top_probs / top_probs.sum()
    next_idx = random.choices(top_indices, weights=top_probs, k=1)[0]
    return itos[next_idx]

def generate_text(seed="hello how are", length=10):
    words = seed.lower().strip().split()
    for _ in range(length):
        next_word = predict_next_word(words)
        words.append(next_word)
    return " ".join(words)

# -----------------------
# 5) Run training & demo
# -----------------------
if __name__ == "__main__":
    print("Vocabulary:", vocab)
    train_model(epochs=1000)

    print("\n--- Sample generations ---")
    starters = ["hello how are", "machine learning is", "you can build"]
    for seed in starters:
        print(f"Seed: '{seed}' -> {generate_text(seed, length=6)}")

    # Interactive loop
    print("\nType a seed to continue (type 'quit' to exit):")
    while True:
        user_input = input("You: ").strip().lower()
        if user_input == "quit":
            break
        continuation = generate_text(seed=user_input, length=10)
        print("AI:", continuation)
