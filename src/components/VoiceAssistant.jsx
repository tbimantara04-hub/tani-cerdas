import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, Square, Globe } from 'lucide-react';

import { infoData } from '../data/agriculturalData';

const VoiceAssistant = ({ activeTab, onNavigate, onPriceTabChange, onInfoCategoryChange, infoCategory, selectedPlant, chatbotRef }) => {
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [supported, setSupported] = useState(true);
    const [voiceStatus, setVoiceStatus] = useState(''); // Status text for user feedback
    const [isChatbotMode, setIsChatbotMode] = useState(false); // Track if in chatbot-only mode
    const recognitionRef = useRef(null);

    // Auto-read plant details when selected
    useEffect(() => {
        // Skip auto-read if chatbot is open (voice is in chatbot-only mode)
        if (chatbotRef?.current?.isOpen()) return;
        if (activeTab === 'info' && selectedPlant && infoCategory) {
            const plantData = selectedPlant.data[infoCategory];
            if (plantData) {
                // Short delay
                setTimeout(() => {
                    const tipsText = plantData.tips.slice(0, 3).join('. '); // Read max 3 tips to keep it concise
                    speak(`Ini panduan untuk ${selectedPlant.name}. ${plantData.title}. ${tipsText}.`);
                }, 500);
            }
        }
    }, [selectedPlant, infoCategory, activeTab]);

    // Auto-read info category when selected
    useEffect(() => {
        // Skip auto-read if chatbot is open (voice is in chatbot-only mode)
        if (chatbotRef?.current?.isOpen()) return;
        if (activeTab === 'info' && infoCategory && !selectedPlant) {
            const categoryData = infoData.find(item => item.categoryKey === infoCategory);
            if (categoryData) {
                // Short delay to allow UI transition
                setTimeout(() => {
                    speak(`Ini adalah menu ${categoryData.title}. ${categoryData.desc} Silakan pilih jenis tanaman.`);
                }, 500);
            }
        }
    }, [infoCategory, activeTab, selectedPlant]);

    // Initialize Speech Recognition
    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false; // Stop after one command usually better for valid commands
            recognitionRef.current.interimResults = false;
            recognitionRef.current.lang = 'id-ID';

            recognitionRef.current.onresult = (event) => {
                const transcript = event.results[0][0].transcript.toLowerCase();
                console.log('Voice Command:', transcript);
                const processCommand = async (command) => {
                    // ===== CHATBOT MODE - Only process chatbot questions =====
                    if (isChatbotMode) {
                        // Exit chatbot mode with specific commands
                        if (command.includes('selesai') || command.includes('tutup') || command.includes('keluar')) {
                            setIsChatbotMode(false);
                            if (chatbotRef?.current) {
                                chatbotRef.current.close();
                            }
                            speak('Keluar dari mode chat. Saya siap membantu dengan perintah lain.');
                            return;
                        }

                        // Send all other commands directly to chatbot while in chatbot mode
                        if (command.trim() && chatbotRef?.current) {
                            await sendToChatbot(command);
                        }
                        return;
                    }

                    // ===== CHATBOT INTEGRATION =====
                    // Detect "tanya ai", "chat", "tanya", or "hai ai" commands
                    const chatTriggers = ['tanya ai', 'tanya a i', 'chat ai', 'hai ai', 'hey ai', 'hei ai'];
                    const askTriggers = ['tanya ', 'tanyakan ', 'tolong tanya ', 'tolong tanyakan '];

                    // Check for exact chat triggers (open chatbot only and ENTER CHATBOT MODE)
                    if (chatTriggers.some(trigger => command.trim() === trigger)) {
                        if (chatbotRef?.current) {
                            chatbotRef.current.open();
                            setIsChatbotMode(true); // Enter chatbot-only mode
                            speak('Chatbot sudah dibuka. Silakan ucapkan pertanyaan Anda.');
                            // Auto-start listening for chatbot questions
                            setTimeout(() => {
                                if (recognitionRef.current && !isListening) {
                                    recognitionRef.current.start();
                                    setIsListening(true);
                                    setVoiceStatus('Mendengarkan untuk Chatbot...');
                                }
                            }, 1000);
                        }
                        return;
                    }

                    // Check for "tanya ai [pertanyaan]" pattern - send question to chatbot
                    for (const trigger of chatTriggers) {
                        if (command.startsWith(trigger + ' ')) {
                            const question = command.substring(trigger.length + 1).trim();
                            if (question && chatbotRef?.current) {
                                setIsChatbotMode(true); // Enter chatbot-only mode
                                if (!chatbotRef.current.isOpen?.()) {
                                    chatbotRef.current.open();
                                }
                                await sendToChatbot(question);
                            }
                            return;
                        }
                    }

                    // Check for "tanya [pertanyaan]" pattern
                    for (const trigger of askTriggers) {
                        if (command.startsWith(trigger)) {
                            const question = command.substring(trigger.length).trim();
                            if (question && chatbotRef?.current) {
                                if (!chatbotRef.current.isOpen?.()) {
                                    chatbotRef.current.open();
                                }
                                await sendToChatbot(question);
                            }
                            return;
                        }
                    }
                    setIsChatbotMode(true); // Enter chatbot mode
                    if (!chatbotRef.current.isOpen?.()) {
                        chatbotRef.current.open();
                    }
                    await sendToChatbot(question);
                }
                return;
            }
        }

        // Check for "tanya [pertanyaan]" pattern
        for (const trigger of askTriggers) {
            if (command.startsWith(trigger)) {
                const question = command.substring(trigger.length).trim();
                if (question && chatbotRef?.current) {
                    if (!chatbotRef.current.isOpen?.()) {
                        chatbotRef.current.open();
                    }
                    await sendToChatbot(question);
                }
                return;
            }
        }

>>>>>>> eb1e6ed (Agentic overhaul: add multi-agent orchestrator, agents, memory, tools, API and frontend integration)
        // ===== EXISTING NAVIGATION COMMANDS =====
        // Info sub-commands
        if (command.includes('bibit')) {
            onNavigate('info');
            if (onInfoCategoryChange) onInfoCategoryChange('bibit');
            speak('Membuka info pemilihan bibit');
        } else if (command.includes('tanam') || command.includes('nanam')) {
            onNavigate('info');
            if (onInfoCategoryChange) onInfoCategoryChange('penanaman');
            speak('Membuka info penanaman');
        } else if (command.includes('panen') && !command.includes('pasca')) {
            onNavigate('info');
            if (onInfoCategoryChange) onInfoCategoryChange('panen');
            speak('Membuka info waktu panen');
        } else if (command.includes('olahan') || command.includes('pasca panen')) {
            onNavigate('info');
            if (onInfoCategoryChange) onInfoCategoryChange('olahan');
            speak('Membuka info olahan panen');
        } else if (command.includes('hama') || command.includes('penyakit') || command.includes('opt')) {
            onNavigate('info');
            if (onInfoCategoryChange) onInfoCategoryChange('opt');
            speak('Membuka info pengendalian hama');
        }
        // Main tabs
        else if (command.includes('cuaca') || command.includes('langit')) {
            onNavigate('cuaca');
            speak('Membuka halaman Cuaca');
        } else if (command.includes('info') || command.includes('berita') || command.includes('tips')) {
            onNavigate('info');
            if (onInfoCategoryChange) onInfoCategoryChange(null); // Reset to main list
            speak('Membuka halaman Informasi');
        } else if (command.includes('pupuk')) {
            onNavigate('harga');
            if (onPriceTabChange) onPriceTabChange('pupuk');
            speak('Membuka harga pupuk');
        } else if (command.includes('harga') || command.includes('pasar') || command.includes('jual')) {
            onNavigate('harga');
            if (onPriceTabChange) onPriceTabChange('pangan'); // Default to pangan
            speak('Membuka halaman Harga');
        } else if (command.includes('baca') || command.includes('ngomong')) {
            readCurrentPage();
        } else if (command.includes('buka chat') || command.includes('tanya ai')) {
            } else {
                // If command doesn't match any navigation, send it to chatbot as a question
                if (chatbotRef?.current) {
                    await sendToChatbot(command);
                } else {
                    speak('Maaf, saya tidak mengerti. Gunakan tombol mic di chatbot untuk bertanya pada AI.');
                }
            }
        };

        // Send message to chatbot and read the response aloud
        const sendToChatbot = async (question) => {
            setVoiceStatus('Mengirim ke AI...');
            speak(`Mengirimkan pertanyaan: ${question}`);
        
            try {
                const botResponse = await chatbotRef.current.sendMessage(question);
            
                // Only update status if not in chatbot mode
                if (!isChatbotMode) {
                    setVoiceStatus('Membacakan jawaban...');
                }
            
                // Wait a moment for the "sending" speech to finish, then read the response
                await new Promise(resolve => setTimeout(resolve, 1000));
                speak(`Jawaban dari AI: ${botResponse}`);
            
                // If in chatbot mode, automatically start listening for next question after response is read
                if (isChatbotMode) {
                    // Wait for speech to finish (approximately based on text length)
                    const estimatedDuration = (botResponse.length / 100) * 1000 + 2000; // rough estimate
                    await new Promise(resolve => setTimeout(resolve, estimatedDuration));
                
                    // Auto-start listening for next question
                    if (recognitionRef.current && !isListening) {
                        recognitionRef.current.start();
                        setIsListening(true);
                        setVoiceStatus('Siap untuk pertanyaan berikutnya...');
                    }
                }
            } catch (error) {
                console.error('Error sending to chatbot:', error);
                speak('Maaf, terjadi kesalahan saat menghubungi AI.');
            
                // In chatbot mode, restart listening after error
                if (isChatbotMode) {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    if (recognitionRef.current && !isListening) {
                        recognitionRef.current.start();
                        setIsListening(true);
                        setVoiceStatus('Siap untuk pertanyaan berikutnya...');
                    }
                }
            } finally {
                // Don't clear voiceStatus in chatbot mode
                if (!isChatbotMode) {
                    setVoiceStatus('');
                }
            }
        };
            }
        } finally {
            // Don't clear voiceStatus in chatbot mode
            if (!isChatbotMode) {
                setVoiceStatus('');
            }
>>>>>>> eb1e6ed (Agentic overhaul: add multi-agent orchestrator, agents, memory, tools, API and frontend integration)
        }
    };

    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current.stop();
            setVoiceStatus('');
        } else {
            try {
                recognitionRef.current.start();
                setIsListening(true);
                setVoiceStatus('Mendengarkan...');
            } catch (error) {
                console.error("Error starting recognition", error);
            }
        }
    };

    const speak = (text) => {
        if ('speechSynthesis' in window) {
            stopSpeaking(); // Stop any previous speech
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'id-ID';

            utterance.onstart = () => setIsSpeaking(true);
            utterance.onend = () => {
                setIsSpeaking(false);
                setVoiceStatus('');
            };
            utterance.onerror = () => {
                setIsSpeaking(false);
                setVoiceStatus('');
            };

            window.speechSynthesis.speak(utterance);
        }
    };

    const stopSpeaking = () => {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            setIsSpeaking(false);
        }
    };

    const readCurrentPage = () => {
        // Basic screen reader logic: read the text content of the main area
        // Use a slight delay to ensure render if navigation happened recently, though manual trigger doesn't need it.
        const mainContent = document.querySelector('main');
        if (mainContent) {
            // Clean up text a bit
            let textToRead = mainContent.innerText || mainContent.textContent;
            // Limit length or clean up excessive whitespace if needed
            textToRead = textToRead.replace(/\s+/g, ' ').trim();

            // Contextual intro
            let intro = "";
            if (activeTab === 'cuaca') intro = "Berikut adalah info cuaca. ";
            else if (activeTab === 'info') intro = "Berikut adalah artikel informasi. ";
            else if (activeTab === 'harga') intro = "Berikut adalah daftar harga. ";

            if (textToRead.length > 0) {
                speak(intro + textToRead);
            } else {
                speak("Tidak ada konten yang dapat dibaca di halaman ini.");
            }
        }
    };

    const handleSpeakToggle = () => {
        if (isSpeaking) {
            stopSpeaking();
        } else {
            readCurrentPage();
        }
    };

    if (!supported) return null;

    return (
        <div className="voice-assistant-controls" style={{
            position: 'fixed',
            bottom: '90px',
            right: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
            zIndex: 1000,
            alignItems: 'flex-end'
        }}>
            {/* Status Label */}
            {voiceStatus && (
                <div style={{
                    backgroundColor: isChatbotMode ? 'rgba(59, 130, 246, 0.9)' : 'rgba(45, 90, 39, 0.9)',
                    color: 'white',
                    padding: '8px 14px',
                    borderRadius: '20px',
                    fontSize: '13px',
                    whiteSpace: 'nowrap',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                    animation: 'fadeInUp 0.3s ease',
                    fontWeight: isChatbotMode ? '600' : 'normal'
                }}>
                    {voiceStatus}
                </div>
            )}

            {/* Chatbot Mode Indicator */}
            {isChatbotMode && (
                <div style={{
                    backgroundColor: 'rgba(59, 130, 246, 0.9)',
                    color: 'white',
                    padding: '8px 14px',
                    borderRadius: '20px',
                    fontSize: '12px',
                    whiteSpace: 'nowrap',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                    animation: 'fadeInUp 0.3s ease',
                    fontWeight: '600',
                    border: '2px solid rgba(255,255,255,0.3)'
                }}>
                    🎙️ Mode Chat AI Aktif
                </div>
            )}

            {/* Listening Button */}
            <button
                onClick={toggleListening}
                style={{
                    backgroundColor: isListening ? '#ef4444' : (isChatbotMode ? '#3b82f6' : '#2D5A27'),
                    color: 'white',
                    border: isChatbotMode ? '2px solid rgba(255,255,255,0.5)' : 'none',
                    borderRadius: '50%',
                    width: '56px',
                    height: '56px',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    boxShadow: isListening
                        ? '0 4px 6px rgba(239,68,68,0.3), 0 0 0 4px rgba(239,68,68,0.15)'
                        : (isChatbotMode ? '0 4px 6px rgba(59,130,246,0.3)' : '0 4px 6px rgba(0,0,0,0.1)'),
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    animation: isListening ? 'pulse-voice 1.5s ease-in-out infinite' : (isChatbotMode ? 'pulse-chatbot 2s ease-in-out infinite' : 'none')
                }}
                aria-label={isChatbotMode ? "Mode Chat Aktif" : "Fitur Suara"}
            >
                {isListening ? <MicOff size={24} /> : <Mic size={24} />}
            </button>

            {/* Read Page Button */}
            <button
                onClick={handleSpeakToggle}
                style={{
                    backgroundColor: isSpeaking ? '#eab308' : '#ffffff',
                    color: isSpeaking ? 'white' : '#2D5A27',
                    border: '1px solid #e5e5e5',
                    borderRadius: '50%',
                    width: '56px',
                    height: '56px',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                }}
                aria-label="Bacakan Halaman"
            >
                {isSpeaking ? <Square size={20} fill="currentColor" /> : <Volume2 size={24} />}
            </button>

            {/* Listening Indicator Label (Optional) */}
            {isListening && (
                <div style={{
                    position: 'absolute',
                    right: '65px',
                    top: voiceStatus ? '55px' : '15px',
                    backgroundColor: 'rgba(0,0,0,0.7)',
                    color: 'white',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    whiteSpace: 'nowrap'
                }}>
                    Mendengarkan...
                </div>
            )}

            <style>
                {`
                @keyframes pulse-voice {
                    0% { box-shadow: 0 4px 6px rgba(239,68,68,0.3), 0 0 0 0px rgba(239,68,68,0.3); }
                    50% { box-shadow: 0 4px 6px rgba(239,68,68,0.3), 0 0 0 12px rgba(239,68,68,0); }
                    100% { box-shadow: 0 4px 6px rgba(239,68,68,0.3), 0 0 0 0px rgba(239,68,68,0.3); }
                }
                @keyframes fadeInUp {
                    from { opacity: 0; transform: translateY(8px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                `}
            </style>
        </div>
    );
};

export default VoiceAssistant;
