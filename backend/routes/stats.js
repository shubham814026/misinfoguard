const express = require('express');
const router = express.Router();
const Stats = require('../models/Stats');

// GET /api/stats - Get current statistics
router.get('/', async (req, res) => {
  try {
    const stats = await Stats.getGlobalStats();
    
    // Calculate helpful percentage from actual data
    const totalFeedback = stats.helpfulFeedback + stats.notHelpfulFeedback;
    const helpfulPercentage = totalFeedback > 0 
      ? Math.round((stats.helpfulFeedback / totalFeedback) * 100)
      : 0; // Show 0 if no feedback yet
    
    res.json({
      success: true,
      totalAnalyses: stats.totalAnalyses,
      accuracyRate: stats.accuracyRate,
      helpfulFeedback: helpfulPercentage,
      totalFeedbackCount: totalFeedback,
      lastUpdated: stats.lastUpdated
    });
  } catch (error) {
    console.error('Error getting stats:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to retrieve statistics'
    });
  }
});

// POST /api/stats/increment-analysis - Increment analysis count
router.post('/increment-analysis', async (req, res) => {
  try {
    const stats = await Stats.incrementAnalyses();
    
    res.json({
      success: true,
      totalAnalyses: stats.totalAnalyses
    });
  } catch (error) {
    console.error('Error incrementing analysis:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update statistics'
    });
  }
});

// POST /api/feedback - Record user feedback (mounted at /api/feedback)
router.post('/', async (req, res) => {
  try {
    const { helpful } = req.body;
    
    if (typeof helpful !== 'boolean') {
      return res.status(400).json({
        success: false,
        error: 'helpful field must be a boolean'
      });
    }
    
    const stats = await Stats.recordFeedback(helpful);
    
    const totalFeedback = stats.helpfulFeedback + stats.notHelpfulFeedback;
    const helpfulPercentage = totalFeedback > 0 
      ? Math.round((stats.helpfulFeedback / totalFeedback) * 100) 
      : 0;
    
    res.json({
      success: true,
      helpfulPercentage
    });
  } catch (error) {
    console.error('Error recording feedback:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to record feedback'
    });
  }
});

module.exports = router;
