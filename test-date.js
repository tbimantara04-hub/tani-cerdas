
import axios from 'axios';

async function testDateParam() {
    try {
        const dates = ['2025-12-25', '2025-12-26'];
        for (const date of dates) {
            const url = `https://api-panelhargav2.badanpangan.go.id/api/front/harga-pangan-informasi?province_id=&city_id=&level_harga_id=3&date=${date}`;
            console.log(`Testing Date: ${date}`);

            const response = await axios.get(url, {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json',
                    'Origin': 'https://panelharga.badanpangan.go.id',
                    'Referer': 'https://panelharga.badanpangan.go.id/'
                }
            });

            console.log(`Status ${date}:`, response.status);
            console.log(`Data Status ${date}:`, response.data.status);
            if (response.data.data && response.data.data.length > 0) {
                console.log(`First item ${date}:`, response.data.data[0].name, response.data.data[0].today);
            }
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
}

testDateParam();
