
import axios from 'axios';

async function testApi() {
  try {
    const url = 'https://api-panelhargav2.badanpangan.go.id/api/front/harga-pangan-informasi?province_id=&city_id=&level_harga_id=3';
    console.log(`Testing URL: ${url}`);
    
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Origin': 'https://panelharga.badanpangan.go.id',
        'Referer': 'https://panelharga.badanpangan.go.id/'
      }
    });
    
    console.log('Status:', response.status);
    console.log('Data Status:', response.data.status);
    console.log('Sample data count:', response.data.data ? response.data.data.length : 0);
  } catch (error) {
    console.error('Error fetching API:');
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', JSON.stringify(error.response.data));
    } else {
      console.error(error.message);
    }
  }
}

testApi();
