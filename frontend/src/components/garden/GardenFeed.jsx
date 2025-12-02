/**
 * GardenFeed - Main feed component for Garden System.
 * 
 * Supports three feed types:
 * - wild: Wild Garden (For You Page)
 * - rows: Garden Rows (Following)
 * - greenhouse: Greenhouse (Own seeds)
 */
import React, { useState, useEffect } from 'react';
import { SeedCard } from './SeedCard';
import { gardenAPI } from '../../services/gardenAPI';
import './GardenFeed.css';

export function GardenFeed({ feedType = 'wild' }) {
  const [seeds, setSeeds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const feedTitles = {
    wild: '🌸 Wild Garden',
    rows: '🌾 Garden Rows',
    greenhouse: '🏡 Greenhouse'
  };
  
  useEffect(() => {
    loadFeed();
  }, [feedType]);
  
  const loadFeed = async () => {
    try {
      setLoading(true);
      const data = await gardenAPI.getFeed(feedType);
      setSeeds(data.seeds);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const handleWater = async (seedId) => {
    try {
      await gardenAPI.waterSeed(seedId);
      // Update seed in state
      setSeeds(seeds.map(s => 
        s.id === seedId 
          ? { ...s, water_level: s.water_level + 1 }
          : s
      ));
    } catch (err) {
      console.error('Failed to water seed:', err);
    }
  };
  
  const handleSunlight = async (seedId) => {
    try {
      await gardenAPI.shineSunlight(seedId);
      setSeeds(seeds.map(s => 
        s.id === seedId 
          ? { ...s, sunlight_hours: s.sunlight_hours + 1 }
          : s
      ));
    } catch (err) {
      console.error('Failed to add sunlight:', err);
    }
  };
  
  const handleComment = (seedId) => {
    // TODO: Open comment modal
    console.log('Comment on seed:', seedId);
  };
  
  if (loading) {
    return <div className="feed-loading">🌱 Loading garden...</div>;
  }
  
  if (error) {
    return <div className="feed-error">❌ {error}</div>;
  }
  
  return (
    <div className="garden-feed">
      <div className="feed-header">
        <h2>{feedTitles[feedType]}</h2>
      </div>
      
      <div className="feed-content">
        {seeds.length === 0 ? (
          <div className="feed-empty">
            <p>No seeds in this garden yet 🌱</p>
          </div>
        ) : (
          seeds.map(seed => (
            <SeedCard
              key={seed.id}
              seed={seed}
              onWater={handleWater}
              onSunlight={handleSunlight}
              onComment={handleComment}
            />
          ))
        )}
      </div>
    </div>
  );
}
