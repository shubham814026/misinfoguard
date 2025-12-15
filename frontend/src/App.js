import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import LandingPage from './pages/LandingPage';
import AnalyzePage from './pages/AnalyzePage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-crypto-950 via-brown-900 to-crypto-900">
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#3a1d15',
              color: '#f3d9c0',
              border: '1px solid #c06d3f',
            },
            success: {
              iconTheme: {
                primary: '#d4864b',
                secondary: '#f3d9c0',
              },
            },
            error: {
              iconTheme: {
                primary: '#dc2626',
                secondary: '#f3d9c0',
              },
            },
          }}
        />
        
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/analyze" element={<AnalyzePage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
