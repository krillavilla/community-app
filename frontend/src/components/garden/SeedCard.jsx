/**
 * SeedCard - Displays a seed (post/video) with Garden System metrics.
 * 
 * Shows:
 * - Video player with Mux playback
 * - Lifecycle state indicator
 * - Growth metrics (water, nutrients, sunlight)
 * - Time until wilt
 * - Actions (water, sunlight, comment, vote)
 */
import React from 'react';
import { motion } from 'framer-motion';
import './SeedCard.css';

const LIFECYCLE_COLORS = {
  planted: '#8B4513',
  sprouting: '#90EE90',
  blooming: '#FFD700',
  wilting: '#FFA500',
  composting: '#696969'
};

const LIFECYCLE_LABELS = {
  planted: '🌱 Planted',
  sprouting: '🌿 Sprouting',
  blooming: '🌸 Blooming',
  wilting: '🍂 Wilting',
  composting: '♻️ Composting'
};

export function SeedCard({ seed, onWater, onSunlight, onComment, onVote }) {
  const lifecycleColor = LIFECYCLE_COLORS[seed.state] || '#888';
  const lifecycleLabel = LIFECYCLE_LABELS[seed.state] || seed.state;
  
  // Calculate growth bar widths
  const maxMetric = Math.max(seed.water_level, seed.nutrient_score, seed.sunlight_hours, 1);
  const waterWidth = (seed.water_level / maxMetric) * 100;
  const nutrientWidth = (seed.nutrient_score / maxMetric) * 100;
  const sunlightWidth = (seed.sunlight_hours / maxMetric) * 100;
  
  // Format time until wilt
  const formatTimeUntilWilt = () => {
    if (!seed.wilts_at) return null;
    const wiltsAt = new Date(seed.wilts_at);
    const now = new Date();
    const hoursLeft = Math.max(0, (wiltsAt - now) / (1000 * 60 * 60));
    
    if (hoursLeft < 1) return '< 1 hour';
    if (hoursLeft < 24) return `${Math.floor(hoursLeft)}h`;
    return `${Math.floor(hoursLeft / 24)}d`;
  };
  
  const timeUntilWilt = formatTimeUntilWilt();
  
  return (
    <motion.div
      className="seed-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Lifecycle Badge */}
      <div 
        className="lifecycle-badge"
        style={{ backgroundColor: lifecycleColor }}
      >
        {lifecycleLabel}
      </div>
      
      {/* Video Player */}
      <div className="video-container">
        {seed.mux_playback_id ? (
          <video
            controls
            poster={seed.thumbnail_url}
            src={`https://stream.mux.com/${seed.mux_playback_id}.m3u8`}
            onClick={() => onWater && onWater(seed.id)}
          />
        ) : (
          <div className="video-placeholder">
            🎬 Video processing...
          </div>
        )}
      </div>
      
      {/* Content */}
      {seed.content && (
        <div className="seed-content">
          <p>{seed.content}</p>
        </div>
      )}
      
      {/* Growth Metrics */}
      <div className="growth-metrics">
        <div className="metric">
          <span className="metric-icon">💧</span>
          <div className="metric-bar">
            <div 
              className="metric-fill water"
              style={{ width: `${waterWidth}%` }}
            />
          </div>
          <span className="metric-value">{seed.water_level}</span>
        </div>
        
        <div className="metric">
          <span className="metric-icon">🌱</span>
          <div className="metric-bar">
            <div 
              className="metric-fill nutrients"
              style={{ width: `${nutrientWidth}%` }}
            />
          </div>
          <span className="metric-value">{seed.nutrient_score}</span>
        </div>
        
        <div className="metric">
          <span className="metric-icon">☀️</span>
          <div className="metric-bar">
            <div 
              className="metric-fill sunlight"
              style={{ width: `${sunlightWidth}%` }}
            />
          </div>
          <span className="metric-value">{seed.sunlight_hours}</span>
        </div>
      </div>
      
      {/* Time Until Wilt */}
      {timeUntilWilt && (
        <div className="time-until-wilt">
          <span>🕐 {timeUntilWilt} left</span>
        </div>
      )}
      
      {/* Actions */}
      <div className="seed-actions">
        <button 
          className="action-btn water-btn"
          onClick={() => onWater && onWater(seed.id)}
          title="Water (view)"
        >
          💧 Water
        </button>
        
        <button 
          className="action-btn sunlight-btn"
          onClick={() => onSunlight && onSunlight(seed.id)}
          title="Share"
        >
          ☀️ Share
        </button>
        
        <button 
          className="action-btn comment-btn"
          onClick={() => onComment && onComment(seed.id)}
          title="Add soil (comment)"
        >
          💬 Comment
        </button>
      </div>
    </motion.div>
  );
}
