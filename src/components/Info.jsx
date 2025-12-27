import React, { useState } from 'react';
import { Sprout, Shovel, Timer, PackageCheck, ChevronRight, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const infoData = [
    {
        id: 1,
        icon: Sprout,
        title: "Pilih Bibit",
        desc: "Cara memilih bibit unggul dan sehat.",
        color: "#2D5A27",
        details: (
            <div>
                <h4 className="font-bold mb-2">Beras & Jagung</h4>
                <p className="mb-2 text-sm text-gray-700">Pilih benih bersertifikat (label biru/ungu). Pastikan benih bersih, bernas (berisi), dan tidak keriput. Rendam benih; yang tenggelam adalah yang bagus.</p>
                <h4 className="font-bold mb-2">Cabai & Bawang</h4>
                <p className="text-sm text-gray-700">Untuk cabai, pilih dari buah yang tua, sehat, dan sempurna. Untuk bawang, gunakan umbi yang sudah disimpan 2-3 bulan, tidak busuk, dan tunasnya baru muncul.</p>
            </div>
        )
    },
    {
        id: 2,
        icon: Shovel,
        title: "Penanaman",
        desc: "Langkah menanam agar cepat tumbuh.",
        color: "#2D5A27",
        details: (
            <div>
                <h4 className="font-bold mb-2">Persiapan Lahan</h4>
                <p className="mb-2 text-sm text-gray-700">Gemburkan tanah dan beri pupuk kandang 1 minggu sebelum tanam. Pastikan sistem irigasi lancar.</p>
                <h4 className="font-bold mb-2">Jarak Tanam</h4>
                <ul className="list-disc pl-4 text-sm text-gray-700">
                    <li>Padi: Sistem jajar legowo (2:1 atau 4:1) untuk hasil lebih tinggi.</li>
                    <li>Jagung: 70cm x 20cm, 1 biji per lubang.</li>
                    <li>Cabai: 50cm x 60cm, gunakan mulsa plastik.</li>
                </ul>
            </div>
        )
    },
    {
        id: 3,
        icon: Timer,
        title: "Waktu Panen",
        desc: "Tanda-tanda tanaman siap dipetik.",
        color: "#F4B41A",
        details: (
            <div>
                <h4 className="font-bold mb-2">Ciri Siap Panen</h4>
                <ul className="list-disc pl-4 text-sm text-gray-700">
                    <li><strong>Padi:</strong> 95% butir sudah menguning, daun bendera mulai kering.</li>
                    <li><strong>Jagung:</strong> Kelobot kering/coklat, biji mengkilap dan keras bila ditekan kuku.</li>
                    <li><strong>Cabai:</strong> 60-80% warna merah merata (untuk cabai merah).</li>
                    <li><strong>Bawang:</strong> Leher batang lunak dan 60% daun menguning/rebah.</li>
                </ul>
            </div>
        )
    },
    {
        id: 4,
        icon: PackageCheck,
        title: "Olahan Panen",
        desc: "Menjaga hasil panen tetap segar.",
        color: "#F4B41A",
        details: (
            <div>
                <h4 className="font-bold mb-2">Pasca Panen</h4>
                <p className="mb-2 text-sm text-gray-700">Segera keringkan hasil panen (padi/jagung) hingga kadar air aman (14%). Simpan di tempat kering dan berventilasi.</p>
                <h4 className="font-bold mb-2">Tips Pemasaran</h4>
                <p className="text-sm text-gray-700">Bersihkan hasil panen dari kotoran sebelum dijual. Kelompokkan berdasarkan ukuran (grading) untuk harga jual yang lebih baik. Cek harga pasar di tab 'Harga' sebelum menjual.</p>
            </div>
        )
    }
];

const InfoCard = ({ item, onClick }) => {
    const Icon = item.icon;
    return (
        <div
            className="card"
            style={{ display: 'flex', alignItems: 'center', gap: '20px', cursor: 'pointer', marginBottom: '16px' }}
            onClick={() => onClick(item)}
        >
            <div style={{
                backgroundColor: item.color,
                padding: '15px',
                borderRadius: '20px',
                color: 'white'
            }}>
                <Icon size={32} />
            </div>
            <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '20px', marginBottom: '4px' }}>{item.title}</h3>
                <p style={{ fontSize: '14px', color: '#666' }}>{item.desc}</p>
            </div>
            <ChevronRight size={24} color="#ccc" />
        </div>
    );
};

const InfoDetail = ({ item, onClose }) => {
    if (!item) return null;
    const Icon = item.icon;

    return (
        <motion.div
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'white',
                zIndex: 50,
                padding: '24px',
                overflowY: 'auto'
            }}
        >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                <button onClick={onClose} style={{ background: 'none', border: 'none', padding: 0 }}>
                    <X size={28} color="#333" />
                </button>
                <h3 style={{ fontSize: '18px', fontWeight: 'bold' }}>Detail Informasi</h3>
                <div style={{ width: '28px' }}></div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '32px' }}>
                <div style={{
                    backgroundColor: item.color,
                    padding: '24px',
                    borderRadius: '50%',
                    color: 'white',
                    marginBottom: '16px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                }}>
                    <Icon size={48} />
                </div>
                <h2 style={{ fontSize: '28px', color: '#333', margin: 0 }}>{item.title}</h2>
            </div>

            <div style={{ fontSize: '16px', lineHeight: '1.6', color: '#444' }}>
                {item.details}
            </div>
        </motion.div>
    );
};

const Info = () => {
    const [selectedItem, setSelectedItem] = useState(null);

    return (
        <div>
            <h2 className="mb-4">Panduan Tani</h2>

            {infoData.map((item) => (
                <InfoCard key={item.id} item={item} onClick={setSelectedItem} />
            ))}

            <AnimatePresence>
                {selectedItem && (
                    <InfoDetail item={selectedItem} onClose={() => setSelectedItem(null)} />
                )}
            </AnimatePresence>
        </div>
    );
};

export default Info;
