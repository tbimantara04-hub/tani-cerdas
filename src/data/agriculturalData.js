import { Sprout, Shovel, Timer, PackageCheck, Wheat, Flame, Leaf, Bug } from 'lucide-react';

export const plantTypes = [
    {
        id: 'padi',
        name: 'Padi',
        icon: Wheat,
        emoji: '🌾',
        color: '#8B7355',
        data: {
            bibit: {
                title: 'Pemilihan Bibit Padi',
                tips: [
                    'Pilih benih bersertifikat (label biru atau ungu)',
                    'Pastikan benih bernas (isi penuh), tidak keriput',
                    'Uji apung: pilih benih yang tenggelam dalam air garam',
                    'Gunakan varietas unggul (Inpari, Ciherang, dll)',
                    'Perhatikan tanggal kedaluwarsa benih'
                ]
            },
            penanaman: {
                title: 'Cara Menanam Padi',
                tips: [
                    'Gunakan sistem Jajar Legowo (2:1 atau 4:1)',
                    'Umur bibit saat pindah tanam: 15-21 hari',
                    'Kedalaman tanam: 2-3 cm agar anakan banyak',
                    'Jumlah bibit: 1-3 batang per lubang tanam',
                    'Jaga genangan air macak-macak di awal tanam'
                ]
            },
            panen: {
                title: 'Waktu Panen Padi',
                tips: [
                    '95% butir gabah sudah menguning',
                    'Kadar air gabah berkisar 22-25%',
                    'Daun bendera sudah mulai mengering',
                    'Gunakan sabit tajam atau combine harvester',
                    'Segera lakukan perontokan setelah dipotong'
                ]
            },
            olahan: {
                title: 'Pasca Panen Padi',
                tips: [
                    'Keringkan gabah hingga kadar air 14% (GKG)',
                    'Bersihkan dari kotoran sebelum digiling',
                    'Simpan di tempat kering dan berventilasi',
                    'Gunakan kemasan karung yang bersih',
                    'Pantau suhu gudang agar tidak lembab'
                ]
            },
            opt: {
                title: 'Hama Penyakit Padi',
                tips: [
                    'Wereng Coklat: pantau populasi di pangkal batang',
                    'Tikus: lakukan gropyokan massal atau pagar plastik',
                    'Penggerek Batang: pasang lampu perangkap malam hari',
                    'Hawar Daun Bakteri: hindari pupuk N berlebih',
                    'Gunakan agensia hayati sebelum pestisida kimia'
                ]
            }
        }
    },
    {
        id: 'jagung',
        name: 'Jagung',
        icon: Sprout,
        emoji: '🌽',
        color: '#FFA500',
        data: {
            bibit: {
                title: 'Pemilihan Bibit Jagung',
                tips: [
                    'Pilih benih hibrida bersertifikat untuk hasil tinggi',
                    'Biji berukuran seragam dan tidak cacat',
                    'Daya kecambah minimal harus di atas 90%',
                    'Simpan benih di tempat sejuk hingga saat tanam',
                    'Pilih varietas tahan bulai (P35, Bisi 18, dll)'
                ]
            },
            penanaman: {
                title: 'Cara Menanam Jagung',
                tips: [
                    'Jarak tanam: 70cm x 20cm (1 biji/lubang)',
                    'Kedalaman tanam: 3-5 cm',
                    'Pastikan tanah lembab tapi tidak tergenang',
                    'Lakukan pemupukan dasar (Urea, SP36, KCl)',
                    'Tutup lubang tanam dengan tanah gembur/pupuk'
                ]
            },
            panen: {
                title: 'Waktu Panen Jagung',
                tips: [
                    'Kelobot sudah kering/berwarna coklat',
                    'Biji jagung keras dan mengkilap',
                    'Muncul lapisan hitam (black layer) di pangkal biji',
                    'Umur tanaman mencapai 105-115 hari (tergantung varietas)',
                    'Batang tanaman sudah mulai mengering'
                ]
            },
            olahan: {
                title: 'Pasca Panen Jagung',
                tips: [
                    'Kupas kelobot segera setelah dipanen',
                    'Jemur jagung tongkol hingga kadar air 17%',
                    'Pipil jagung menggunakan alat pemipil',
                    'Keringkan biji pipil hingga kadar air 14%',
                    'Simpan dalam silo atau karung di tempat kering'
                ]
            },
            opt: {
                title: 'Hama Penyakit Jagung',
                tips: [
                    'Ulat Grayak (FAW): cek pucuk daun secara rutin',
                    'Penyakit Bulai: gunakan benih dengan perlakuan fungisida',
                    'Ulat Tongkol: potong ujung tongkol yang terserang',
                    'Penyakit Karat Daun: atur drainase agar tidak lembab',
                    'Gunakan musuh alami seperti semut merah atau lebah parasit'
                ]
            }
        }
    },
    {
        id: 'cabai',
        name: 'Cabai',
        icon: Flame,
        emoji: '🌶️',
        color: '#DC2626',
        data: {
            bibit: {
                title: 'Pemilihan Bibit Cabai',
                tips: [
                    'Pilih biji dari buah yang tua dan sehat (tidak busuk)',
                    'Keringkan biji hingga kadar air 10%',
                    'Semai di media pot tray/polybag selama 25-30 hari',
                    'Pilih bibit yang tegak, sehat, dan berdaun 4-6',
                    'Lakukan sterilisasi media semai'
                ]
            },
            penanaman: {
                title: 'Cara Menanam Cabai',
                tips: [
                    'Jarak tanam: 60cm x 70cm dalam bedengan',
                    'Gunakan mulsa plastik hitam perak untuk kontrol gulma',
                    'Lakukan pindah tanam pada sore hari agar tidak layu',
                    'Siram bibit segera setelah ditanam',
                    'Pasang ajir (penyangga) sejak awal tanam'
                ]
            },
            panen: {
                title: 'Waktu Panen Cabai',
                tips: [
                    'Cabai sudah berwarna merah merata (atau sesuai kebutuhan)',
                    'Lakukan pemetikan beserta tangkainya',
                    'Waktu panen terbaik: Pagi hari (07.00 - 09.00)',
                    'Interval panen: 3-5 hari sekali',
                    'Pilih buah yang kencang dan mengkilap'
                ]
            },
            olahan: {
                title: 'Pasca Panen Cabai',
                tips: [
                    'Sortasi: pisahkan buah yang busuk/cacat',
                    'Hamparkan cabai di tempat teduh (jangan ditumpuk)',
                    'Gunakan kemasan peti kayu atau keranjang berventilasi',
                    'Jangan cuci cabai jika ingin disimpan lama',
                    'Simpan di suhu sejuk (5-10°C) jika memungkinkan'
                ]
            },
            opt: {
                title: 'Hama Penyakit Cabai',
                tips: [
                    'Antraknosa (Patek): buang buah yang terkena agar tidak menular',
                    'Thrips/Kutu Daun: gunakan perangkap kuning',
                    'Virus Kuning/Bule: cabut tanaman yang terinfeksi sejak dini',
                    'Ulat Tanah: lakukan sanitasi lahan secara rutin',
                    'Gunakan pestisida nabati sebagai langkah pencegahan'
                ]
            }
        }
    },
    {
        id: 'bawang',
        name: 'Bawang',
        icon: Leaf,
        emoji: '🧅',
        color: '#9333EA',
        data: {
            bibit: {
                title: 'Pemilihan Bibit Bawang',
                tips: [
                    'Gunakan umbi yang sudah disimpan 2-4 bulan',
                    'Umbi harus padat, sehat, dan warna kulit mengkilap',
                    'Titik tumbuh (tunas) sudah terlihat di ujung umbi',
                    'Potong sedikit ujung umbi (1/3 bagian) untuk percepat tumbuh',
                    'Ukuran umbi seragam (5-10 gram/umbi)'
                ]
            },
            penanaman: {
                title: 'Cara Menanam Bawang',
                tips: [
                    'Jarak tanam: 15cm x 15cm atau 20cm x 20cm',
                    'Benamkan umbi ke tanah hingga batas leher umbi',
                    'Pastikan drainase lahan sangat baik (garitan/bedengan)',
                    'Lakukan penyiraman pagi dan sore di awal tanam',
                    'Tanah harus gembur dan kaya bahan organik'
                ]
            },
            panen: {
                title: 'Waktu Panen Bawang',
                tips: [
                    '60-70% daun sudah mulai rebah/menguning',
                    'Umbi sudah terlihat besar dan menonjol ke permukaan',
                    'Leher batang sudah mulai lunak/lemas',
                    'Kuliit umbi sudah berwarna merah cerah',
                    'Panen saat cuaca cerah (lahan tidak becek)'
                ]
            },
            olahan: {
                title: 'Pasca Panen Bawang',
                tips: [
                    'Lakukan pengeringan (pelayuan) di bawah sinar matahari',
                    'Ikat bawang menjadi bendelan-bendelan kecil',
                    'Gantung bawang di rak penyimpanan (para-para)',
                    'Pastikan sirkulasi udara di gudang sangat baik',
                    'Pisahkan umbi untuk konsumsi dan untuk calon bibit'
                ]
            },
            opt: {
                title: 'Hama Penyakit Bawang',
                tips: [
                    'Ulat Bawang (Spodoptera): petik daun yang berisi telur/ulat',
                    'Penyakit Moler (Layu Fusarium): cabut dan bakar tanaman sakit',
                    'Penyakit Otot Ayam: perbaiki sirkulasi udara lahan',
                    'Gunakan perangkap lampu (light trap) untuk ngengat',
                    'Lakukan rotasi tanaman (jangan bawang terus menerus)'
                ]
            }
        }
    }
];

export const infoData = [
    {
        id: 1,
        icon: Sprout,
        title: "Pilih Bibit",
        desc: "Cara memilih bibit unggul dan sehat.",
        color: "#2D5A27",
        hasSubCategories: true,
        categoryKey: 'bibit'
    },
    {
        id: 2,
        icon: Shovel,
        title: "Penanaman",
        desc: "Langkah menanam agar cepat tumbuh.",
        color: "#2D5A27",
        hasSubCategories: true,
        categoryKey: 'penanaman'
    },
    {
        id: 3,
        icon: Timer,
        title: "Waktu Panen",
        desc: "Tanda-tanda tanaman siap dipetik.",
        color: "#F4B41A",
        hasSubCategories: true,
        categoryKey: 'panen'
    },
    {
        id: 4,
        icon: PackageCheck,
        title: "Olahan Panen",
        desc: "Menjaga hasil panen tetap segar.",
        color: "#F4B41A",
        hasSubCategories: true,
        categoryKey: 'olahan'
    },
    {
        id: 5,
        icon: Bug,
        title: "Pengendalian OPT",
        desc: "Upaya mengendalikan hama & penyakit.",
        color: "#DC2626",
        hasSubCategories: true,
        categoryKey: 'opt'
    }
];
