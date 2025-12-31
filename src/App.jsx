import React, { useState } from 'react';
import { Cloud, BookOpen, Scale as Tag, Menu, Home } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Weather from './components/Weather';
import Info from './components/Info';
import PriceMonitor from './components/PriceMonitor';

function App() {
  const [activeTab, setActiveTab] = useState('cuaca');

  const renderContent = () => {
    switch (activeTab) {
      case 'cuaca':
        return <Weather />;
      case 'info':
        return <Info />;
      case 'harga':
        return <PriceMonitor />;
      default:
        return <Weather />;
    }
  };

  return (
    <div className="app-container">
      <header className="container" style={{ paddingBottom: '10px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ fontSize: '28px' }}>Tani Cerdas</h1>
          <Menu size={28} color="#2D5A27" />
        </div>
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
      </main>

      <nav className="bottom-nav">
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
      </nav>
    </div>
  );
}

export default App;
