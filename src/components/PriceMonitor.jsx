import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, ArrowRight, Loader2, AlertCircle, Calendar } from 'lucide-react';
import axios from 'axios';

const PriceHistory = ({ history }) => {
    if (!history || history.length === 0) return null;

    const maxPrice = Math.max(...history.map(h => h.price));
    const minPrice = Math.min(...history.map(h => h.price));
    const range = maxPrice - minPrice || 1;

    return (
        <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#fff', borderRadius: '16px', border: '1px dashed #ddd' }}>
            <p style={{ fontSize: '13px', color: '#666', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Calendar size={14} />
                Tren 5 Hari Terakhir
            </p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', height: '80px', padding: '0 4px', gap: '4px' }}>
                {history.map((day, idx) => {
                    const height = ((day.price - minPrice) / range * 40) + 10;
                    return (
                        <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
                            <span style={{ fontSize: '9px', fontWeight: '600', color: idx === history.length - 1 ? '#2D5A27' : '#666', marginBottom: '4px' }}>
                                {day.price.toLocaleString()}
                            </span>
                            <div
                                style={{
                                    width: '100%',
                                    maxWidth: '16px',
                                    height: `${height}px`,
                                    backgroundColor: idx === history.length - 1 ? '#2D5A27' : '#A5D6A7',
                                    borderRadius: '4px',
                                    transition: 'height 0.3s'
                                }}
                            />
                            <span style={{ fontSize: '10px', color: '#888', marginTop: '4px' }}>{day.date.split('-')[2]}</span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

const PriceItem = ({ name, price, trend, unit, history }) => {
    const [showHistory, setShowHistory] = useState(false);

    return (
        <div className="card" style={{ marginBottom: '12px', cursor: 'pointer' }} onClick={() => setShowHistory(!showHistory)}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <p style={{ fontSize: '14px', color: '#666', margin: 0 }}>{name}</p>
                    <h3 style={{ fontSize: '20px', margin: '4px 0' }}>Rp {price.toLocaleString()} <span style={{ fontSize: '14px', fontWeight: '400' }}>/{unit}</span></h3>
                </div>
                <div style={{ textAlign: 'right' }}>
                    {trend === 'up' ? (
                        <div style={{ color: '#d32f2f', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <TrendingUp size={18} />
                            <span style={{ fontWeight: '700', fontSize: '14px' }}>Naik</span>
                        </div>
                    ) : trend === 'down' ? (
                        <div style={{ color: '#388e3c', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <TrendingDown size={18} />
                            <span style={{ fontWeight: '700', fontSize: '14px' }}>Turun</span>
                        </div>
                    ) : (
                        <div style={{ color: '#666', fontSize: '14px' }}>Stabil</div>
                    )}
                    <p style={{ fontSize: '10px', color: '#999', margin: '2px 0 0 0' }}>Klik detail</p>
                </div>
            </div>
            {showHistory && <PriceHistory history={history} />}
        </div>
    );
};

const PriceMonitor = () => {
    const [prices, setPrices] = useState([]);
    const [historyData, setHistoryData] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState('');
    const [isOffline, setIsOffline] = useState(!navigator.onLine);

    const targetCommodities = [
        "Beras Medium",
        "Cabai Merah Keriting",
        "Bawang Merah",
        "Jagung Tk Peternak"
    ];

    // Listen for online/offline status
    useEffect(() => {
        const handleOnline = () => setIsOffline(false);
        const handleOffline = () => setIsOffline(true);
        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);
        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, []);

    useEffect(() => {
        const fetchAllData = async () => {
            try {
                setLoading(true);

                // Load from cache first for instant display
                const cachedPrices = localStorage.getItem('prices');
                const cachedHistory = localStorage.getItem('historyData');
                const cachedUpdate = localStorage.getItem('lastUpdate');

                if (cachedPrices) setPrices(JSON.parse(cachedPrices));
                if (cachedHistory) setHistoryData(JSON.parse(cachedHistory));
                if (cachedUpdate) setLastUpdate(cachedUpdate);

                // Get today and last 4 days
                const dates = [];
                for (let i = 0; i < 5; i++) {
                    const d = new Date();
                    d.setDate(d.getDate() - i);
                    dates.push(d.toISOString().split('T')[0]);
                }
                dates.reverse(); // Oldest to newest

                const historyTemp = {};
                let latestPrices = [];
                let latestUpdateStr = '';

                // Fetch data for each date
                const promises = dates.map(async (date, index) => {
                    try {
                        const response = await axios.get(`/api-bapanas/api/front/harga-pangan-informasi?province_id=&city_id=&level_harga_id=3&date=${date}`, {
                            timeout: 5000 // Short timeout for low connection
                        });

                        if (response.data && response.data.status === 'success') {
                            const dailyData = response.data.data.filter(item =>
                                targetCommodities.some(target => item.name.toLowerCase().includes(target.toLowerCase()))
                            );

                            dailyData.forEach(item => {
                                if (!historyTemp[item.name]) historyTemp[item.name] = [];
                                historyTemp[item.name].push({
                                    date: date,
                                    price: item.today
                                });
                            });

                            // If it's the latest date
                            if (index === dates.length - 1) {
                                latestPrices = dailyData;
                                if (response.data.request_data && response.data.request_data[0]) {
                                    latestUpdateStr = response.data.request_data[0].today;
                                }
                            }
                        }
                    } catch (e) {
                        console.warn(`Failed to fetch data for ${date}`, e);
                    }
                });

                await Promise.all(promises);

                // Update state and cache if we got new data
                if (latestPrices.length > 0) {
                    setPrices(latestPrices);
                    setHistoryData(historyTemp);
                    if (latestUpdateStr) setLastUpdate(latestUpdateStr);

                    localStorage.setItem('prices', JSON.stringify(latestPrices));
                    localStorage.setItem('historyData', JSON.stringify(historyTemp));
                    if (latestUpdateStr) localStorage.setItem('lastUpdate', latestUpdateStr);
                    setError(null);
                } else if (!cachedPrices) {
                    // Only error if we have no cache and no new data
                    setError('Gagal memuat harga pasar. Periksa koneksi internet Anda.');
                }
            } catch (err) {
                console.error('Error fetching all price data:', err);
                if (!localStorage.getItem('prices')) {
                    setError('Gagal memuat harga pasar.');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchAllData();
    }, []);

    return (
        <div className="price-monitor">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                <div>
                    <h2 style={{ margin: 0 }}>Harga Pasar</h2>
                    {isOffline && (
                        <span style={{ fontSize: '12px', color: '#f57c00', fontWeight: '600', backgroundColor: '#fff3e0', padding: '2px 8px', borderRadius: '4px', marginTop: '4px', display: 'inline-block' }}>
                            Sinyal Lemah - Mode Offline
                        </span>
                    )}
                </div>
                <p style={{ fontSize: '11px', color: '#666', margin: 0, textAlign: 'right' }}>
                    Data: {lastUpdate || '...'}<br />
                    {isOffline ? '(Data Disimpan)' : '(Terbaru)'}
                </p>
            </div>

            {loading && prices.length === 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '40px 0', color: '#666' }}>
                    <Loader2 className="animate-spin" size={32} />
                    <p style={{ marginTop: '12px' }}>Memuat harga...</p>
                </div>
            ) : error && prices.length === 0 ? (
                <div style={{ padding: '20px', backgroundColor: '#ffebee', borderRadius: '12px', color: '#c62828', display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <AlertCircle size={24} />
                    <p style={{ fontSize: '14px', margin: 0 }}>{error}</p>
                </div>
            ) : (
                <>
                    {prices.map((item) => (
                        <PriceItem
                            key={item.id}
                            name={item.name}
                            price={item.today}
                            trend={item.gap_change}
                            unit={item.satuan.split('./')[1] || 'kg'}
                            history={historyData[item.name] || []}
                        />
                    ))}
                    <button className="btn-primary mt-2" onClick={() => window.open('https://panelharga.badanpangan.go.id/', '_blank')}>
                        Lihat Semua Harga
                        <ArrowRight size={24} />
                    </button>
                    <p style={{ textAlign: 'center', fontSize: '12px', color: '#888', marginTop: '12px' }}>
                        {isOffline
                            ? 'Menampilkan data terakhir yang disimpan'
                            : 'Ketuk kartu harga untuk tren 5 hari'}
                    </p>
                </>
            )}
        </div>
    );
};

export default PriceMonitor;
