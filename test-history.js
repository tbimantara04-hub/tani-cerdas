
import axios from 'axios';

async function testHistoryApi() {
    try {
        const url = 'https://api-panelhargav2.badanpangan.go.id/api/front/harga-pangan-bulanan-v2?start_year=2025&end_year=2025&period_date=22/12/2025 - 27/12/2025&province_id=&level_harga_id=3';
        const response = await axios.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Origin': 'https://panelharga.badanpangan.go.id',
                'Referer': 'https://panelharga.badanpangan.go.id/'
            }
        });

        if (response.data && response.data.data && response.data.data["2025"]) {
            const items = response.data.data["2025"];
            const RiceMedium = items.find(item => item.Komoditas === "Beras Medium");
            if (RiceMedium) {
                console.log('Beras Medium Des:', JSON.stringify(RiceMedium.Des, null, 2));
            }
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
}

testHistoryApi();
