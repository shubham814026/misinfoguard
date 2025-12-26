const express = require('express');
const router = express.Router();
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');
const Stats = require('../models/Stats');

const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:8000';

// Increment analysis count in MongoDB
const incrementAnalysisCount = async () => {
    try {
        await Stats.incrementAnalyses();
    } catch (error) {
        console.error('Error incrementing analysis count:', error);
    }
};

// Analyze image endpoint
router.post('/image', async (req, res) => {
    try {
        const { filePath } = req.body;
        
        if (!filePath) {
            return res.status(400).json({
                success: false,
                error: 'File path is required'
            });
        }
        
        // Check if file exists
        if (!fs.existsSync(filePath)) {
            return res.status(404).json({
                success: false,
                error: 'File not found'
            });
        }
        
        // Create form data
        const formData = new FormData();
        formData.append('file', fs.createReadStream(filePath));
        
        // Send to Python service
        const response = await axios.post(
            `${PYTHON_SERVICE_URL}/api/analyze/image`,
            formData,
            {
                headers: formData.getHeaders(),
                timeout: 30000 // 30 seconds
            }
        );
        
        const analysisResult = response.data;
        
        // If analysis successful and claims found, fact-check them
        if (analysisResult.success && analysisResult.claims && analysisResult.claims.length > 0) {
            const factCheckResponse = await axios.post(
                `${PYTHON_SERVICE_URL}/api/fact-check`,
                {
                    claims: analysisResult.claims
                },
                {
                    timeout: 60000 // 60 seconds for fact-checking
                }
            );
            
            // Increment analysis count on success
            incrementAnalysisCount();
            
            res.json({
                success: true,
                analysis: analysisResult,
                factCheck: factCheckResponse.data.results
            });
        } else {
            // Increment analysis count on success
            incrementAnalysisCount();
            
            res.json({
                success: true,
                analysis: analysisResult,
                factCheck: []
            });
        }
        
        // Clean up uploaded file
        try {
            fs.unlinkSync(filePath);
        } catch (err) {
            console.error('Error deleting file:', err);
        }
        
    } catch (error) {
        console.error('Image analysis error:', error);
        
        // Handle specific error types
        if (error.response) {
            return res.status(error.response.status).json({
                success: false,
                error: error.response.data.detail || error.response.data.error || 'Analysis failed'
            });
        }
        
        // Handle timeout errors
        if (error.code === 'ECONNABORTED') {
            return res.status(504).json({
                success: false,
                error: 'Analysis timed out. Please try with a smaller image.'
            });
        }
        
        res.status(500).json({
            success: false,
            error: error.message || 'Analysis failed'
        });
    }
});

// Analyze text endpoint
router.post('/text', async (req, res) => {
    try {
        const { text } = req.body;
        
        if (!text || text.trim().length === 0) {
            return res.status(400).json({
                success: false,
                error: 'Text is required'
            });
        }

        // Limit text length to prevent abuse
        if (text.length > 10000) {
            return res.status(400).json({
                success: false,
                error: 'Text is too long. Maximum 10,000 characters allowed.'
            });
        }
        
        // Send to Python service for NLP analysis
        const analysisResponse = await axios.post(
            `${PYTHON_SERVICE_URL}/api/analyze/text`,
            { text },
            {
                timeout: 30000
            }
        );
        
        const analysisResult = analysisResponse.data;
        
        // Fact-check claims
        if (analysisResult.success && analysisResult.claims && analysisResult.claims.length > 0) {
            const factCheckResponse = await axios.post(
                `${PYTHON_SERVICE_URL}/api/fact-check`,
                {
                    claims: analysisResult.claims
                },
                {
                    timeout: 60000
                }
            );
            
            // Increment analysis count on success
            incrementAnalysisCount();
            
            res.json({
                success: true,
                analysis: analysisResult,
                factCheck: factCheckResponse.data.results
            });
        } else {
            // Increment analysis count on success
            incrementAnalysisCount();
            
            res.json({
                success: true,
                analysis: analysisResult,
                factCheck: []
            });
        }
        
    } catch (error) {
        console.error('Text analysis error:', error);
        
        if (error.response) {
            return res.status(error.response.status).json({
                success: false,
                error: error.response.data.detail || error.response.data.error || 'Analysis failed'
            });
        }
        
        res.status(500).json({
            success: false,
            error: error.message || 'Analysis failed'
        });
    }
});

// Direct fact-check endpoint
router.post('/fact-check', async (req, res) => {
    try {
        const { claims } = req.body;
        
        if (!claims || !Array.isArray(claims) || claims.length === 0) {
            return res.status(400).json({
                success: false,
                error: 'Claims array is required'
            });
        }
        
        const response = await axios.post(
            `${PYTHON_SERVICE_URL}/api/fact-check`,
            { claims },
            {
                timeout: 60000
            }
        );
        
        res.json(response.data);
        
    } catch (error) {
        console.error('Fact-check error:', error);
        
        if (error.response) {
            return res.status(error.response.status).json({
                success: false,
                error: error.response.data.detail || error.response.data.error || 'Fact-check failed'
            });
        }
        
        res.status(500).json({
            success: false,
            error: error.message || 'Fact-check failed'
        });
    }
});

module.exports = router;
