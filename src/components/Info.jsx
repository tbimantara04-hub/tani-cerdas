import React from 'react';
import { Sprout, Shovel, Timer, PackageCheck, ChevronRight } from 'lucide-react';

const InfoCard = ({ icon: Icon, title, desc, color }) => (
    <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{
            backgroundColor: color,
            padding: '15px',
            borderRadius: '20px',
            color: 'white'
        }}>
            <Icon size={32} />
        </div>
        <div style={{ flex: 1 }}>
            <h3 style={{ fontSize: '20px', marginBottom: '4px' }}>{title}</h3>
            <p style={{ fontSize: '14px', color: '#666' }}>{desc}</p>
        </div>
        <ChevronRight size={24} color="#ccc" />
    </div>
);

const Info = () => {
    return (
        <div>
            <h2 className="mb-4">Panduan Tani</h2>

            <InfoCard
                icon={Sprout}
                title="Pilih Bibit"
                desc="Cara memilih bibit unggul dan sehat."
                color="#2D5A27"
            />

            <InfoCard
                icon={Shovel}
                title="Penanaman"
                desc="Langkah menanam agar cepat tumbuh."
                color="#2D5A27"
            />

            <InfoCard
                icon={Timer}
                title="Waktu Panen"
                desc="Tanda-tanda tanaman siap dipetik."
                color="#F4B41A"
            />

            <InfoCard
                icon={PackageCheck}
                title="Olahan Panen"
                desc="Menjaga hasil panen tetap segar."
                color="#F4B41A"
            />

        </div>
    );
};

export default Info;
