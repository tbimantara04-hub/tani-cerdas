import React, { useState, useRef, useEffect, useImperativeHandle, forwardRef } from 'react';
import { MessageCircle, X, Send, Loader2, Bot, Mic, MicOff, Volume2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const Chatbot = forwardRef((props, ref) => {
    const [isOpen, setIsOpen] = useState(false);
    const isOpenRef = useRef(false);
    const [messages, setMessages] = useState([
        { id: 1, text: "Halo! Saya Tani-Cerdas AI. Ada yang bisa saya bantu terkait pertanian hari ini?", sender: "bot" }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [llmMode, setLlmMode] = useState(() => localStorage.getItem('llmMode') || 'local');
    const messagesEndRef = useRef(null);
    const recognitionRef = useRef(null);

    // Initialize Speech Recognition for Chatbot
    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false;
            recognitionRef.current.interimResults = false;
            recognitionRef.current.lang = 'id-ID';

            recognitionRef.current.onresult = async (event) => {
                const transcript = event.results[0][0].transcript;
                console.log('Chatbot Voice Input:', transcript);
                setIsListening(false);
                // Send the voice input directly
                await sendMessageToAPI(transcript, true);
            };

            recognitionRef.current.onerror = (event) => {
                console.error('Chatbot speech recognition error', event.error);
                setIsListening(false);
            };

            recognitionRef.current.onend = () => {
                setIsListening(false);
            };
        }
        
        return () => {
            if (recognitionRef.current) recognitionRef.current.abort();
            stopSpeaking();
        };
    }, []);

    useEffect(() => {
        localStorage.setItem('llmMode', llmMode);
    }, [llmMode]);

    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current?.stop();
            setIsListening(false);
        } else {
            try {
                recognitionRef.current?.start();
                setIsListening(true);
            } catch (error) {
                console.error("Error starting recognition", error);
            }
        }
    };

    const speak = (text) => {
        if ('speechSynthesis' in window) {
            stopSpeaking();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'id-ID';
            utterance.onstart = () => setIsSpeaking(true);
            utterance.onend = () => setIsSpeaking(false);
            utterance.onerror = () => setIsSpeaking(false);
            window.speechSynthesis.speak(utterance);
        }
    };

    const stopSpeaking = () => {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            setIsSpeaking(false);
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await axios.get('http://127.0.0.1:8000/api/history');
                if (response.data && Array.isArray(response.data) && response.data.length > 0) {
                    const historyMessages = response.data.flatMap((item, index) => {
                        const ts = item.timestamp ? new Date(item.timestamp).getTime() : index;
                        
                        // SANITIZATION: Ensure text is always a string to prevent React rendering crashes
                        const sanitize = (val) => {
                            if (typeof val === 'string') return val;
                            if (Array.isArray(val)) return val.map(v => typeof v === 'string' ? v : JSON.stringify(v)).join(' ');
                            if (typeof val === 'object' && val !== null) return JSON.stringify(val);
                            return String(val || '');
                        };

                        return [
                            { id: `hist-u-${index}-${ts}`, text: sanitize(item.user), sender: "user" },
                            { id: `hist-b-${index}-${ts}`, text: sanitize(item.bot), sender: "bot" }
                        ];
                    });
                    
                    setMessages(prev => {
                        const welcomeMsg = prev.find(m => m.id === 1);
                        // Filter out any duplicates and merge history
                        const combined = [welcomeMsg, ...historyMessages].filter(Boolean);
                        const uniqueMap = new Map();
                        combined.forEach(m => uniqueMap.set(m.id, m));
                        return Array.from(uniqueMap.values());
                    });
                }
            } catch (error) {
                console.error("Error fetching chat history:", error);
            }
        };
        
        fetchHistory();
    }, []);

    useEffect(() => {
        if (isOpen) {
            scrollToBottom();
        }
    }, [messages, isOpen]);

    // Core send logic, returns the bot response text
    const sendMessageToAPI = async (userMessage, readAloud = false) => {
        const newUserMsg = { id: Date.now(), text: userMessage, sender: "user" };
        setMessages(prev => [...prev, newUserMsg]);
        setIsLoading(true);

        try {
            const response = await axios.post('http://127.0.0.1:8000/api/chat', {
                message: userMessage,
                llm_mode: llmMode
            });
            
            // SANITIZATION: Handle potential array/object responses from bot
            const rawBotMsg = response.data.response;
            const sanitizedText = typeof rawBotMsg === 'string' ? rawBotMsg : JSON.stringify(rawBotMsg);
            
            const botMsg = { id: Date.now() + 1, text: sanitizedText, sender: "bot" };
            setMessages(prev => [...prev, botMsg]);
            
            // Read aloud if requested (e.g. from voice input)
            if (readAloud) {
                speak(sanitizedText);
            }
            
            return sanitizedText;
        } catch (error) {
            console.error("Error communicating with chatbot:", error);
            let errorText = "Maaf, terjadi kesalahan saat menghubungi server.";
            if (error.response && error.response.data && error.response.data.detail) {
                errorText = `Error dari server: ${error.response.data.detail}`;
            }
            const errorMsg = { id: Date.now() + 1, text: errorText, sender: "bot" };
            setMessages(prev => [...prev, errorMsg]);
            return errorText;
        } finally {
            setIsLoading(false);
        }
    };

    const handleSend = async () => {
        if (!input.trim()) return;
        const userMessage = input.trim();
        setInput('');
        await sendMessageToAPI(userMessage);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Keep isOpenRef in sync with isOpen state
    useEffect(() => {
        isOpenRef.current = isOpen;
    }, [isOpen]);

    // Expose methods to parent (VoiceAssistant) via ref
    useImperativeHandle(ref, () => ({
        // Open the chatbot window
        open: () => setIsOpen(true),
        // Close the chatbot window
        close: () => setIsOpen(false),
        // Check if chatbot is open - uses ref to avoid stale closure
        isOpen: () => isOpenRef.current,
        // Send a message programmatically and return the bot's response
        sendMessage: async (message) => {
            setIsOpen(true); // Auto-open chatbot when sending via voice
            // Small delay to let the UI open first
            await new Promise(resolve => setTimeout(resolve, 300));
            const botResponse = await sendMessageToAPI(message);
            return botResponse;
        }
    }));

    return (
        <>
            {/* Floating Button */}
            <motion.button
                className="chatbot-toggle-btn"
                onClick={() => setIsOpen(true)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                style={{
                    position: 'fixed',
                    bottom: '90px',
                    left: '20px', // Put on the left, VoiceAssistant is on the right
                    width: '56px',
                    height: '56px',
                    borderRadius: '50%',
                    backgroundColor: '#2D5A27',
                    color: 'white',
                    border: 'none',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                    display: isOpen ? 'none' : 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    zIndex: 1000
                }}
            >
                <MessageCircle size={28} />
            </motion.button>

            {/* Chat Window */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="chatbot-window"
                        style={{
                            position: 'fixed',
                            bottom: '90px',
                            left: '20px',
                            width: '350px',
                            maxWidth: 'calc(100vw - 40px)',
                            height: '500px',
                            maxHeight: 'calc(100vh - 120px)',
                            backgroundColor: 'white',
                            borderRadius: '20px',
                            boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
                            display: 'flex',
                            flexDirection: 'column',
                            overflow: 'hidden',
                            zIndex: 1001,
                            border: '1px solid #eee'
                        }}
                    >
                        {/* Header */}
                        <div style={{
                            padding: '16px',
                            backgroundColor: '#2D5A27',
                            color: 'white',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <Bot size={24} />
                                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', color: 'white' }}>Tani-Cerdas AI</h3>
                            </div>
                            
                            <div style={{ display: 'flex', alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: '20px', padding: '2px 4px', margin: '0 8px' }}>
                                <button 
                                    onClick={() => setLlmMode('local')}
                                    style={{ 
                                        background: llmMode === 'local' ? 'white' : 'transparent', 
                                        color: llmMode === 'local' ? '#2D5A27' : 'white',
                                        border: 'none', borderRadius: '16px', padding: '4px 12px', fontSize: '12px', fontWeight: 'bold', cursor: 'pointer',
                                        transition: 'all 0.2s'
                                    }}
                                >
                                    💻 Local
                                </button>
                                <button 
                                    onClick={() => setLlmMode('api')}
                                    style={{ 
                                        background: llmMode === 'api' ? 'white' : 'transparent', 
                                        color: llmMode === 'api' ? '#2D5A27' : 'white',
                                        border: 'none', borderRadius: '16px', padding: '4px 12px', fontSize: '12px', fontWeight: 'bold', cursor: 'pointer',
                                        transition: 'all 0.2s'
                                    }}
                                >
                                    ☁️ API
                                </button>
                            </div>

                            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                                {isSpeaking && (
                                    <button 
                                        onClick={stopSpeaking}
                                        title="Hentikan suara"
                                        style={{ background: 'none', border: 'none', color: '#F4B41A', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center' }}
                                    >
                                        <Volume2 size={20} />
                                    </button>
                                )}
                                <button 
                                    onClick={() => setIsOpen(false)}
                                    style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center' }}
                                >
                                    <X size={20} />
                                </button>
                            </div>
                        </div>

                        {/* Messages Area */}
                        <div style={{
                            flex: 1,
                            overflowY: 'auto',
                            padding: '16px',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '12px',
                            backgroundColor: '#f9fdf9'
                        }}>
                            {messages.map((msg) => (
                                <div key={msg.id} style={{
                                    display: 'flex',
                                    justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                                    gap: '8px'
                                }}>
                                    {msg.sender === 'bot' && (
                                        <div style={{
                                            width: '32px',
                                            height: '32px',
                                            borderRadius: '50%',
                                            backgroundColor: '#E8F5E9',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            flexShrink: 0
                                        }}>
                                            <Bot size={16} color="#2D5A27" />
                                        </div>
                                    )}
                                    <div style={{
                                        maxWidth: '75%',
                                        padding: '10px 14px',
                                        borderRadius: '16px',
                                        borderBottomRightRadius: msg.sender === 'user' ? '4px' : '16px',
                                        borderBottomLeftRadius: msg.sender === 'bot' ? '4px' : '16px',
                                        backgroundColor: msg.sender === 'user' ? '#2D5A27' : 'white',
                                        color: msg.sender === 'user' ? 'white' : '#333',
                                        boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                                        border: msg.sender === 'user' ? 'none' : '1px solid #eee',
                                        fontSize: '14px',
                                        lineHeight: '1.5',
                                        whiteSpace: 'pre-wrap'
                                    }}>
                                        {msg.text}
                                    </div>
                                </div>
                            ))}
                            {isLoading && (
                                <div style={{ display: 'flex', justifyContent: 'flex-start', gap: '8px' }}>
                                    <div style={{
                                            width: '32px',
                                            height: '32px',
                                            borderRadius: '50%',
                                            backgroundColor: '#E8F5E9',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            flexShrink: 0
                                        }}>
                                            <Bot size={16} color="#2D5A27" />
                                    </div>
                                    <div style={{
                                        padding: '10px 14px',
                                        borderRadius: '16px',
                                        borderBottomLeftRadius: '4px',
                                        backgroundColor: 'white',
                                        border: '1px solid #eee',
                                        display: 'flex',
                                        alignItems: 'center'
                                    }}>
                                        <Loader2 size={16} color="#666" style={{ animation: 'spin-chatbot 1s linear infinite' }} />
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Area */}
                        <div style={{
                            padding: '12px',
                            borderTop: '1px solid #eee',
                            backgroundColor: 'white',
                            display: 'flex',
                            gap: '8px',
                            alignItems: 'center'
                        }}>
                            <button
                                onClick={toggleListening}
                                title={isListening ? "Berhenti mendengarkan" : "Gunakan suara"}
                                style={{
                                    width: '40px',
                                    height: '40px',
                                    borderRadius: '50%',
                                    backgroundColor: isListening ? '#ef4444' : '#f5f5f5',
                                    color: isListening ? 'white' : '#666',
                                    border: 'none',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                            >
                                {isListening ? <MicOff size={18} /> : <Mic size={18} />}
                            </button>
                            
                            <textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder={isListening ? "Mendengarkan..." : "Ketik pesan..."}
                                disabled={isListening}
                                style={{
                                    flex: 1,
                                    resize: 'none',
                                    border: '1px solid #e5e5e5',
                                    borderRadius: '20px',
                                    padding: '10px 16px',
                                    height: '44px',
                                    fontFamily: 'inherit',
                                    fontSize: '14px',
                                    outline: 'none',
                                    backgroundColor: isListening ? '#f9fafb' : 'white'
                                }}
                            />
                            <button
                                onClick={handleSend}
                                disabled={!input.trim() || isLoading}
                                style={{
                                    width: '44px',
                                    height: '44px',
                                    borderRadius: '50%',
                                    backgroundColor: input.trim() && !isLoading ? '#2D5A27' : '#e5e5e5',
                                    color: 'white',
                                    border: 'none',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    cursor: input.trim() && !isLoading ? 'pointer' : 'default',
                                    transition: 'background-color 0.2s'
                                }}
                            >
                                <Send size={18} />
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
            
            <style>
                {`
                @keyframes spin-chatbot {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                `}
            </style>
        </>
    );
});

Chatbot.displayName = 'Chatbot';

export default Chatbot;
