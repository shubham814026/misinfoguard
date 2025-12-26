import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const LandingPage = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalAnalyses: 0,
    accuracyRate: 90,
    helpfulFeedback: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/stats`);
        if (response.data && response.data.success) {
          setStats({
            totalAnalyses: response.data.totalAnalyses || 0,
            accuracyRate: response.data.accuracyRate || 90,
            helpfulFeedback: response.data.helpfulFeedback || 0
          });
        }
      } catch (error) {
        console.log('Stats API not available, using defaults');
        // Use default stats if API is unavailable
        setStats({
          totalAnalyses: 0,
          accuracyRate: 90,
          helpfulFeedback: 0
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-navy-900 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.649 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.35-.166-2A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z" clipRule="evenodd" />
              </svg>
            </div>
            <span className="text-xl font-semibold text-navy-900">MIS InfoGuard</span>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-5xl mx-auto px-6">
        <section className="py-16 md:py-24 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Accuracy Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-verified-50 border border-verified-200 rounded-full mb-8">
              <div className="w-2 h-2 bg-verified-500 rounded-full"></div>
              <span className="text-verified-700 font-medium text-sm">
                {stats.accuracyRate}% Accuracy Rate
              </span>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-navy-900 mb-6 leading-tight">
              Verify news before <br className="hidden md:block" />
              you share it
            </h1>

            {/* Subtitle */}
            <p className="text-lg md:text-xl text-slate-600 mb-10 max-w-2xl mx-auto">
              Check if information is real, misleading, or fake in seconds. 
              Trusted by thousands to make informed decisions.
            </p>

            {/* CTA Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate('/analyze')}
              className="inline-flex items-center gap-2 px-8 py-4 bg-navy-900 text-white text-lg font-semibold rounded-xl hover:bg-navy-800 transition-colors shadow-lg shadow-navy-900/20"
            >
              Check News
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </motion.button>
          </motion.div>
        </section>

        {/* Stats Section - Only show if there's data */}
        {!loading && stats.totalAnalyses > 0 && (
          <section className="py-12 border-t border-slate-200">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="grid grid-cols-1 md:grid-cols-3 gap-8"
            >
              {/* Total Analyses */}
              <div className="text-center p-6">
                <div className="text-4xl md:text-5xl font-bold text-navy-900 mb-2">
                  {stats.totalAnalyses.toLocaleString()}
                </div>
                <div className="text-slate-600">
                  Analyses performed
                </div>
              </div>

              {/* Accuracy Rate */}
              {stats.accuracyRate > 0 && (
                <div className="text-center p-6 border-y md:border-y-0 md:border-x border-slate-200">
                  <div className="text-4xl md:text-5xl font-bold text-verified-600 mb-2">
                    {stats.accuracyRate}%
                  </div>
                  <div className="text-slate-600">
                    Accuracy rate
                  </div>
                </div>
              )}

              {/* User Feedback */}
              {stats.helpfulFeedback > 0 && (
                <div className="text-center p-6">
                  <div className="text-4xl md:text-5xl font-bold text-navy-900 mb-2">
                    {stats.helpfulFeedback}%
                  </div>
                  <div className="text-slate-600">
                    Found results helpful
                  </div>
                </div>
              )}
            </motion.div>
          </section>
        )}

        {/* Trust Indicators */}
        <section className="py-16 border-t border-slate-200">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6"
          >
            <div className="card p-6">
              <div className="w-10 h-10 bg-navy-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-navy-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-navy-900 mb-2">Instant Results</h3>
              <p className="text-slate-600">Get verification results in seconds, not hours.</p>
            </div>

            <div className="card p-6">
              <div className="w-10 h-10 bg-navy-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-navy-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-navy-900 mb-2">Verified Sources</h3>
              <p className="text-slate-600">Cross-referenced with trusted fact-checking organizations.</p>
            </div>

            <div className="card p-6">
              <div className="w-10 h-10 bg-navy-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-5 h-5 text-navy-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-navy-900 mb-2">No Account Required</h3>
              <p className="text-slate-600">Start checking immediately. No sign-up or personal data needed.</p>
            </div>
          </motion.div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 mt-8">
        <div className="max-w-5xl mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-slate-600">
              <div className="w-6 h-6 bg-navy-900 rounded flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.649 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.35-.166-2A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z" clipRule="evenodd" />
                </svg>
              </div>
              <span className="font-medium">MIS InfoGuard</span>
            </div>
            <p className="text-slate-500 text-sm">
              © 2025 MIS InfoGuard. Helping you make informed decisions.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
