import React, { useState, useEffect } from 'react';
import { Sun, CloudRain, Wind, Thermometer, MapPin, Gauge, Cloud } from 'lucide-react';
import axios from 'axios';

const Weather = () => {
    const [current, setCurrent] = useState(null);
    const [forecast, setForecast] = useState([]);
    const [loading, setLoading] = useState(true);
    const API_KEY = import.meta.env.VITE_OPENWEATHER_API_KEY || "";

    useEffect(() => {
        const fetchData = async (lat, lon, cityName) => {
            try {
                let currentUrl = `https://api.openweathermap.org/data/2.5/weather?q=${cityName}&appid=${API_KEY}&units=metric&lang=id`;
                let forecastUrl = `https://api.openweathermap.org/data/2.5/forecast?q=${cityName}&appid=${API_KEY}&units=metric&lang=id`;
                
                if (lat && lon) {
                    currentUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${API_KEY}&units=metric&lang=id`;
                    forecastUrl = `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&appid=${API_KEY}&units=metric&lang=id`;
                }

                // Fetch Current Weather
                const currentRes = await axios.get(currentUrl);
                setCurrent(currentRes.data);

                // Fetch 5-day Forecast
                const forecastRes = await axios.get(forecastUrl);

                // Process forecast data to get one entry per day (noon)
                const dailyData = forecastRes.data.list.filter(item => item.dt_txt.includes("12:00:00"));
                setForecast(dailyData);

            } catch (error) {
                console.error("Error fetching weather data:", error);
                // Fallback for demo
                setCurrent({
                    main: { temp: 28, pressure: 1012 },
                    weather: [{ description: "Cerah Berawan", main: "Clouds" }],
                    name: cityName || "Lokasi Anda"
                });
                setForecast([
                    { dt_txt: "Besok", main: { temp: 29 }, weather: [{ main: "Sun" }] },
                    { dt_txt: "Lusa", main: { temp: 27 }, weather: [{ main: "Rain" }] }
                ]);
            } finally {
                setLoading(false);
            }
        };

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    fetchData(position.coords.latitude, position.coords.longitude, null);
                },
                (error) => {
                    console.warn("Geolocation permission denied or error. Falling back to default.");
                    fetchData(null, null, "Jakarta"); // Fallback
                }
            );
        } else {
            fetchData(null, null, "Jakarta");
        }
    }, []);

    const getWeatherIcon = (main, size = 32) => {
        switch (main) {
            case 'Rain': return <CloudRain size={size} color="#2196F3" />;
            case 'Clear': return <Sun size={size} color="#F4B41A" />;
            case 'Clouds': return <Cloud size={size} color="#78909C" />;
            default: return <Sun size={size} color="#F4B41A" />;
        }
    };

    const getDayName = (dateStr) => {
        const days = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
        const d = new Date(dateStr);
        return days[d.getDay()];
    };

    if (loading) return <div className="text-center">Memuat...</div>;

    return (
        <div>
            {/* Current Weather Card */}
            <div className="card text-center" style={{ backgroundColor: '#2D5A27', color: 'white', padding: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '10px', flexWrap: 'wrap' }}>
                    <MapPin size={20} />
                    <span style={{ fontWeight: '600', fontSize: '16px' }}>{current.name}</span>
                </div>
                <div className="mb-2">
                    {getWeatherIcon(current.weather[0].main, 80)}
                </div>
                <h2 style={{ fontSize: 'clamp(32px, 8vw, 56px)', color: 'white', margin: '10px 0' }}>{Math.round(current.main.temp)}°C</h2>
                <p style={{ fontSize: 'clamp(16px, 4vw, 24px)', textTransform: 'capitalize', margin: '8px 0' }}>{current.weather[0].description}</p>
            </div>

            {/* Info Grid */}
            <div className="grid-2" style={{ marginBottom: '20px' }}>
                <div className="card text-center" style={{ marginBottom: 0 }}>
                    <Thermometer className="mb-2" size={32} color="#2D5A27" style={{ margin: '0 auto' }} />
                    <p style={{ fontSize: 'clamp(12px, 3vw, 14px)', color: '#666' }}>Suhu</p>
                    <p style={{ fontWeight: '700', fontSize: 'clamp(18px, 5vw, 24px)' }}>{Math.round(current.main.temp)}°C</p>
                </div>
                <div className="card text-center" style={{ marginBottom: 0 }}>
                    <Gauge className="mb-2" size={32} color="#2D5A27" style={{ margin: '0 auto' }} />
                    <p style={{ fontSize: 'clamp(12px, 3vw, 14px)', color: '#666' }}>Tekanan</p>
                    <p style={{ fontWeight: '700', fontSize: 'clamp(18px, 5vw, 24px)' }}>{current.main.pressure}</p>
                </div>
            </div>

            {/* Forecast Section */}
            <h2 className="mb-4" style={{ fontSize: 'clamp(20px, 6vw, 28px)' }}>Ramalan 5 Hari</h2>
            <div className="card" style={{ padding: '12px' }}>
                {forecast.map((day, index) => (
                    <div key={index} style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '10px 0',
                        borderBottom: index === forecast.length - 1 ? 'none' : '1px solid #eee',
                        fontSize: 'clamp(12px, 3vw, 16px)'
                    }}>
                        <div style={{ flex: '1', fontWeight: '600' }}>
                            {index === 0 ? "Hari ini" : getDayName(day.dt_txt)}
                        </div>
                        <div style={{ flex: '0 0 auto', display: 'flex', justifyContent: 'center' }}>
                            {getWeatherIcon(day.weather[0].main, 24)}
                        </div>
                        <div style={{ flex: '0 0 60px', textAlign: 'right', fontWeight: '700' }}>
                            {Math.round(day.main.temp)}°C
                        </div>
                    </div>
                ))}
            </div>

            <div className="card" style={{ borderLeft: '8px solid #F4B41A', marginTop: '20px' }}>
                <p style={{ fontWeight: '700', fontSize: 'clamp(14px, 3vw, 16px)' }}>Saran Tani:</p>
                <p style={{ fontSize: 'clamp(12px, 3vw, 14px)' }}>Cuaca {current.weather[0].main === 'Rain' ? 'Hujan' : 'Cerah'}. {current.weather[0].main === 'Rain' ? 'Pastikan saluran air lancar.' : 'Waktu yang baik untuk menyiram tanaman.'}</p>
            </div>
        </div>
    );
};

export default Weather;
