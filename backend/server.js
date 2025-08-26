import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { v4 as uuidv4 } from 'uuid';
import { spawn } from 'child_process';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// In-memory storage for conversations (use database in production)
const conversations = new Map();

// AI Model Interface Class
class AIInterface {
  constructor() {
    this.isReady = false;
    this.initializeAI();
  }

  async initializeAI() {
    try {
      console.log('Initializing AI model...');
      // Check if AI model exists
      const modelPath = path.join(__dirname, '../ai/fine_tuned_model');
      const modelExists = await fs.pathExists(modelPath);
      
      if (!modelExists) {
        console.log('Fine-tuned model not found, will use base model');
      }
      
      this.isReady = true;
      console.log('AI interface ready!');
    } catch (error) {
      console.error('Error initializing AI:', error);
      this.isReady = false;
    }
  }

  async generateResponse(message, conversationId = null) {
    return new Promise((resolve, reject) => {
      if (!this.isReady) {
        reject(new Error('AI model not ready'));
        return;
      }

      // Prepare the Python script execution
      const pythonScript = path.join(__dirname, '../ai/api_interface.py');
      const pythonProcess = spawn('python', [pythonScript], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: path.join(__dirname, '../ai')
      });

      let responseData = '';
      let errorData = '';

      // Send input to Python script
      const inputData = JSON.stringify({
        message: message,
        conversation_id: conversationId,
        max_length: 150,
        temperature: 0.8
      });

      pythonProcess.stdin.write(inputData);
      pythonProcess.stdin.end();

      // Collect output
      pythonProcess.stdout.on('data', (data) => {
        responseData += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        errorData += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          try {
            // Clean the response data
            const cleanedData = responseData.trim();
            
            // Try to find JSON in the output (in case there are debug messages)
            let jsonData = cleanedData;
            const lines = cleanedData.split('\n');
            
            // Look for the last line that looks like JSON
            for (let i = lines.length - 1; i >= 0; i--) {
              const line = lines[i].trim();
              if (line.startsWith('{') && line.endsWith('}')) {
                jsonData = line;
                break;
              }
            }
            
            // Parse the JSON response from Python
            const response = JSON.parse(jsonData);
            
            if (response.success) {
              resolve({
                response: response.response,
                mode: response.mode || 'default',
                conversation_id: conversationId || uuidv4(),
                timestamp: new Date().toISOString()
              });
            } else {
              reject(new Error(response.error || 'AI processing failed'));
            }
          } catch (error) {
            console.error('Raw Python output:', responseData);
            console.error('Parse error:', error.message);
            reject(new Error('Failed to parse AI response: ' + error.message));
          }
        } else {
          console.error('Python stderr:', errorData);
          reject(new Error('AI process failed: ' + errorData));
        }
      });

      // Timeout after 30 seconds
      setTimeout(() => {
        pythonProcess.kill();
        reject(new Error('AI response timeout'));
      }, 30000);
    });
  }
}

// Initialize AI interface
const ai = new AIInterface();

// Routes

// Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    ai_ready: ai.isReady,
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { message, conversation_id } = req.body;

    if (!message || typeof message !== 'string' || !message.trim()) {
      return res.status(400).json({ error: 'Message is required and must be a non-empty string' });
    }

    const conversationId = conversation_id || uuidv4();
    const startTime = Date.now();

    // Generate AI response
    const aiResponse = await ai.generateResponse(message.trim(), conversationId);
    const generationTime = (Date.now() - startTime) / 1000;

    // Store conversation
    if (!conversations.has(conversationId)) {
      conversations.set(conversationId, []);
    }

    const conversation = conversations.get(conversationId);
    conversation.push({
      user: message.trim(),
      ai: aiResponse.response,
      timestamp: aiResponse.timestamp,
      mode: aiResponse.mode
    });

    // Keep only last 20 exchanges per conversation
    if (conversation.length > 20) {
      conversation.splice(0, conversation.length - 20);
    }

    res.json({
      response: aiResponse.response,
      conversation_id: conversationId,
      mode: aiResponse.mode,
      generation_time: generationTime,
      timestamp: aiResponse.timestamp
    });

  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ 
      error: 'Failed to generate response',
      details: error.message 
    });
  }
});

// Get conversation history
app.get('/api/conversations/:id', (req, res) => {
  const { id } = req.params;
  
  if (!conversations.has(id)) {
    return res.status(404).json({ error: 'Conversation not found' });
  }

  const history = conversations.get(id);
  res.json({
    conversation_id: id,
    history: history,
    message_count: history.length
  });
});

// List all conversations
app.get('/api/conversations', (req, res) => {
  const conversationList = [];
  
  for (const [id, history] of conversations.entries()) {
    if (history.length > 0) {
      const lastMessage = history[history.length - 1];
      conversationList.push({
        id: id,
        last_message: lastMessage.user.substring(0, 50) + (lastMessage.user.length > 50 ? '...' : ''),
        timestamp: lastMessage.timestamp,
        message_count: history.length
      });
    }
  }

  // Sort by timestamp (most recent first)
  conversationList.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  res.json({ conversations: conversationList });
});

// Delete conversation
app.delete('/api/conversations/:id', (req, res) => {
  const { id } = req.params;
  
  if (!conversations.has(id)) {
    return res.status(404).json({ error: 'Conversation not found' });
  }

  conversations.delete(id);
  res.json({ message: 'Conversation deleted successfully' });
});

// Creative text generation
app.post('/api/generate', async (req, res) => {
  try {
    const { prompt, max_length = 150, temperature = 1.0 } = req.body;

    if (!prompt || typeof prompt !== 'string' || !prompt.trim()) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    const startTime = Date.now();
    const response = await ai.generateResponse(prompt.trim(), null);
    const generationTime = (Date.now() - startTime) / 1000;

    res.json({
      generated_text: response.response,
      generation_time: generationTime,
      timestamp: response.timestamp
    });

  } catch (error) {
    console.error('Generation error:', error);
    res.status(500).json({ 
      error: 'Failed to generate text',
      details: error.message 
    });
  }
});

// Serve static files from frontend build (for production)
const frontendBuildPath = path.join(__dirname, '../frontend/dist');
if (fs.existsSync(frontendBuildPath)) {
  app.use(express.static(frontendBuildPath));
  
  // Catch-all handler for React Router
  app.get('*', (req, res) => {
    if (!req.path.startsWith('/api')) {
      res.sendFile(path.join(frontendBuildPath, 'index.html'));
    }
  });
}

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Server error:', error);
  res.status(500).json({ 
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Start server
app.listen(PORT, () => {
  console.log(`Smart AI Backend Server running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/api/health`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Received SIGTERM, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('Received SIGINT, shutting down gracefully...');
  process.exit(0);
});