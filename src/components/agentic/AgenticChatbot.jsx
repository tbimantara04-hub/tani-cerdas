import React, { useState, useRef, useEffect, useImperativeHandle, forwardRef } from 'react';
import { MessageCircle, X, Send, Loader2, Bot, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

/**
 * AgenticChatbot Component
 * Enhanced chatbot with agentic system support
 * Backwards compatible with legacy system
 */
const AgenticChatbot = forwardRef((props, ref) => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { 
            id: 1, 
            text: "Halo! Saya Tani-Cerdas AI. Ada yang bisa saya bantu terkait pertanian hari ini?", 
            sender: "bot",
            agent: "system"
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [farmerId, setFarmerId] = useState('default');
    const [systemMode, setSystemMode] = useState('agentic'); // 'agentic' or 'legacy'
    const [activeAgent, setActiveAgent] = useState(null);
    const messagesEndRef = useRef(null);

    const API_BASE = 'http://localhost:8000';

    useEffect(() => {
        detectSystemMode();
        loadChatHistory();
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const detectSystemMode = async () => {
        try {
            const response = await axios.get(`${API_BASE}/`);
            const version = response.data?.version || '';
            const mode = version.includes('agentic') ? 'agentic' : 'legacy';
            setSystemMode(mode);
            console.log(`[Chatbot] System mode: ${mode}`);
        } catch (e) {
            console.error('Error detecting system mode:', e);
            setSystemMode('legacy');
        }
    };

    const loadChatHistory = async () => {
        try {
            const response = await axios.get(`${API_BASE}/api/history`, {
                params: { farmer_id: farmerId }
            });
            
            if (response.data && Array.isArray(response.data) && response.data.length > 0) {
                const historyMessages = response.data.flatMap((item, index) => {
                    const ts = item.timestamp ? new Date(item.timestamp).getTime() : index;
                    
                    const sanitize = (val) => {
                        if (typeof val === 'string') return val;
                        if (Array.isArray(val)) return val.map(v => typeof v === 'string' ? v : JSON.stringify(v)).join(' ');
                        if (typeof val === 'object' && val !== null) return JSON.stringify(val);
                        return String(val || '');
                    };

                    return [
                        { 
                            id: `hist-u-${index}-${ts}`, 
                            text: sanitize(item.user), 
                            sender: "user",
                            timestamp: item.timestamp
                        },
                        { 
                            id: `hist-b-${index}-${ts}`, 
                            text: sanitize(item.bot), 
                            sender: "bot",
                            agent: item.agent || 'unknown',
                            timestamp: item.timestamp
                        }
                    ];
                });
                
                setMessages(prev => {
                    const welcomeMsg = prev.find(m => m.id === 1);
                    const combined = [welcomeMsg, ...historyMessages].filter(Boolean);
                    const uniqueMap = new Map();
                    combined.forEach(m => uniqueMap.set(m.id, m));
                    return Array.from(uniqueMap.values());
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    };

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = {
            id: Date.now(),
            text: input,
            sender: 'user',
            timestamp: new Date().toISOString()
        };
        
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);
        setActiveAgent(null);

        try {
            const payload = {
                message: input,
                farmer_id: farmerId
            };

            const response = await axios.post(
                `${API_BASE}/api/chat`,
                payload
            );

            const botResponse = {
                id: Date.now() + 1,
                text: response.data.response,
                sender: 'bot',
                agent: response.data.agent || 'unknown',
                timestamp: new Date().toISOString()
            };

            if (systemMode === 'agentic') {
                setActiveAgent(response.data.agent);
            }

            setMessages(prev => [...prev, botResponse]);
        } catch (error) {
            console.error('Error sending message:', error);
            
            const errorMessage = {
                id: Date.now() + 1,
                text: error.response?.data?.detail || 'Maaf, terjadi kesalahan. Silakan coba lagi.',
                sender: 'bot',
                agent: 'error',
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    useImperativeHandle(ref, () => ({
        openChat: () => setIsOpen(true),
        closeChat: () => setIsOpen(false),
        toggleChat: () => setIsOpen(!isOpen),
        sendMessage: (msg) => {
            setInput(msg);
            setIsLoading(true);
        },
        clearHistory: () => setMessages([messages[0]])
    }));

    const getAgentColor = (agent) => {
        const colors = {
            'weather': 'from-blue-400 to-blue-600',
            'price': 'from-green-400 to-green-600',
            'farm': 'from-yellow-400 to-yellow-600',
            'knowledge': 'from-purple-400 to-purple-600',
            'advisory': 'from-pink-400 to-pink-600',
            'orchestrator': 'from-indigo-400 to-indigo-600',
            'unknown': 'from-gray-400 to-gray-600'
        };
        return colors[agent] || colors['unknown'];
    };

    const getAgentEmoji = (agent) => {
        const emojis = {
            'weather': '🌦️',
            'price': '💰',
            'farm': '🌾',
            'knowledge': '📚',
            'advisory': '🎯',
            'orchestrator': '🤖',
            'system': '✨'
        };
        return emojis[agent] || '🤖';
    };

    return (
        <>
            {/* Chat Toggle Button */}
            <motion.button
                onClick={() => setIsOpen(!isOpen)}
                className="fixed left-8 bottom-8 rounded-full shadow-lg hover:shadow-xl transition-all z-40 flex items-center justify-center"
                style={{
                    backgroundColor: '#2D5A27',
                    width: '60px',
                    height: '60px'
                }}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
            >
                <AnimatePresence mode="wait">
                    {isOpen ? (
                        <motion.div
                            key="close"
                            initial={{ rotate: 0 }}
                            animate={{ rotate: 180 }}
                            exit={{ rotate: 0 }}
                        >
                            <X size={28} className="text-white" />
                        </motion.div>
                    ) : (
                        <motion.div
                            key="open"
                            initial={{ rotate: 180 }}
                            animate={{ rotate: 0 }}
                            exit={{ rotate: 180 }}
                        >
                            <MessageCircle size={28} className="text-white" />
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.button>

            {/* Chat Window */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.8, y: 20 }}
                        className="fixed left-8 bottom-24 w-96 bg-white rounded-lg shadow-2xl flex flex-col z-40 max-h-[600px]"
                    >
                        {/* Header */}
                        <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-4 rounded-t-lg flex justify-between items-center">
                            <div className="flex items-center gap-2">
                                <Bot size={20} />
                                <span className="font-bold">Tani-Cerdas AI</span>
                                {systemMode === 'agentic' && (
                                    <span className="text-xs bg-green-800 px-2 py-1 rounded flex items-center gap-1">
                                        <Zap size={12} /> Agentic
                                    </span>
                                )}
                            </div>
                        </div>

                        {/* Active Agent Badge */}
                        {activeAgent && systemMode === 'agentic' && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`bg-gradient-to-r ${getAgentColor(activeAgent)} text-white text-xs font-semibold px-4 py-2 flex items-center gap-2`}
                            >
                                {getAgentEmoji(activeAgent)}
                                <span>{activeAgent.charAt(0).toUpperCase() + activeAgent.slice(1)} Agent</span>
                            </motion.div>
                        )}

                        {/* Messages Container */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
                            {messages.map((msg) => (
                                <motion.div
                                    key={msg.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div className={`max-w-xs px-4 py-2 rounded-lg ${
                                        msg.sender === 'user'
                                            ? 'bg-green-600 text-white rounded-br-none'
                                            : 'bg-gray-200 text-gray-800 rounded-bl-none'
                                    }`}>
                                        <p className="text-sm whitespace-pre-wrap break-words">{msg.text}</p>
                                        {msg.agent && systemMode === 'agentic' && msg.sender === 'bot' && (
                                            <p className="text-xs mt-1 opacity-70">
                                                {getAgentEmoji(msg.agent)} {msg.agent}
                                            </p>
                                        )}
                                    </div>
                                </motion.div>
                            ))}
                            
                            {isLoading && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="flex justify-start"
                                >
                                    <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg rounded-bl-none flex items-center gap-2">
                                        <Loader2 size={16} className="animate-spin" />
                                        <span className="text-sm">Sedang memproses...</span>
                                    </div>
                                </motion.div>
                            )}
                            
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Area */}
                        <div className="border-t p-3 bg-white rounded-b-lg">
                            <div className="flex gap-2">
                                <textarea
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Tanya sesuatu..."
                                    className="flex-1 resize-none border rounded-lg p-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                    rows="2"
                                    disabled={isLoading}
                                />
                                <motion.button
                                    onClick={sendMessage}
                                    disabled={isLoading || !input.trim()}
                                    className="bg-green-600 text-white p-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                >
                                    <Send size={18} />
                                </motion.button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
});

AgenticChatbot.displayName = 'AgenticChatbot';

export default AgenticChatbot;
