const mongoose = require('mongoose');

const statsSchema = new mongoose.Schema({
  key: {
    type: String,
    default: 'global',
    unique: true
  },
  totalAnalyses: {
    type: Number,
    default: 0
  },
  accuracyRate: {
    type: Number,
    default: 90
  },
  helpfulFeedback: {
    type: Number,
    default: 0
  },
  notHelpfulFeedback: {
    type: Number,
    default: 0
  },
  lastUpdated: {
    type: Date,
    default: Date.now
  }
}, { timestamps: true });

// Static method to get or create global stats
statsSchema.statics.getGlobalStats = async function() {
  let stats = await this.findOne({ key: 'global' });
  if (!stats) {
    stats = await this.create({ key: 'global' });
  }
  return stats;
};

// Static method to increment analysis count
statsSchema.statics.incrementAnalyses = async function() {
  const stats = await this.findOneAndUpdate(
    { key: 'global' },
    { 
      $inc: { totalAnalyses: 1 },
      $set: { lastUpdated: new Date() }
    },
    { upsert: true, new: true }
  );
  return stats;
};

// Static method to record feedback
statsSchema.statics.recordFeedback = async function(helpful) {
  const update = helpful 
    ? { $inc: { helpfulFeedback: 1 } }
    : { $inc: { notHelpfulFeedback: 1 } };
  
  update.$set = { lastUpdated: new Date() };
  
  const stats = await this.findOneAndUpdate(
    { key: 'global' },
    update,
    { upsert: true, new: true }
  );
  return stats;
};

module.exports = mongoose.model('Stats', statsSchema);
