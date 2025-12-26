import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const AnalyzePage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('text');
  const [textInput, setTextInput] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [feedbackGiven, setFeedbackGiven] = useState(false);

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
    maxSize: 10485760,
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
      const formData = new FormData();
      formData.append('file', uploadedFile);

      const uploadResponse = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (!uploadResponse.data.success) {
        throw new Error(uploadResponse.data.error || 'Upload failed');
      }

      const analyzeResponse = await axios.post(`${API_URL}/api/analyze/image`, {
        filePath: uploadResponse.data.file.path
      });

      if (analyzeResponse.data.success) {
        setResults(analyzeResponse.data);
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
    setFeedbackGiven(false);
  };

  const submitFeedback = async (helpful) => {
    try {
      await axios.post(`${API_URL}/api/feedback`, { helpful });
      setFeedbackGiven(true);
      toast.success('Thank you for your feedback!');
    } catch (error) {
      // Silently fail - feedback is optional
      setFeedbackGiven(true);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-slate-600 hover:text-navy-900 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span className="font-medium">Back</span>
            </button>
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 bg-navy-900 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.649 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.35-.166-2A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z" clipRule="evenodd" />
                </svg>
              </div>
              <span className="font-semibold text-navy-900">MIS InfoGuard</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          {!results ? (
            <motion.div
              key="input"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
            >
              {/* Title */}
              <div className="mb-8">
                <h1 className="text-2xl md:text-3xl font-bold text-navy-900 mb-2">
                  Check your content
                </h1>
                <p className="text-slate-600">
                  Paste text or upload an image to verify its accuracy.
                </p>
              </div>

              {/* Tab Selector */}
              <div className="flex gap-2 mb-6 p-1 bg-slate-100 rounded-lg w-fit">
                <button
                  onClick={() => setActiveTab('text')}
                  className={`px-4 py-2 rounded-md font-medium text-sm transition-all ${
                    activeTab === 'text'
                      ? 'bg-white text-navy-900 shadow-sm'
                      : 'text-slate-600 hover:text-navy-900'
                  }`}
                >
                  Paste Text
                </button>
                <button
                  onClick={() => setActiveTab('image')}
                  className={`px-4 py-2 rounded-md font-medium text-sm transition-all ${
                    activeTab === 'image'
                      ? 'bg-white text-navy-900 shadow-sm'
                      : 'text-slate-600 hover:text-navy-900'
                  }`}
                >
                  Upload File
                </button>
              </div>

              {/* Text Input Tab */}
              {activeTab === 'text' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="space-y-4"
                >
                  <div className="relative">
                    <textarea
                      value={textInput}
                      onChange={(e) => setTextInput(e.target.value.slice(0, 10000))}
                      placeholder="Enter the news, claim, or statement you want to verify..."
                      rows={6}
                      maxLength={10000}
                      className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-navy-500 focus:border-transparent transition-all resize-none"
                    />
                    <span className={`absolute bottom-3 right-3 text-xs ${textInput.length > 9000 ? 'text-warning-600' : 'text-slate-400'}`}>
                      {textInput.length.toLocaleString()}/10,000
                    </span>
                  </div>
                  <button
                    onClick={analyzeText}
                    disabled={!textInput.trim() || analyzing}
                    className="w-full px-6 py-3 bg-navy-900 text-white font-semibold rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:bg-navy-800 transition-all flex items-center justify-center gap-2"
                  >
                    {analyzing ? (
                      <>
                        <LoadingSpinner />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        Verify Content
                      </>
                    )}
                  </button>
                </motion.div>
              )}

              {/* Image Upload Tab */}
              {activeTab === 'image' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="space-y-4"
                >
                  <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                      isDragActive
                        ? 'border-navy-500 bg-navy-50'
                        : uploadedFile
                        ? 'border-verified-500 bg-verified-50'
                        : 'border-slate-300 hover:border-navy-400 hover:bg-slate-50'
                    }`}
                  >
                    <input {...getInputProps()} />
                    {uploadedFile ? (
                      <div>
                        <div className="w-12 h-12 bg-verified-100 rounded-full flex items-center justify-center mx-auto mb-3">
                          <svg className="w-6 h-6 text-verified-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <p className="text-lg font-medium text-navy-900 mb-1">
                          {uploadedFile.name}
                        </p>
                        <p className="text-slate-500 text-sm">
                          {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB • Click to change
                        </p>
                      </div>
                    ) : (
                      <div>
                        <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-3">
                          <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                          </svg>
                        </div>
                        <p className="text-lg font-medium text-navy-900 mb-1">
                          {isDragActive ? 'Drop your file here' : 'Drag & drop or click to upload'}
                        </p>
                        <p className="text-slate-500 text-sm">
                          Supports JPG, PNG, PDF (Max 10MB)
                        </p>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={analyzeImage}
                    disabled={!uploadedFile || analyzing}
                    className="w-full px-6 py-3 bg-navy-900 text-white font-semibold rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:bg-navy-800 transition-all flex items-center justify-center gap-2"
                  >
                    {analyzing ? (
                      <>
                        <LoadingSpinner />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        Verify Content
                      </>
                    )}
                  </button>
                </motion.div>
              )}

              {/* Loading State */}
              {analyzing && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-8 text-center"
                >
                  <div className="inline-flex items-center gap-3 px-6 py-3 bg-slate-100 rounded-full">
                    <LoadingSpinner />
                    <span className="text-slate-600">Verifying your content...</span>
                  </div>
                </motion.div>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
            >
              <ResultsDisplay 
                results={results} 
                onReset={resetAnalysis}
                feedbackGiven={feedbackGiven}
                onFeedback={submitFeedback}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

const LoadingSpinner = () => (
  <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
  </svg>
);

const ResultsDisplay = ({ results, onReset, feedbackGiven, onFeedback }) => {
  const { factCheck = [] } = results;

  // Determine overall verdict
  const getOverallVerdict = () => {
    if (factCheck.length === 0) return null;
    
    const verdicts = factCheck.map(r => r.verdict);
    if (verdicts.every(v => v === 'LIKELY TRUE')) return 'real';
    if (verdicts.some(v => v === 'LIKELY FALSE')) return 'fake';
    return 'misleading';
  };

  const overallVerdict = getOverallVerdict();
  const primaryResult = factCheck[0];

  const verdictConfig = {
    real: {
      label: 'Likely Real',
      bgColor: 'bg-verified-50',
      borderColor: 'border-verified-200',
      textColor: 'text-verified-700',
      iconBg: 'bg-verified-100',
      icon: (
        <svg className="w-8 h-8 text-verified-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    },
    fake: {
      label: 'Likely Fake',
      bgColor: 'bg-danger-50',
      borderColor: 'border-danger-200',
      textColor: 'text-danger-700',
      iconBg: 'bg-danger-100',
      icon: (
        <svg className="w-8 h-8 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    },
    misleading: {
      label: 'Misleading',
      bgColor: 'bg-warning-50',
      borderColor: 'border-warning-200',
      textColor: 'text-warning-700',
      iconBg: 'bg-warning-100',
      icon: (
        <svg className="w-8 h-8 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      )
    }
  };

  const config = overallVerdict ? verdictConfig[overallVerdict] : null;

  return (
    <div className="space-y-6">
      {/* Primary Result Card - FIRST */}
      {config && primaryResult && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className={`${config.bgColor} ${config.borderColor} border-2 rounded-2xl p-6`}
        >
          <div className="flex items-start gap-4">
            <div className={`${config.iconBg} rounded-full p-3 flex-shrink-0`}>
              {config.icon}
            </div>
            <div className="flex-1">
              <h2 className={`text-2xl font-bold ${config.textColor} mb-1`}>
                {config.label}
              </h2>
              <div className="text-slate-600 mb-3">
                Confidence: <span className="font-semibold">{primaryResult.confidence}%</span>
              </div>
              <p className="text-slate-700 leading-relaxed">
                {primaryResult.explanation}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* No Claims Found */}
      {factCheck.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card p-8 text-center"
        >
          <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-navy-900 mb-2">
            No verifiable claims found
          </h3>
          <p className="text-slate-600">
            We couldn't extract verifiable claims from this content. Try with different text or an image with clearer text.
          </p>
        </motion.div>
      )}

      {/* Analyzed Claim */}
      {primaryResult && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-6"
        >
          <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wide mb-2">
            Analyzed Claim
          </h3>
          <p className="text-lg text-navy-900">
            "{primaryResult.claim}"
          </p>
        </motion.div>
      )}

      {/* Sources */}
      {primaryResult?.sources && primaryResult.sources.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card p-6"
        >
          <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wide mb-4">
            Sources ({primaryResult.total_sources_found} found)
          </h3>
          <div className="space-y-3">
            {primaryResult.sources.slice(0, 5).map((source, idx) => (
              <a
                key={idx}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors border border-slate-200"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-navy-700">
                        {source.source_name}
                      </span>
                      <span className="text-xs px-2 py-0.5 bg-slate-200 text-slate-600 rounded">
                        {(source.credibility * 100).toFixed(0)}% credibility
                      </span>
                    </div>
                    <h4 className="text-navy-900 font-medium mb-1 truncate">
                      {source.title}
                    </h4>
                    <p className="text-sm text-slate-600 line-clamp-2">
                      {source.snippet}
                    </p>
                  </div>
                  <svg className="w-4 h-4 text-slate-400 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </div>
              </a>
            ))}
          </div>
        </motion.div>
      )}

      {/* Extracted Text (for image uploads) */}
      {results.analysis?.extracted_text && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card p-6"
        >
          <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wide mb-2">
            Extracted Text
          </h3>
          <p className="text-slate-700 whitespace-pre-wrap text-sm">
            {results.analysis.extracted_text}
          </p>
        </motion.div>
      )}

      {/* User Feedback */}
      {factCheck.length > 0 && !feedbackGiven && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card p-6 text-center"
        >
          <p className="text-slate-600 mb-4">Does this result help you decide?</p>
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={() => onFeedback(true)}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-verified-50 text-verified-700 font-medium rounded-lg hover:bg-verified-100 transition-colors border border-verified-200"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Yes, it helped
            </button>
            <button
              onClick={() => onFeedback(false)}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-100 text-slate-600 font-medium rounded-lg hover:bg-slate-200 transition-colors border border-slate-200"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              No, I'm not sure
            </button>
          </div>
        </motion.div>
      )}

      {feedbackGiven && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center text-slate-500 py-4"
        >
          Thank you for your feedback!
        </motion.div>
      )}

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="flex flex-col sm:flex-row gap-3 pt-4"
      >
        <button
          onClick={onReset}
          className="flex-1 px-6 py-3 bg-navy-900 text-white font-semibold rounded-xl hover:bg-navy-800 transition-colors flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Check Another
        </button>
      </motion.div>
    </div>
  );
};

export default AnalyzePage;
