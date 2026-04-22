import React, { useState, useEffect } from 'react';
import { User, Map, Sprout, Save, ShieldCheck, Loader2, AlertCircle } from 'lucide-react';
import axios from 'axios';
import { motion } from 'framer-motion';

const FarmerProfile = () => {
    const [tanaman, setTanaman] = useState('');
    const [luasLahan, setLuasLahan] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/profile');
                setTanaman(response.data.tanaman || '');
                setLuasLahan(response.data.luas_lahan || '');
            } catch (error) {
                console.error("Error fetching profile:", error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchProfile();
    }, []);

    const handleSave = async (e) => {
        e.preventDefault();
        setIsSaving(true);
        setMessage({ type: '', text: '' });

        try {
            await axios.post('http://localhost:8000/api/profile', {
                tanaman: tanaman,
                luas_lahan: luasLahan
            });
            setMessage({ type: 'success', text: 'Profil berhasil diperbarui dan dienkripsi!' });
        } catch (error) {
            console.error("Error saving profile:", error);
            setMessage({ type: 'error', text: 'Gagal menyimpan profil.' });
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
                <Loader2 className="animate-spin" color="#2D5A27" size={32} />
            </div>
        );
    }

    return (
        <div className="farmer-profile">
            <h2 className="mb-4" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <User color="#2D5A27" /> Profil & Preferensi Petani
            </h2>

            <div className="card mb-4" style={{ padding: '24px' }}>
                <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '10px', 
                    marginBottom: '20px', 
                    backgroundColor: '#E8F5E9', 
                    padding: '12px', 
                    borderRadius: '12px',
                    color: '#2D5A27',
                    fontSize: '14px'
                }}>
                    <ShieldCheck size={20} />
                    <span>Data profil Anda dienkripsi dengan <b>AES-256</b> agar privasi lahan tetap terjaga.</span>
                </div>

                <form onSubmit={handleSave}>
                    <div className="mb-3">
                        <label className="form-label" style={{ fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <Sprout size={18} /> Jenis Tanaman Utama
                        </label>
                        <input 
                            type="text" 
                            className="form-control" 
                            value={tanaman}
                            onChange={(e) => setTanaman(e.target.value)}
                            placeholder="Contoh: Padi, Cabai, Jagung"
                            style={{ borderRadius: '10px', padding: '12px' }}
                        />
                        <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                            Chatbot akan memberikan saran spesifik untuk tanaman ini.
                        </div>
                    </div>

                    <div className="mb-4">
                        <label className="form-label" style={{ fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <Map size={18} /> Luas Lahan (m²)
                        </label>
                        <input 
                            type="text" 
                            className="form-control" 
                            value={luasLahan}
                            onChange={(e) => setLuasLahan(e.target.value)}
                            placeholder="Contoh: 1000m2 atau 1 Hektar"
                            style={{ borderRadius: '10px', padding: '12px' }}
                        />
                        <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                            Digunakan untuk kalkulasi kebutuhan pupuk dan pestisida.
                        </div>
                    </div>

                    <button 
                        type="submit" 
                        className="btn btn-primary w-100" 
                        disabled={isSaving}
                        style={{ 
                            backgroundColor: '#2D5A27', 
                            border: 'none', 
                            padding: '14px',
                            fontWeight: 'bold',
                            borderRadius: '12px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '10px'
                        }}
                    >
                        {isSaving ? <Loader2 size={20} className="animate-spin" /> : <Save size={20} />}
                        Simpan Profil
                    </button>
                </form>

                {message.text && (
                    <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        style={{ 
                            marginTop: '16px', 
                            padding: '12px', 
                            borderRadius: '10px',
                            backgroundColor: message.type === 'success' ? '#F0FFF4' : '#FFF5F5',
                            color: message.type === 'success' ? '#2F855A' : '#C53030',
                            fontSize: '14px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}
                    >
                        {message.type === 'success' ? <ShieldCheck size={18} /> : <AlertCircle size={18} />}
                        {message.text}
                    </motion.div>
                )}
            </div>

            <div className="card" style={{ padding: '20px', borderLeft: '4px solid #F6AD55', backgroundColor: '#FFFAF0' }}>
                <h4 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '8px' }}>💬 Tips Chatbot</h4>
                <p style={{ fontSize: '13px', color: '#744210', lineHeight: '1.5', margin: 0 }}>
                    Anda juga bisa memperbarui profil di atas cukup dengan berbicara kepada chatbot. 
                    Misal: <b>"Ingat ya, sekarang saya tanam Tomat di lahan 200m2"</b>. 
                    AI akan otomatis mengenali dan memperbarui profil Anda secara aman.
                </p>
            </div>

            <style>{`
                .animate-spin {
                    animation: spin 1s linear infinite;
                }
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
};

export default FarmerProfile;
