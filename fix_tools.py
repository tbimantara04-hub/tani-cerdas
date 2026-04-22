import json
path = 'backend/evaluation_dataset.json'
with open(path, encoding='utf-8') as f:
    d = json.load(f)

for item in d:
    cat = item.get('category', '')
    q = item['query'].lower()
    tools = []
    
    if cat == 'Cuaca': tools = ['cek_cuaca']
    elif cat == 'Harga Pasar': 
        tools = ['cek_harga_pangan']
        if 'pupuk' in q: tools.append('cek_harga_pupuk')
    elif cat == 'Penyakit & Hama': tools = ['tanya_panduan_hama']
    elif cat == 'Profil Petani': tools = ['simpan_profil_petani']
    elif cat == 'Kombinasi':
        if any(k in q for k in ['cuaca', 'hujan', 'panas', 'iklim', 'kemarau', 'besok', 'hari ini']): tools.append('cek_cuaca')
        if any(k in q for k in ['harga', 'pasar', 'jual', 'komoditas']): tools.append('cek_harga_pangan')
        if any(k in q for k in ['pupuk']): tools.append('cek_harga_pupuk')
        if any(k in q for k in ['hama', 'penyakit', 'ulat', 'jamur', 'obat', 'keriting', 'layu', 'kuning']): tools.append('tanya_panduan_hama')
        if any(k in q for k in ['simpan', 'profil']): tools.append('simpan_profil_petani')
        if not tools: tools = ['cek_cuaca', 'cek_harga_pangan'] # Fallback
        
    item['expected_tools'] = tools

with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print("Berhasil mengevaluasi expected_tools dengan lebih spesifik!")
