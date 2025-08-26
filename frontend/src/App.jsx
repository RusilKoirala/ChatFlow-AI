import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { Send, User, Trash2, MessageSquare, Plus, Settings, Menu } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, vs } from 'react-syntax-highlighter/dist/esm/styles/prism';
import Logo from './components/Logo';
import ThemeToggle from './components/ThemeToggle';
import { useTheme } from './hooks/useTheme';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState(null);
    const [conversations, setConversations] = useState([]);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const messagesEndRef = useRef(null);
    const { theme, toggleTheme } = useTheme();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        loadConversations();
    }, []);

    const loadConversations = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/conversations`);
            setConversations(response.data.conversations);
        } catch (error) {
            console.error('Error loading conversations:', error);
        }
    };

    const startNewConversation = () => {
        setMessages([]);
        setConversationId(null);
    };

    const loadConversation = async (convId) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/conversations/${convId}`);
            const history = response.data.history;

            const formattedMessages = [];
            history.forEach(exchange => {
                formattedMessages.push({
                    id: uuidv4(),
                    text: exchange.user,
                    sender: 'user',
                    timestamp: new Date(exchange.timestamp)
                });
                formattedMessages.push({
                    id: uuidv4(),
                    text: exchange.ai,
                    sender: 'assistant',
                    timestamp: new Date(exchange.timestamp)
                });
            });

            setMessages(formattedMessages);
            setConversationId(convId);
        } catch (error) {
            console.error('Error loading conversation:', error);
        }
    };

    const deleteConversation = async (convId) => {
        try {
            await axios.delete(`${API_BASE_URL}/conversations/${convId}`);
            loadConversations();
            if (conversationId === convId) {
                startNewConversation();
            }
        } catch (error) {
            console.error('Error deleting conversation:', error);
        }
    };

    const sendMessage = async () => {
        if (!inputMessage.trim() || isLoading) return;

        const userMessage = {
            id: uuidv4(),
            text: inputMessage,
            sender: 'user',
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);

        try {
            const response = await axios.post(`${API_BASE_URL}/chat`, {
                message: inputMessage,
                conversation_id: conversationId
            });

            const assistantMessage = {
                id: uuidv4(),
                text: response.data.response,
                sender: 'assistant',
                timestamp: new Date()
            };

            setMessages(prev => [...prev, assistantMessage]);
            setConversationId(response.data.conversation_id);
            loadConversations();
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                id: uuidv4(),
                text: 'Sorry, I encountered an error. Please try again.',
                sender: 'assistant',
                timestamp: new Date(),
                isError: true
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const formatTime = (date) => {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    // Theme-based styles
    const themeStyles = {
        light: {
            bg: 'bg-slate-50',
            sidebar: 'bg-white border-gray-200',
            header: 'bg-white border-gray-200',
            message: 'bg-white border-gray-200 text-gray-900',
            userMessage: 'bg-indigo-600 text-white',
            input: 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-500',
            text: 'text-gray-900',
            textSecondary: 'text-gray-600',
            textMuted: 'text-gray-500',
            hover: 'hover:bg-gray-50',
            border: 'border-gray-200'
        },
        dark: {
            bg: 'bg-gray-950',
            sidebar: 'bg-gray-900 border-gray-700',
            header: 'bg-gray-900 border-gray-700',
            message: 'bg-gray-800 border-gray-700 text-gray-100',
            userMessage: 'bg-indigo-600 text-white',
            input: 'bg-gray-800 border-gray-600 text-white placeholder-gray-400',
            text: 'text-white',
            textSecondary: 'text-gray-300',
            textMuted: 'text-gray-400',
            hover: 'hover:bg-gray-800',
            border: 'border-gray-700'
        }
    };

    const styles = themeStyles[theme];

    return (
        <div className={`h-screen w-screen ${styles.bg} flex overflow-hidden transition-colors duration-300`}>
            {/* Sidebar */}
            <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 ${styles.sidebar} border-r flex flex-col shadow-sm`}>
                <div className={`p-4 border-b ${styles.border}`}>
                    <div className="flex items-center gap-3 mb-4">
                        <Logo size="md" theme={theme} />
                        <div>
                            <h1 className={`font-semibold ${styles.text}`}>ChatFlow AI</h1>
                            <p className={`text-xs ${styles.textMuted}`}>Intelligent Assistant</p>
                        </div>
                    </div>
                    <button
                        onClick={startNewConversation}
                        className="w-full bg-indigo-600 text-white hover:bg-indigo-700 px-4 py-2.5 rounded-xl flex items-center justify-center gap-2 transition-all font-medium"
                    >
                        <Plus className="w-4 h-4" />
                        New Chat
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-4">
                    <h3 className={`text-sm font-medium ${styles.textSecondary} mb-3`}>Recent Chats</h3>
                    {conversations.length === 0 ? (
                        <p className={`${styles.textMuted} text-sm`}>No conversations yet</p>
                    ) : (
                        <div className="space-y-2">
                            {conversations.map((conv) => (
                                <div
                                    key={conv.id}
                                    className={`p-3 rounded-lg cursor-pointer transition-all group ${styles.hover} ${
                                        conversationId === conv.id ? `bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800` : `border border-transparent`
                                    }`}
                                    onClick={() => loadConversation(conv.id)}
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex-1 min-w-0">
                                            <p className={`text-sm font-medium truncate ${styles.text}`}>{conv.last_message}</p>
                                            <p className={`text-xs ${styles.textMuted} mt-1`}>
                                                {conv.message_count} messages
                                            </p>
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                deleteConversation(conv.id);
                                            }}
                                            className={`opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-all p-1 hover:bg-red-50 dark:hover:bg-red-900/20 rounded`}
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Header */}
                <div className={`${styles.header} border-b p-4`}>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => setSidebarOpen(!sidebarOpen)}
                                className={`p-2 ${styles.hover} rounded-lg transition-colors`}
                            >
                                <Menu className={`w-5 h-5 ${styles.textSecondary}`} />
                            </button>
                            {!sidebarOpen && (
                                <Logo size="sm" theme={theme} showText />
                            )}
                        </div>
                        <div className="flex items-center gap-2">
                            <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
                            <button className={`p-2 ${styles.hover} rounded-lg transition-colors`}>
                                <Settings className={`w-5 h-5 ${styles.textSecondary}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Messages */}
                <div className={`flex-1 overflow-y-auto p-6 ${styles.bg}`}>
                    {messages.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full">
                            <Logo size="2xl" className="mb-6" theme={theme} />
                            <h2 className={`text-2xl font-semibold mb-2 ${styles.text}`}>Welcome to ChatFlow AI</h2>
                            <p className={`text-center max-w-md ${styles.textSecondary}`}>
                                Your intelligent conversation partner. Ask me anything about coding, creative writing, analysis, or general questions.
                            </p>
                        </div>
                    ) : (
                        <div className="max-w-4xl mx-auto space-y-6">
                            {messages.map((message) => (
                                <div
                                    key={message.id}
                                    className={`flex gap-4 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    {message.sender === 'assistant' && (
                                        <div className="flex-shrink-0">
                                            <Logo size="sm" theme={theme} />
                                        </div>
                                    )}

                                    <div
                                        className={`max-w-3xl px-4 py-3 rounded-2xl shadow-sm ${
                                            message.sender === 'user'
                                                ? styles.userMessage
                                                : message.isError
                                                ? 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200 border border-red-200 dark:border-red-800'
                                                : `${styles.message} border`
                                        }`}
                                    >
                                        {message.sender === 'assistant' ? (
                                            <ReactMarkdown
                                                components={{
                                                    code({ node, inline, className, children, ...props }) {
                                                        const match = /language-(\w+)/.exec(className || '');
                                                        return !inline && match ? (
                                                            <SyntaxHighlighter
                                                                style={theme === 'dark' ? vscDarkPlus : vs}
                                                                language={match[1]}
                                                                PreTag="div"
                                                                className="rounded-lg my-2"
                                                                {...props}
                                                            >
                                                                {String(children).replace(/\n$/, '')}
                                                            </SyntaxHighlighter>
                                                        ) : (
                                                            <code className={`${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'} px-2 py-1 rounded text-sm font-mono`} {...props}>
                                                                {children}
                                                            </code>
                                                        );
                                                    }
                                                }}
                                            >
                                                {message.text}
                                            </ReactMarkdown>
                                        ) : (
                                            <p className="whitespace-pre-wrap">{message.text}</p>
                                        )}

                                        <div className="flex items-center justify-between mt-2 text-xs opacity-60">
                                            <span>{formatTime(message.timestamp)}</span>
                                        </div>
                                    </div>

                                    {message.sender === 'user' && (
                                        <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-cyan-400 rounded-full flex items-center justify-center flex-shrink-0">
                                            <User className="w-4 h-4 text-white" />
                                        </div>
                                    )}
                                </div>
                            ))}

                            {isLoading && (
                                <div className="flex gap-4 justify-start">
                                    <div className="flex-shrink-0">
                                        <Logo size="sm" theme={theme} />
                                    </div>
                                    <div className={`${styles.message} border shadow-sm px-4 py-3 rounded-2xl`}>
                                        <div className="flex items-center space-x-3">
                                            <div className="flex space-x-1">
                                                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                                                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                            </div>
                                            <span className={`text-sm ${styles.textSecondary}`}>Thinking...</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className={`border-t ${styles.border} p-4 ${styles.header}`}>
                    <div className="max-w-4xl mx-auto">
                        <div className="flex gap-3 items-end">
                            <div className="flex-1 relative">
                                <textarea
                                    value={inputMessage}
                                    onChange={(e) => setInputMessage(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="Type your message..."
                                    className={`w-full ${styles.input} border rounded-2xl px-4 py-3 pr-12 resize-none focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-colors`}
                                    rows="1"
                                    disabled={isLoading}
                                    style={{
                                        minHeight: '48px',
                                        maxHeight: '200px'
                                    }}
                                    onInput={(e) => {
                                        e.target.style.height = 'auto';
                                        e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
                                    }}
                                />
                                <button
                                    onClick={sendMessage}
                                    disabled={!inputMessage.trim() || isLoading}
                                    className="absolute right-2 top-1/2 transform -translate-y-1/2 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all"
                                >
                                    <Send className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;