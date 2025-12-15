const express = require('express');
const router = express.Router();

// Health check endpoint
router.get('/', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        service: 'MisinfoGuard Backend'
    });
});

module.exports = router;
