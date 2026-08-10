import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, Square } from 'lucide-react';

import { infoData } from '../data/agriculturalData';

const VoiceAssistant = ({ activeTab, onNavigate, onPriceTabChange, onInfoCategoryChange, infoCategory, selectedPlant, chatbotRef }) => {
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [supported, setSupported] = useState(true);
    const [voiceStatus, setVoiceStatus] = useState('');
    const [isChatbotMode, setIsChatbotMode] = useState(false);
    const recognitionRef = useRef(null);

    // Triggers
    const chatTriggers = ['tanya ai', 'tanya a i', 'chat ai', 'hai ai', 'hey ai', 'hei ai'];
    const askTriggers = ['tanya ', 'tanyakan ', 'tolong tanya ', 'tolong tanyakan '];

    useEffect(() => {
        // Auto-read plant details when selected
        if (chatbotRef?.current?.isOpen && chatbotRef.current.isOpen()) return;
        if (activeTab === 'info' && selectedPlant && infoCategory) {
            const plantData = selectedPlant.data[infoCategory];
            if (plantData) {
                setTimeout(() => {
                    const tipsText = (plantData.tips || []).slice(0, 3).join('. ');
                    speak(`Ini panduan untuk ${selectedPlant.name}. ${plantData.title}. ${tipsText}.`);
                }, 500);
            }
        }
    }, [selectedPlant, infoCategory, activeTab]);

    useEffect(() => {
        // Auto-read info category when selected
        if (chatbotRef?.current?.isOpen && chatbotRef.current.isOpen()) return;
        if (activeTab === 'info' && infoCategory && !selectedPlant) {
            const categoryData = infoData.find(item => item.categoryKey === infoCategory);
            if (categoryData) {
                setTimeout(() => {
                    speak(`Ini adalah menu ${categoryData.title}. ${categoryData.desc} Silakan pilih jenis tanaman.`);
                }, 500);
            }
        }
    }, [infoCategory, activeTab, selectedPlant]);

    // Initialize SpeechRecognition
    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false;
            recognitionRef.current.interimResults = false;
            recognitionRef.current.lang = 'id-ID';

            recognitionRef.current.onresult = (event) => {
                const transcript = event.results[0][0].transcript.toLowerCase();
                console.log('Voice Command:', transcript);
                processCommand(transcript).catch(err => console.error('processCommand error', err));
                setIsListening(false);
            };

            recognitionRef.current.onerror = (event) => {
                console.error('Speech recognition error', event.error);
                setIsListening(false);
                setVoiceStatus('');
            };

            recognitionRef.current.onend = () => {
                setIsListening(false);
            };
        } else {
            setSupported(false);
        }

        return () => {
            if (recognitionRef.current) {
                try { recognitionRef.current.abort(); } catch (e) {}
            }
            stopSpeaking();
        };
    }, []);

    const processCommand = async (command) => {
        if (!command) return;

        // CHATBOT MODE: only forward to chatbot
        if (isChatbotMode) {
            if (command.includes('selesai') || command.includes('tutup') || command.includes('keluar')) {
                setIsChatbotMode(false);
                if (chatbotRef?.current?.close) chatbotRef.current.close();
                speak('Keluar dari mode chat. Saya siap membantu dengan perintah lain.');
                return;
            }

            if (command.trim() && chatbotRef?.current?.sendMessage) {
                await sendToChatbot(command);
            }
            return;
        }

        // CHATBOT INTEGRATION: open chatbot or send question
        if (chatTriggers.some(trigger => command.trim() === trigger)) {
            if (chatbotRef?.current?.open) {
                chatbotRef.current.open();
                setIsChatbotMode(true);
                speak('Chatbot sudah dibuka. Silakan ucapkan pertanyaan Anda.');
                setTimeout(() => {
                    if (recognitionRef.current && !isListening) {
                        try { recognitionRef.current.start(); setIsListening(true); setVoiceStatus('Mendengarkan untuk Chatbot...'); } catch(e){}
                    }
                }, 1000);
            }
            return;
        }

        for (const trigger of chatTriggers) {
            if (command.startsWith(trigger + ' ')) {
                const question = command.substring(trigger.length + 1).trim();
                if (question && chatbotRef?.current?.sendMessage) {
                    setIsChatbotMode(true);
                    if (chatbotRef.current.open) chatbotRef.current.open();
                    await sendToChatbot(question);
                }
                return;
            }
        }

        for (const trigger of askTriggers) {
            if (command.startsWith(trigger)) {
                const question = command.substring(trigger.length).trim();
                if (question && chatbotRef?.current?.sendMessage) {
                    if (chatbotRef.current.open) chatbotRef.current.open();
                    await sendToChatbot(question);
                }
                return;
            }
        }

        // NAVIGATION COMMANDS
        if (command.includes('bibit')) {
            onNavigate('info'); if (onInfoCategoryChange) onInfoCategoryChange('bibit'); speak('Membuka info pemilihan bibit');
        } else if (command.includes('tanam') || command.includes('nanam')) {
            onNavigate('info'); if (onInfoCategoryChange) onInfoCategoryChange('penanaman'); speak('Membuka info penanaman');
        } else if (command.includes('panen') && !command.includes('pasca')) {
            onNavigate('info'); if (onInfoCategoryChange) onInfoCategoryChange('panen'); speak('Membuka info waktu panen');
        } else if (command.includes('olahan') || command.includes('pasca panen')) {
            onNavigate('info'); if (onInfoCategoryChange) onInfoCategoryChange('olahan'); speak('Membuka info olahan panen');
        } else if (command.includes('hama') || command.includes('penyakit') || command.includes('opt')) {
            onNavigate('info'); if (onInfoCategoryChange) onInfoCategoryChange('opt'); speak('Membuka info pengendalian hama');
        } else if (command.includes('cuaca') || command.includes('langit')) {
            onNavigate('cuaca'); speak('Membuka halaman Cuaca');
        } else if (command.includes('info') || command.includes('berita') || command.includes('tips')) {
            onNavigate('info'); if (onInfoCategoryChange) onInfoCategoryChange(null); speak('Membuka halaman Informasi');
        } else if (command.includes('pupuk')) {
            onNavigate('harga'); if (onPriceTabChange) onPriceTabChange('pupuk'); speak('Membuka harga pupuk');
        } else if (command.includes('harga') || command.includes('pasar') || command.includes('jual')) {
            onNavigate('harga'); if (onPriceTabChange) onPriceTabChange('pangan'); speak('Membuka halaman Harga');
        } else if (command.includes('baca') || command.includes('ngomong')) {
            readCurrentPage();
        } else if (command.includes('buka chat') || command.includes('tanya ai')) {
            if (chatbotRef?.current?.open) { chatbotRef.current.open(); speak('Membuka chatbot AI.'); }
        } else if (command.includes('tutup chat') || command.includes('keluar chat')) {
            if (chatbotRef?.current?.close) { chatbotRef.current.close(); speak('Menutup chatbot.'); }
        } else {
            // fallback: send to chatbot
            if (chatbotRef?.current?.sendMessage) {
                await sendToChatbot(command);
            } else {
                speak('Maaf, saya tidak mengerti.');
            }
        }
    };

    const sendToChatbot = async (question) => {
        setVoiceStatus('Mengirim ke AI...');
        speak(`Mengirimkan pertanyaan: ${question}`);

        try {
            const botResponse = await chatbotRef.current.sendMessage(question);

            if (!isChatbotMode) setVoiceStatus('Membacakan jawaban...');

            await new Promise(resolve => setTimeout(resolve, 1000));
            speak(`Jawaban dari AI: ${botResponse}`);

            if (isChatbotMode) {
                const estimatedDuration = (botResponse?.length || 0) / 100 * 1000 + 2000;
                await new Promise(resolve => setTimeout(resolve, estimatedDuration));
                if (recognitionRef.current && !isListening) {
                    try { recognitionRef.current.start(); setIsListening(true); setVoiceStatus('Siap untuk pertanyaan berikutnya...'); } catch(e){}
                }
            }
        } catch (error) {
            console.error('Error sending to chatbot:', error);
            speak('Maaf, terjadi kesalahan saat menghubungi AI.');
            if (isChatbotMode) {
                await new Promise(resolve => setTimeout(resolve, 2000));
                if (recognitionRef.current && !isListening) {
                    try { recognitionRef.current.start(); setIsListening(true); setVoiceStatus('Siap untuk pertanyaan berikutnya...'); } catch(e){}
                }
            }
        } finally {
            if (!isChatbotMode) setVoiceStatus('');
        }
    };

    const toggleListening = () => {
        if (!recognitionRef.current) return;
        if (isListening) {
            try { recognitionRef.current.stop(); } catch(e){}
            setVoiceStatus('');
        } else {
            try { recognitionRef.current.start(); setIsListening(true); setVoiceStatus('Mendengarkan...'); } catch(e) { console.error(e); }
        }
    };

    const speak = (text) => {
        if ('speechSynthesis' in window) {
            stopSpeaking();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'id-ID';
            utterance.onstart = () => setIsSpeaking(true);
            utterance.onend = () => { setIsSpeaking(false); setVoiceStatus(''); };
            utterance.onerror = () => { setIsSpeaking(false); setVoiceStatus(''); };
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
        const mainContent = document.querySelector('main');
        if (mainContent) {
            let textToRead = mainContent.innerText || mainContent.textContent || '';
            textToRead = textToRead.replace(/\s+/g, ' ').trim();
            let intro = '';
            if (activeTab === 'cuaca') intro = 'Berikut adalah info cuaca. ';
            else if (activeTab === 'info') intro = 'Berikut adalah artikel informasi. ';
            else if (activeTab === 'harga') intro = 'Berikut adalah daftar harga. ';
            if (textToRead.length > 0) speak(intro + textToRead);
            else speak('Tidak ada konten yang dapat dibaca di halaman ini.');
        }
    };

    if (!supported) return null;

    return (
        <div className="voice-assistant-controls" style={{ position: 'fixed', bottom: '90px', right: '20px', display: 'flex', flexDirection: 'column', gap: '10px', zIndex: 1000, alignItems: 'flex-end' }}>
            {voiceStatus && (
                <div style={{ backgroundColor: isChatbotMode ? 'rgba(59, 130, 246, 0.9)' : 'rgba(45, 90, 39, 0.9)', color: 'white', padding: '8px 14px', borderRadius: '20px', fontSize: '13px', whiteSpace: 'nowrap', boxShadow: '0 2px 8px rgba(0,0,0,0.15)', animation: 'fadeInUp 0.3s ease', fontWeight: isChatbotMode ? '600' : 'normal' }}>{voiceStatus}</div>
            )}

            {isChatbotMode && (
                <div style={{ backgroundColor: 'rgba(59, 130, 246, 0.9)', color: 'white', padding: '8px 14px', borderRadius: '20px', fontSize: '12px', whiteSpace: 'nowrap', boxShadow: '0 2px 8px rgba(0,0,0,0.15)', animation: 'fadeInUp 0.3s ease', fontWeight: '600', border: '2px solid rgba(255,255,255,0.3)' }}>🎙️ Mode Chat AI Aktif</div>
            )}

            <button onClick={toggleListening} style={{ backgroundColor: isListening ? '#ef4444' : (isChatbotMode ? '#3b82f6' : '#2D5A27'), color: 'white', border: isChatbotMode ? '2px solid rgba(255,255,255,0.5)' : 'none', borderRadius: '50%', width: '56px', height: '56px', display: 'flex', justifyContent: 'center', alignItems: 'center', boxShadow: isListening ? '0 4px 6px rgba(239,68,68,0.3), 0 0 0 4px rgba(239,68,68,0.15)' : (isChatbotMode ? '0 4px 6px rgba(59,130,246,0.3)' : '0 4px 6px rgba(0,0,0,0.1)'), cursor: 'pointer', transition: 'all 0.2s ease', animation: isListening ? 'pulse-voice 1.5s ease-in-out infinite' : (isChatbotMode ? 'pulse-chatbot 2s ease-in-out infinite' : 'none') }} aria-label={isChatbotMode ? "Mode Chat Aktif" : "Fitur Suara"}>
                {isListening ? <MicOff size={24} /> : <Mic size={24} />}
            </button>

            <button onClick={() => { if (isSpeaking) stopSpeaking(); else readCurrentPage(); }} style={{ backgroundColor: isSpeaking ? '#eab308' : '#ffffff', color: isSpeaking ? 'white' : '#2D5A27', border: '1px solid #e5e5e5', borderRadius: '50%', width: '56px', height: '56px', display: 'flex', justifyContent: 'center', alignItems: 'center', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', cursor: 'pointer', transition: 'all 0.2s ease' }} aria-label="Bacakan Halaman">
                {isSpeaking ? <Square size={20} fill="currentColor" /> : <Volume2 size={24} />}
            </button>

            {isListening && (<div style={{ position: 'absolute', right: '65px', top: voiceStatus ? '55px' : '15px', backgroundColor: 'rgba(0,0,0,0.7)', color: 'white', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', whiteSpace: 'nowrap' }}>Mendengarkan...</div>)}

            <style>{`@keyframes pulse-voice { 0% { box-shadow: 0 4px 6px rgba(239,68,68,0.3), 0 0 0 0px rgba(239,68,68,0.3); } 50% { box-shadow: 0 4px 6px rgba(239,68,68,0.3), 0 0 0 12px rgba(239,68,68,0); } 100% { box-shadow: 0 4px 6px rgba(239,68,68,0.3), 0 0 0 0px rgba(239,68,68,0.3); } } @keyframes fadeInUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }`}</style>
        </div>
    );
};

export default VoiceAssistant;
