const axios = require('axios');
const fs = require('fs');
const path = require('path');

const API_BASE = "https://api-panelhargav2.badanpangan.go.id/api/front";

const formatToday = () => {
    const d = new Date();
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
};

async function fetchPrices() {
    console.log("Memulai pengambilan data harga dari Bapanas...");
    const today = formatToday();
    const period = `${today} - ${today}`;

    try {
        // 1. Get Commodities
        const comsRes = await axios.get(`${API_BASE}/komoditas`);
        const allComs = comsRes.data.data;

        // 2. Get National Averages (Level 3 = Consumer)
        const priceRes = await axios.get(`${API_BASE}/harga-rata-rata`, {
            params: {
                level_harga_id: 3,
                period_date: period
            }
        });

        const prices = priceRes.data.data;

        // Target list (approximate names based on typical Bapanas data)
        const targets = ["Beras", "Cabai", "Bawang", "Daging Ayam", "Telur Ayam"];

        const finalData = prices.filter(p => {
            return targets.some(t => p.name.toLowerCase().includes(t.toLowerCase()));
        }).map(p => ({
            id: p.komoditas_id,
            name: p.name,
            price: Math.round(parseFloat(p.harga)),
            unit: p.unit,
            trend: p.perubahan_harga >= 0 ? 'up' : 'down',
            change: p.perubahan_harga
        }));

        const outputPath = path.join(__dirname, '../src/data/prices.json');
        fs.writeFileSync(outputPath, JSON.stringify({
            updatedAt: new Date().toISOString(),
            data: finalData
        }, null, 2));

        console.log(`Berhasil memperbarui data harga! Tersimpan di: ${outputPath}`);
    } catch (error) {
        console.error("Gagal mengambil data harga:", error.message);
        // Save fallback mock data if real API fails during automation
        const outputPath = path.join(__dirname, '../src/data/prices.json');
        const fallback = {
            updatedAt: new Date().toISOString(),
            data: [
                { id: 1, name: "Beras Medium", price: 14500, unit: "kg", trend: "up" },
                { id: 2, name: "Cabai Merah", price: 42000, unit: "kg", trend: "down" },
                { id: 3, name: "Bawang Merah", price: 35000, unit: "kg", trend: "up" }
            ]
        };
        fs.writeFileSync(outputPath, JSON.stringify(fallback, null, 2));
    }
}

fetchPrices();
