import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { FaArrowLeft, FaUpload, FaImage, FaFileAlt, FaCheckCircle, FaTimesCircle, FaSpinner, FaExternalLinkAlt } from 'react-icons/fa';
import { MdContentPaste } from 'react-icons/md';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const AnalyzePage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('image');
  const [textInput, setTextInput] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setUploadedFile(file);
      toast.success(`File "${file.name}" ready to analyze`);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp'],
      'application/pdf': ['.pdf']
    },
    maxSize: 10485760, // 10MB
    multiple: false
  });

  const analyzeImage = async () => {
    if (!uploadedFile) {
      toast.error('Please upload a file first');
      return;
    }

    setAnalyzing(true);
    setResults(null);

    try {
      // Upload file first
      const formData = new FormData();
      formData.append('file', uploadedFile);

      const uploadResponse = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (!uploadResponse.data.success) {
        throw new Error(uploadResponse.data.error || 'Upload failed');
      }

      // Analyze the uploaded file
      const analyzeResponse = await axios.post(`${API_URL}/api/analyze/image`, {
        filePath: uploadResponse.data.file.path
      });

      if (analyzeResponse.data.success) {
        setResults(analyzeResponse.data);
        toast.success('Analysis complete!');
      } else {
        throw new Error(analyzeResponse.data.error || 'Analysis failed');
      }

    } catch (error) {
      console.error('Analysis error:', error);
      
      if (error.response?.status === 400 && error.response?.data?.error?.includes('Inappropriate')) {
        toast.error('Content rejected: Inappropriate or sensitive material detected');
      } else {
        toast.error(error.response?.data?.error || error.message || 'Analysis failed');
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const analyzeText = async () => {
    if (!textInput.trim()) {
      toast.error('Please enter some text to analyze');
      return;
    }

    setAnalyzing(true);
    setResults(null);

    try {
      const response = await axios.post(`${API_URL}/api/analyze/text`, {
        text: textInput
      });

      if (response.data.success) {
        setResults(response.data);
        toast.success('Analysis complete!');
      } else {
        throw new Error(response.data.error || 'Analysis failed');
      }

    } catch (error) {
      console.error('Analysis error:', error);
      
      if (error.response?.status === 400 && error.response?.data?.error?.includes('Inappropriate')) {
        toast.error('Content rejected: Inappropriate or sensitive material detected');
      } else {
        toast.error(error.response?.data?.error || error.message || 'Analysis failed');
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setResults(null);
    setUploadedFile(null);
    setTextInput('');
  };

  return (
    <div className="min-h-screen py-8 px-4">
      {/* Header */}
      <div className="max-w-6xl mx-auto mb-8">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-crypto-300 hover:text-crypto-200 transition-colors mb-6"
        >
          <FaArrowLeft />
          <span>Back to Home</span>
        </button>

        <h1 className="text-5xl font-bold text-gradient mb-4">
          Analyze Content
        </h1>
        <p className="text-xl text-crypto-300">
          Upload an image or paste text to verify its authenticity
        </p>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto">
        <AnimatePresence mode="wait">
          {!results ? (
            <motion.div
              key="input"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              {/* Tab Selector */}
              <div className="flex gap-4 mb-8">
                <button
                  onClick={() => setActiveTab('image')}
                  className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
                    activeTab === 'image'
                      ? 'bg-gradient-to-r from-crypto-600 to-brown-600 text-white shadow-lg'
                      : 'glass text-crypto-300 hover:text-crypto-200'
                  }`}
                >
                  <FaImage />
                  Upload Image/PDF
                </button>
                <button
                  onClick={() => setActiveTab('text')}
                  className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
                    activeTab === 'text'
                      ? 'bg-gradient-to-r from-crypto-600 to-brown-600 text-white shadow-lg'
                      : 'glass text-crypto-300 hover:text-crypto-200'
                  }`}
                >
                  <FaFileAlt />
                  Paste Text
                </button>
              </div>

              {/* Image Upload Tab */}
              {activeTab === 'image' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="glass p-8 rounded-2xl"
                >
                  <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
                      isDragActive
                        ? 'border-crypto-400 bg-crypto-900/50'
                        : 'border-crypto-700 hover:border-crypto-500'
                    }`}
                  >
                    <input {...getInputProps()} />
                    <FaUpload className="text-6xl text-crypto-400 mx-auto mb-4" />
                    {uploadedFile ? (
                      <div>
                        <p className="text-2xl text-crypto-200 font-semibold mb-2">
                          {uploadedFile.name}
                        </p>
                        <p className="text-crypto-400">
                          {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    ) : (
                      <div>
                        <p className="text-2xl text-crypto-200 font-semibold mb-2">
                          {isDragActive ? 'Drop file here' : 'Drag & drop or click to upload'}
                        </p>
                        <p className="text-crypto-400">
                          Supports JPG, PNG, GIF, BMP, PDF (Max 10MB)
                        </p>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={analyzeImage}
                    disabled={!uploadedFile || analyzing}
                    className="w-full mt-6 px-8 py-4 bg-gradient-to-r from-crypto-600 to-brown-600 text-white text-lg font-bold rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-crypto-500/50 transition-all flex items-center justify-center gap-3"
                  >
                    {analyzing ? (
                      <>
                        <FaSpinner className="animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <FaCheckCircle />
                        Analyze Image
                      </>
                    )}
                  </button>
                </motion.div>
              )}

              {/* Text Input Tab */}
              {activeTab === 'text' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="glass p-8 rounded-2xl"
                >
                  <div className="mb-4">
                    <label className="block text-crypto-200 font-semibold mb-2 text-lg">
                      Enter or paste the claim you want to verify:
                    </label>
                    <textarea
                      value={textInput}
                      onChange={(e) => setTextInput(e.target.value)}
                      placeholder="Enter the text or claim here..."
                      rows={8}
                      className="w-full px-4 py-3 bg-crypto-950/50 border border-crypto-700 rounded-xl text-crypto-100 placeholder-crypto-600 focus:outline-none focus:border-crypto-500 focus:ring-2 focus:ring-crypto-500/50 transition-all"
                    />
                    <p className="text-crypto-400 text-sm mt-2">
                      {textInput.length} characters
                    </p>
                  </div>

                  <button
                    onClick={analyzeText}
                    disabled={!textInput.trim() || analyzing}
                    className="w-full px-8 py-4 bg-gradient-to-r from-crypto-600 to-brown-600 text-white text-lg font-bold rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-crypto-500/50 transition-all flex items-center justify-center gap-3"
                  >
                    {analyzing ? (
                      <>
                        <FaSpinner className="animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <FaCheckCircle />
                        Analyze Text
                      </>
                    )}
                  </button>
                </motion.div>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <ResultsDisplay results={results} onReset={resetAnalysis} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

const ResultsDisplay = ({ results, onReset }) => {
  const { factCheck = [] } = results;

  return (
    <div className="space-y-6">
      {/* Reset Button */}
      <button
        onClick={onReset}
        className="mb-4 px-6 py-3 glass text-crypto-200 hover:text-crypto-100 rounded-lg font-semibold transition-all hover-lift"
      >
        ← Analyze Another
      </button>

      {/* Extracted Text */}
      {results.analysis?.extracted_text && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass p-6 rounded-2xl"
        >
          <h3 className="text-2xl font-bold text-crypto-200 mb-4">Extracted Text</h3>
          <p className="text-crypto-300 whitespace-pre-wrap">
            {results.analysis.extracted_text}
          </p>
        </motion.div>
      )}

      {/* Fact Check Results */}
      {factCheck.length > 0 ? (
        <div className="space-y-6">
          <h2 className="text-3xl font-bold text-gradient">Fact Check Results</h2>
          
          {factCheck.map((result, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass p-8 rounded-2xl hover-lift"
            >
              {/* Verdict Badge */}
              <div className="flex items-start justify-between mb-6">
                <div className="flex-1">
                  <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full font-bold text-lg mb-4 ${
                    result.verdict === 'LIKELY TRUE'
                      ? 'bg-green-600/20 text-green-400 border-2 border-green-500'
                      : 'bg-red-600/20 text-red-400 border-2 border-red-500'
                  }`}>
                    {result.verdict === 'LIKELY TRUE' ? (
                      <FaCheckCircle className="text-2xl" />
                    ) : (
                      <FaTimesCircle className="text-2xl" />
                    )}
                    {result.verdict}
                  </div>
                  
                  <div className="text-crypto-300 mb-2">
                    Confidence: <span className="text-crypto-100 font-bold">{result.confidence}%</span>
                  </div>
                </div>
              </div>

              {/* Claim */}
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-crypto-400 mb-2">Claim:</h4>
                <p className="text-crypto-100 text-lg">"{result.claim}"</p>
              </div>

              {/* Explanation */}
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-crypto-400 mb-2">Why this verdict?</h4>
                <p className="text-crypto-200 leading-relaxed">
                  {result.explanation}
                </p>
              </div>

              {/* Sources */}
              {result.sources && result.sources.length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-crypto-400 mb-4">
                    Sources ({result.total_sources_found} found):
                  </h4>
                  <div className="space-y-3">
                    {result.sources.map((source, idx) => (
                      <a
                        key={idx}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-4 bg-crypto-950/50 rounded-lg hover:bg-crypto-900/50 transition-all border border-crypto-800 hover:border-crypto-600"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-crypto-300 font-semibold">
                                {source.source_name}
                              </span>
                              <span className="text-xs px-2 py-1 bg-crypto-700 rounded text-crypto-300">
                                Credibility: {(source.credibility * 100).toFixed(0)}%
                              </span>
                            </div>
                            <h5 className="text-crypto-100 font-medium mb-2">
                              {source.title}
                            </h5>
                            <p className="text-crypto-400 text-sm">
                              {source.snippet}
                            </p>
                          </div>
                          <FaExternalLinkAlt className="text-crypto-500 flex-shrink-0" />
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {/* Red Flags */}
              {result.red_flags > 0 && (
                <div className="mt-4 p-4 bg-red-900/20 border border-red-700 rounded-lg">
                  <p className="text-red-400">
                    ⚠️ Warning: This claim contains {result.red_flags} red flag(s) commonly associated with misinformation.
                  </p>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="glass p-12 rounded-2xl text-center"
        >
          <FaTimesCircle className="text-6xl text-crypto-500 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-crypto-200 mb-2">
            No Claims Found
          </h3>
          <p className="text-crypto-400">
            Unable to extract verifiable claims from the content. Please try with different content.
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default AnalyzePage;
