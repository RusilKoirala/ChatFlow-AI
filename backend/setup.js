#!/usr/bin/env node

import { spawn } from 'child_process';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('Setting up Smart AI Backend...');

// Check if AI model exists
const aiModelPath = path.join(__dirname, '../ai/fine_tuned_model');
const modelExists = fs.existsSync(aiModelPath);

if (!modelExists) {
  console.log('⚠️  AI model not found. Training a quick model...');
  
  // Run quick AI training
  const trainProcess = spawn('python', ['train_fast.py'], {
    cwd: path.join(__dirname, '../ai'),
    stdio: 'inherit'
  });
  
  trainProcess.on('close', (code) => {
    if (code === 0) {
      console.log('✅ AI model trained successfully!');
      startServer();
    } else {
      console.log('⚠️  AI training failed, but continuing with base model...');
      startServer();
    }
  });
} else {
  console.log('✅ AI model found!');
  startServer();
}

function startServer() {
  console.log('🚀 Starting Express server...');
  
  const serverProcess = spawn('node', ['server.js'], {
    cwd: __dirname,
    stdio: 'inherit'
  });
  
  serverProcess.on('close', (code) => {
    console.log(`Server exited with code ${code}`);
  });
}