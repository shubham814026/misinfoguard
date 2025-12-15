import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { FaShieldAlt, FaSearch, FaBrain, FaCheckCircle } from 'react-icons/fa';
import { MdSecurity } from 'react-icons/md';
import { BiTargetLock } from 'react-icons/bi';

const LandingPage = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <FaSearch className="text-4xl" />,
      title: "Deep Web Scanning",
      description: "Scans the entire internet for fact-checking like Comet browser technology"
    },
    {
      icon: <FaBrain className="text-4xl" />,
      title: "Advanced AI Analysis",
      description: "OCR + NLP powered analysis with 90%+ accuracy guarantee"
    },
    {
      icon: <FaShieldAlt className="text-4xl" />,
      title: "Content Safety",
      description: "Automatically rejects inappropriate and sensitive content"
    },
    {
      icon: <BiTargetLock className="text-4xl" />,
      title: "Binary Verdict",
      description: "Clear results - no neutral answers, just truth or falsehood"
    },
    {
      icon: <FaCheckCircle className="text-4xl" />,
      title: "Trusted Sources",
      description: "Links to verified news sites and fact-checking organizations"
    },
    {
      icon: <MdSecurity className="text-4xl" />,
      title: "No Login Required",
      description: "Instant analysis without registration or personal data"
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden min-h-screen flex items-center justify-center px-4">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <motion.div
            className="absolute top-20 left-10 w-72 h-72 bg-crypto-600 rounded-full mix-blend-multiply filter blur-xl opacity-20"
            animate={{
              x: [0, 100, 0],
              y: [0, 50, 0],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <motion.div
            className="absolute bottom-20 right-10 w-96 h-96 bg-brown-600 rounded-full mix-blend-multiply filter blur-xl opacity-20"
            animate={{
              x: [0, -100, 0],
              y: [0, -50, 0],
            }}
            transition={{
              duration: 12,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        </div>

        <div className="relative z-10 max-w-6xl mx-auto text-center">
          {/* Logo/Icon */}
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ duration: 0.8, type: "spring" }}
            className="mb-8 inline-block"
          >
            <div className="p-6 bg-gradient-to-br from-crypto-600 to-brown-700 rounded-3xl shadow-2xl animate-glow">
              <FaShieldAlt className="text-7xl text-crypto-100" />
            </div>
          </motion.div>

          {/* Title */}
          <motion.h1
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-6xl md:text-8xl font-bold mb-6 text-gradient"
          >
            MisinfoGuard
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-xl md:text-2xl text-crypto-200 mb-4 max-w-3xl mx-auto"
          >
            Your AI-Powered Fake Information Detector
          </motion.p>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="text-lg text-crypto-300 mb-12 max-w-2xl mx-auto"
          >
            Upload images or paste text to verify facts instantly with 90%+ accuracy.
            Powered by advanced OCR, NLP, and real-time web fact-checking.
          </motion.p>

          {/* CTA Button */}
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/analyze')}
            className="px-12 py-5 bg-gradient-to-r from-crypto-600 to-brown-600 text-white text-xl font-bold rounded-full shadow-2xl hover:shadow-crypto-500/50 transition-all duration-300 hover-lift"
          >
            Start Analyzing Now
          </motion.button>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 1 }}
            className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto"
          >
            {[
              { value: "90%+", label: "Accuracy Rate" },
              { value: "0s", label: "Setup Time" },
              { value: "∞", label: "Free Checks" }
            ].map((stat, index) => (
              <div key={index} className="glass p-6 rounded-2xl hover-lift">
                <div className="text-4xl font-bold text-crypto-400 mb-2">{stat.value}</div>
                <div className="text-crypto-200">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 relative">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-bold text-gradient mb-4">
              Powerful Features
            </h2>
            <p className="text-xl text-crypto-300">
              Enterprise-grade misinformation detection at your fingertips
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ y: -10 }}
                className="glass p-8 rounded-2xl hover-lift"
              >
                <div className="text-crypto-400 mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-2xl font-bold text-crypto-200 mb-3">
                  {feature.title}
                </h3>
                <p className="text-crypto-300">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-4 bg-crypto-950/50">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-bold text-gradient mb-4">
              How It Works
            </h2>
            <p className="text-xl text-crypto-300">
              Three simple steps to verify any claim
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              {
                step: "01",
                title: "Upload or Paste",
                description: "Upload an image with text or paste the claim you want to verify"
              },
              {
                step: "02",
                title: "AI Analysis",
                description: "Our AI extracts claims using OCR and NLP, then searches the web for evidence"
              },
              {
                step: "03",
                title: "Get Results",
                description: "Receive a clear verdict with sources and explanations in seconds"
              }
            ].map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
                className="relative"
              >
                <div className="text-8xl font-bold text-crypto-800 absolute -top-8 -left-4">
                  {step.step}
                </div>
                <div className="glass p-8 rounded-2xl relative z-10 hover-lift">
                  <h3 className="text-2xl font-bold text-crypto-200 mb-4">
                    {step.title}
                  </h3>
                  <p className="text-crypto-300">
                    {step.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto text-center glass p-12 rounded-3xl"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gradient mb-6">
            Ready to Fight Misinformation?
          </h2>
          <p className="text-xl text-crypto-300 mb-8">
            Join the fight against fake news. Start verifying claims right now.
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/analyze')}
            className="px-12 py-5 bg-gradient-to-r from-crypto-600 to-brown-600 text-white text-xl font-bold rounded-full shadow-2xl hover:shadow-crypto-500/50 transition-all duration-300"
          >
            Get Started - It's Free
          </motion.button>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-crypto-800">
        <div className="max-w-6xl mx-auto text-center text-crypto-400">
          <p>© 2025 MisinfoGuard. Fighting misinformation with AI.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
