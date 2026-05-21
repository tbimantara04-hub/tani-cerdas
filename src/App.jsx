import React, { useState, useEffect } from 'react';
import { Cloud, BookOpen, Scale as Tag, Menu, Home, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Weather from './components/Weather';
import Info from './components/Info';
import PriceMonitor from './components/PriceMonitor';
import VoiceAssistant from './components/VoiceAssistant';
import Chatbot from './components/Chatbot';
import FarmerProfile from './components/FarmerProfile';
import { User } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('cuaca');
  const [priceSubTab, setPriceSubTab] = useState('pangan');
  const [infoCategory, setInfoCategory] = useState(null);
  const [selectedPlant, setSelectedPlant] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 768);

  useEffect(() => {
    const handleResize = () => {
      setIsDesktop(window.innerWidth >= 768);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'cuaca':
        return <Weather />;
      case 'info':
        return (
          <Info
            activeCategory={infoCategory}
            onCategoryChange={setInfoCategory}
            activePlant={selectedPlant}
            onPlantChange={setSelectedPlant}
          />
        );
      case 'harga':
        return <PriceMonitor activeSubTab={priceSubTab} onSubTabChange={setPriceSubTab} />;
      case 'profil':
        return <FarmerProfile />;
      default:
        return <Weather />;
    }
  };

  return (
    <div className="app-container">
      <nav className={`app-nav ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <button
          className="sidebar-toggle"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          title={sidebarOpen ? 'Tutup sidebar' : 'Buka sidebar'}
        >
          {sidebarOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
        </button>
        
        <div
          className={`nav-item ${activeTab === 'cuaca' ? 'active' : ''}`}
          onClick={() => setActiveTab('cuaca')}
        >
          <Cloud className="icon-large" />
          <span>Cuaca</span>
        </div>
        <div
          className={`nav-item ${activeTab === 'info' ? 'active' : ''}`}
          onClick={() => setActiveTab('info')}
        >
          <BookOpen className="icon-large" />
          <span>Informasi</span>
        </div>
        <div
          className={`nav-item ${activeTab === 'harga' ? 'active' : ''}`}
          onClick={() => setActiveTab('harga')}
        >
          <Tag className="icon-large" />
          <span>Harga</span>
        </div>
        <div
          className={`nav-item ${activeTab === 'profil' ? 'active' : ''}`}
          onClick={() => setActiveTab('profil')}
        >
          <User className="icon-large" />
          <span>Profil</span>
        </div>
      </nav>

      <div className="main-content">
        <header className="container" style={{ paddingBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ fontSize: '28px', margin: 0 }}>Tani Cerdas</h1>
          {!isDesktop && <Menu size={28} color="#2D5A27" className="mobile-menu-icon" />}
        </header>

        <main className="container">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
            >
              {renderContent()}
            </motion.div>
          </AnimatePresence>

          <VoiceAssistant
            activeTab={activeTab}
            onNavigate={setActiveTab}
            onPriceTabChange={setPriceSubTab}
            onInfoCategoryChange={setInfoCategory}
            infoCategory={infoCategory}
            selectedPlant={selectedPlant}
          />
          <Chatbot />
        </main>
      </div>
    </div>
  );
}

export default App;
