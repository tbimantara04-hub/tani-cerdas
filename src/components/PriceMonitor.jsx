import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, ArrowRight, Loader2, AlertCircle, Calendar, Sprout, ShoppingCart } from 'lucide-react';
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

const PriceItem = ({ name, price, trend, unit, history, isFertilizer }) => {
    const [showHistory, setShowHistory] = useState(false);

    // Disable history toggle for fertilizer since data is static HET
    const handleClick = () => {
        if (!isFertilizer) {
            setShowHistory(!showHistory);
        }
    };

    return (
        <div className="card" style={{ marginBottom: '12px', cursor: isFertilizer ? 'default' : 'pointer' }} onClick={handleClick}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <p style={{ fontSize: '14px', color: '#666', margin: 0 }}>{name}</p>
                    <h3 style={{ fontSize: '20px', margin: '4px 0' }}>Rp {price.toLocaleString()} <span style={{ fontSize: '14px', fontWeight: '400' }}>/{unit}</span></h3>
                </div>
                {!isFertilizer && (
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
                )}
                {isFertilizer && (
                    <div style={{ textAlign: 'right' }}>
                        <div style={{ color: '#2D5A27', fontSize: '14px', fontWeight: '600', backgroundColor: '#e8f5e9', padding: '4px 8px', borderRadius: '6px' }}>
                            Subsidi
                        </div>
                    </div>
                )}
            </div>
            {showHistory && !isFertilizer && <PriceHistory history={history} />}
        </div>
    );
};

const PriceMonitor = ({ activeSubTab = 'pangan', onSubTabChange }) => {
    const [internalTab, setInternalTab] = useState('pangan');
    const currentTab = onSubTabChange ? activeSubTab : internalTab;
    const handleTabChange = (tab) => {
        if (onSubTabChange) {
            onSubTabChange(tab);
        } else {
            setInternalTab(tab);
        }
    };
    const [prices, setPrices] = useState([]);
    const [historyData, setHistoryData] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState('');
    const [isOffline, setIsOffline] = useState(!navigator.onLine);

    // Depend on currentTab for any effects if needed, though data fetching is unified currently.

    // Static data for Fertilizer Prices (HET)
    const fertilizerPrices = [
        { id: 'f1', name: 'Pupuk Urea', today: 1800, satuan: 'kg' },
        { id: 'f2', name: 'Pupuk NPK', today: 1840, satuan: 'kg' },
        { id: 'f3', name: 'Pupuk NPK (Kakao)', today: 2640, satuan: 'kg' },
        { id: 'f4', name: 'Pupuk ZA', today: 1360, satuan: 'kg' },
        { id: 'f5', name: 'Pupuk Organik', today: 640, satuan: 'kg' },
    ];

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
                            timeout: 15000 // Increased timeout for slow government API
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
                        // Save last error code if all fail
                        if (!latestUpdateStr) latestUpdateStr = `Err: ${e.message}`;
                    }
                });

                await Promise.all(promises);

                // Update state and cache if we got new data
                if (latestPrices.length > 0) {
                    setPrices(latestPrices);
                    setHistoryData(historyTemp);
                    if (latestUpdateStr && !latestUpdateStr.startsWith('Err:')) setLastUpdate(latestUpdateStr);

                    localStorage.setItem('prices', JSON.stringify(latestPrices));
                    localStorage.setItem('historyData', JSON.stringify(historyTemp));
                    if (latestUpdateStr && !latestUpdateStr.startsWith('Err:')) localStorage.setItem('lastUpdate', latestUpdateStr);
                    setError(null);
                } else if (!cachedPrices) {
                    // Only error if we have no cache and no new data
                    const errorDetail = latestUpdateStr.startsWith('Err:') ? latestUpdateStr : 'Data tidak tersedia';
                    if (errorDetail.includes('500')) {
                        setError(`Server BAPANAS sedang mengalami gangguan (Err 500). Mohon coba lagi nanti.`);
                    } else {
                        setError(`Gagal memuat harga pasar (${errorDetail}). Pastikan koneksi internet stabil atau cek konfigurasi netlify.toml.`);
                    }
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
            </div>

            {/* Tab Toggle */}
            <div style={{
                display: 'flex',
                backgroundColor: '#f1f1f1',
                padding: '4px',
                borderRadius: '12px',
                marginBottom: '20px'
            }}>
                <button
                    onClick={() => handleTabChange('pangan')}
                    style={{
                        flex: 1,
                        padding: '10px',
                        border: 'none',
                        borderRadius: '10px',
                        backgroundColor: currentTab === 'pangan' ? 'white' : 'transparent',
                        color: currentTab === 'pangan' ? '#2D5A27' : '#666',
                        fontWeight: currentTab === 'pangan' ? '700' : '500',
                        boxShadow: currentTab === 'pangan' ? '0 2px 4px rgba(0,0,0,0.1)' : 'none',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '6px',
                        transition: 'all 0.2s'
                    }}
                >
                    <ShoppingCart size={18} />
                    Pangan
                </button>
                <button
                    onClick={() => handleTabChange('pupuk')}
                    style={{
                        flex: 1,
                        padding: '10px',
                        border: 'none',
                        borderRadius: '10px',
                        backgroundColor: currentTab === 'pupuk' ? 'white' : 'transparent',
                        color: currentTab === 'pupuk' ? '#2D5A27' : '#666',
                        fontWeight: currentTab === 'pupuk' ? '700' : '500',
                        boxShadow: currentTab === 'pupuk' ? '0 2px 4px rgba(0,0,0,0.1)' : 'none',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '6px',
                        transition: 'all 0.2s'
                    }}
                >
                    <Sprout size={18} />
                    Pupuk
                </button>
            </div>

            {currentTab === 'pangan' ? (
                /* Food Prices Content */
                <>
                    <p style={{ fontSize: '11px', color: '#666', margin: '0 0 12px 0', textAlign: 'right' }}>
                        Data: {lastUpdate || '...'}<br />
                        {isOffline ? '(Data Disimpan)' : '(Terbaru)'}
                    </p>

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
                                    isFertilizer={false}
                                />
                            ))}
                            <button className="btn-primary mt-2" onClick={() => window.open('https://panelharga.badanpangan.go.id/', '_blank')}>
                                Lihat Semua Harga
                                <ArrowRight size={24} />
                            </button>
                            <p style={{ textAlign: 'center', fontSize: '12px', color: '#888', marginTop: '12px' }}>
                                Sumber: Badan Pangan Nasional
                            </p>
                        </>
                    )}
                </>
            ) : (
                /* Fertilizer Prices Content */
                <>
                    <p style={{ fontSize: '11px', color: '#666', margin: '0 0 12px 0', textAlign: 'right' }}>
                        Harga Eceran Tertinggi (HET)<br />
                        Data Terbaru 2026
                    </p>

                    <div style={{ backgroundColor: '#e8f5e9', padding: '12px', borderRadius: '12px', marginBottom: '16px', display: 'flex', alignItems: 'start', gap: '10px' }}>
                        <AlertCircle size={20} color="#2e7d32" />
                        <p style={{ fontSize: '12px', color: '#1b5e20', margin: 0, lineHeight: '1.5' }}>
                            Harga di bawah adalah <strong>Harga Eceran Tertinggi (HET)</strong> resmi untuk pupuk bersubsidi. Harga di tingkat pengecer resmi tidak boleh melebihi angka ini.
                        </p>
                    </div>

                    {fertilizerPrices.map((item) => (
                        <PriceItem
                            key={item.id}
                            name={item.name}
                            price={item.today}
                            trend="stable"
                            unit={item.satuan}
                            history={[]}
                            isFertilizer={true}
                        />
                    ))}

                    <p style={{ textAlign: 'center', fontSize: '12px', color: '#888', marginTop: '12px' }}>
                        Sumber: Cyber Extension Kementerian Pertanian
                    </p>
                </>
            )}
        </div>
    );
};

export default PriceMonitor;
