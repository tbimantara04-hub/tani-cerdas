import React, { useState } from 'react';
import { Sprout, Shovel, Timer, PackageCheck, ChevronRight, X, Wheat, Flame, Leaf } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Data untuk jenis-jenis tanaman pada Pilih Bibit
const plantTypes = [
    {
        id: 'padi',
        name: 'Padi',
        icon: Wheat,
        emoji: '🌾',
        color: '#8B7355',
        details: {
            title: 'Pemilihan Bibit Padi',
            tips: [
                'Pilih benih bersertifikat (label biru untuk benih sebar atau ungu untuk benih inti)',
                'Pastikan benih bernas (berisi penuh), tidak keriput, dan bersih dari kotoran',
                'Lakukan uji apung: rendam benih dalam air garam, pilih yang tenggelam',
                'Perhatikan tanggal kedaluwarsa dan masa penyimpanan benih',
                'Gunakan varietas unggul sesuai musim dan ketinggian lahan'
            ]
        }
    },
    {
        id: 'jagung',
        name: 'Jagung',
        icon: Sprout,
        emoji: '🌽',
        color: '#FFA500',
        details: {
            title: 'Pemilihan Bibit Jagung',
            tips: [
                'Pilih benih hibrida atau komposit bersertifikat',
                'Pastikan biji berukuran seragam, mengkilap, dan tidak keriput',
                'Periksa daya kecambah minimal 90%',
                'Simpan benih di tempat sejuk dan kering',
                'Gunakan varietas tahan wereng dan penyakit bulai'
            ]
        }
    },
    {
        id: 'cabai',
        name: 'Cabai',
        icon: Flame,
        emoji: '🌶️',
        color: '#DC2626',
        details: {
            title: 'Pemilihan Bibit Cabai',
            tips: [
                'Pilih biji dari buah yang tua, matang sempurna, dan sehat',
                'Keringkan biji hingga kadar air sekitar 8-10%',
                'Pilih varietas sesuai permintaan pasar (cabai merah/rawit)',
                'Semai benih di polybag kecil atau tray semai',
                'Rendam benih dengan air hangat (50°C) selama 3-4 jam sebelum semai'
            ]
        }
    },
    {
        id: 'bawang',
        name: 'Bawang',
        icon: Leaf,
        emoji: '🧅',
        color: '#9333EA',
        details: {
            title: 'Pemilihan Bibit Bawang',
            tips: [
                'Gunakan umbi yang sudah disimpan 2-3 bulan (dorman)',
                'Pilih umbi yang sehat, padat, tidak busuk atau berlubang',
                'Ukuran umbi sebaiknya seragam (diameter 1.5-2.5 cm)',
                'Tunas sudah mulai muncul sedikit (tanda siap tanam)',
                'Untuk bawang daun, bisa juga menggunakan biji'
            ]
        }
    }
];

const infoData = [
    {
        id: 1,
        icon: Sprout,
        title: "Pilih Bibit",
        desc: "Cara memilih bibit unggul dan sehat.",
        color: "#2D5A27",
        hasSubCategories: true,
        plantTypes: plantTypes
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

// Component untuk card jenis tanaman
const PlantTypeCard = ({ plant, onClick }) => {
    const Icon = plant.icon;
    return (
        <div
            className="card"
            style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                cursor: 'pointer',
                marginBottom: '12px',
                padding: '16px',
                transition: 'transform 0.2s, box-shadow 0.2s'
            }}
            onClick={() => onClick(plant)}
            onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,0,0,0.1)';
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '';
            }}
        >
            <div style={{
                backgroundColor: plant.color,
                padding: '12px',
                borderRadius: '16px',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                minWidth: '56px',
                minHeight: '56px'
            }}>
                <Icon size={28} />
            </div>
            <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '18px', marginBottom: '2px', fontWeight: '600' }}>
                    {plant.emoji} {plant.name}
                </h3>
                <p style={{ fontSize: '13px', color: '#666' }}>
                    Tips memilih bibit {plant.name.toLowerCase()}
                </p>
            </div>
            <ChevronRight size={20} color="#ccc" />
        </div>
    );
};

// Component untuk detail jenis tanaman
const PlantTypeDetail = ({ plant, onClose, onBack }) => {
    if (!plant) return null;
    const Icon = plant.icon;

    return (
        <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'white',
                zIndex: 52,
                padding: '24px',
                overflowY: 'auto'
            }}
        >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <button onClick={onBack} style={{ background: 'none', border: 'none', padding: 0 }}>
                    <X size={28} color="#333" />
                </button>
                <h3 style={{ fontSize: '18px', fontWeight: 'bold' }}>{plant.details.title}</h3>
                <div style={{ width: '28px' }}></div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '32px' }}>
                <div style={{
                    backgroundColor: plant.color,
                    padding: '24px',
                    borderRadius: '50%',
                    color: 'white',
                    marginBottom: '16px',
                    boxShadow: '0 8px 24px rgba(0,0,0,0.15)'
                }}>
                    <Icon size={48} />
                </div>
                <div style={{ fontSize: '48px', marginBottom: '8px' }}>{plant.emoji}</div>
                <h2 style={{ fontSize: '28px', color: '#333', margin: 0 }}>{plant.name}</h2>
            </div>

            <div style={{
                backgroundColor: '#F9FAFB',
                padding: '20px',
                borderRadius: '16px',
                marginBottom: '16px'
            }}>
                <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: '#333' }}>
                    Tips Memilih Bibit:
                </h4>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                    {plant.details.tips.map((tip, index) => (
                        <li key={index} style={{
                            fontSize: '14px',
                            lineHeight: '1.6',
                            color: '#555',
                            marginBottom: '12px',
                            paddingLeft: '24px',
                            position: 'relative'
                        }}>
                            <span style={{
                                position: 'absolute',
                                left: 0,
                                top: 0,
                                color: plant.color,
                                fontWeight: 'bold'
                            }}>✓</span>
                            {tip}
                        </li>
                    ))}
                </ul>
            </div>
        </motion.div>
    );
};

// Component untuk menampilkan daftar jenis tanaman
const PlantTypeList = ({ onClose, onSelectPlant }) => {
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
                zIndex: 51,
                padding: '24px',
                overflowY: 'auto'
            }}
        >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <button onClick={onClose} style={{ background: 'none', border: 'none', padding: 0 }}>
                    <X size={28} color="#333" />
                </button>
                <h3 style={{ fontSize: '18px', fontWeight: 'bold' }}>Pilih Jenis Tanaman</h3>
                <div style={{ width: '28px' }}></div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '24px' }}>
                <div style={{
                    backgroundColor: '#2D5A27',
                    padding: '20px',
                    borderRadius: '50%',
                    color: 'white',
                    marginBottom: '16px',
                    boxShadow: '0 6px 16px rgba(45,90,39,0.3)'
                }}>
                    <Sprout size={40} />
                </div>
                <h2 style={{ fontSize: '24px', color: '#333', marginBottom: '8px' }}>Pilih Bibit Unggul</h2>
                <p style={{ fontSize: '14px', color: '#666', textAlign: 'center' }}>
                    Pilih jenis tanaman untuk melihat tips pemilihan bibit
                </p>
            </div>

            <div>
                {plantTypes.map((plant) => (
                    <PlantTypeCard key={plant.id} plant={plant} onClick={onSelectPlant} />
                ))}
            </div>
        </motion.div>
    );
};

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
    const [showPlantTypes, setShowPlantTypes] = useState(false);
    const [selectedPlant, setSelectedPlant] = useState(null);

    const handleCardClick = (item) => {
        if (item.hasSubCategories) {
            setShowPlantTypes(true);
        } else {
            setSelectedItem(item);
        }
    };

    const handleClosePlantTypes = () => {
        setShowPlantTypes(false);
    };

    const handleSelectPlant = (plant) => {
        setSelectedPlant(plant);
    };

    const handleClosePlantDetail = () => {
        setSelectedPlant(null);
        setShowPlantTypes(false);
    };

    return (
        <div>
            <h2 className="mb-4">Panduan Tani</h2>

            {infoData.map((item) => (
                <InfoCard key={item.id} item={item} onClick={handleCardClick} />
            ))}

            <AnimatePresence>
                {selectedItem && (
                    <InfoDetail item={selectedItem} onClose={() => setSelectedItem(null)} />
                )}
            </AnimatePresence>

            <AnimatePresence>
                {showPlantTypes && !selectedPlant && (
                    <PlantTypeList onClose={handleClosePlantTypes} onSelectPlant={handleSelectPlant} />
                )}
            </AnimatePresence>

            <AnimatePresence>
                {selectedPlant && (
                    <PlantTypeDetail
                        plant={selectedPlant}
                        onClose={handleClosePlantDetail}
                        onBack={() => setSelectedPlant(null)}
                    />
                )}
            </AnimatePresence>
        </div>
    );
};

export default Info;
