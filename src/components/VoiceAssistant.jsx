import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, Square, Globe } from 'lucide-react';

import { infoData } from '../data/agriculturalData';

const VoiceAssistant = ({ activeTab, onNavigate, onPriceTabChange, onInfoCategoryChange, infoCategory, selectedPlant }) => {
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [supported, setSupported] = useState(true);
    const recognitionRef = useRef(null);

    // Auto-read plant details when selected
    useEffect(() => {
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
                processCommand(transcript);
                setIsListening(false);
            };

            recognitionRef.current.onerror = (event) => {
                console.error('Speech recognition error', event.error);
                setIsListening(false);
            };

            recognitionRef.current.onend = () => {
                setIsListening(false);
            };
        } else {
            setSupported(false);
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.abort();
            }
            stopSpeaking();
        };
    }, [activeTab]); // Depend on activeTab if we want context-aware commands later

    const processCommand = (command) => {
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
        } else {
            speak('Maaf, saya tidak mengerti.');
        }
    };

    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current.stop();
        } else {
            try {
                recognitionRef.current.start();
                setIsListening(true);
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
            zIndex: 1000
        }}>
            {/* Listening Button */}
            <button
                onClick={toggleListening}
                style={{
                    backgroundColor: isListening ? '#ef4444' : '#2D5A27',
                    color: 'white',
                    border: 'none',
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
                aria-label="Fitur Suara"
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
                    top: '15px',
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
        </div>
    );
};

export default VoiceAssistant;
