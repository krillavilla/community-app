import React, { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useParams } from 'react-router-dom';
import { mvpAPI } from '../services/mvpAPI';

export default function UserProfile() {
  const { userId } = useParams();
  const { getAccessTokenSilently, user } = useAuth0();
  const [profile, setProfile] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const isOwnProfile = !userId || userId === user?.sub;

  useEffect(() => {
    loadProfile();
  }, [userId]);

  const loadProfile = async () => {
    try {
      const token = await getAccessTokenSilently();
      const targetUserId = userId || user?.sub;
      
      const [profileRes, postsRes] = await Promise.all([
        mvpAPI.getProfile(token, targetUserId),
        mvpAPI.getUserPosts(token, targetUserId)
      ]);
      
      setProfile(profileRes.data);
      setPosts(postsRes.data.posts || []);
    } catch (err) {
      console.error('Error loading profile:', err);
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async () => {
    try {
      const token = await getAccessTokenSilently();
      await mvpAPI.followUser(token, userId);
      // Refresh profile to update follow status
      loadProfile();
    } catch (err) {
      console.error('Error following user:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white">Loading profile...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-red-400">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-800 p-4">
        <div className="max-w-lg mx-auto flex items-center gap-4">
          <a href="/feed" className="text-emerald-400">← Back</a>
          <h1 className="text-xl font-bold flex-1">Profile</h1>
        </div>
      </header>

      {/* Profile Info */}
      <div className="max-w-lg mx-auto p-4">
        <div className="bg-slate-800 rounded-xl p-6 mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-20 h-20 bg-emerald-600 rounded-full flex items-center justify-center text-3xl font-bold">
              {profile?.display_name?.charAt(0)?.toUpperCase() || '?'}
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold">{profile?.display_name || 'User'}</h2>
              {profile?.bio && <p className="text-slate-400">{profile.bio}</p>}
            </div>
          </div>

          {/* Stats */}
          <div className="flex justify-around py-4 border-t border-slate-700">
            <div className="text-center">
              <div className="text-2xl font-bold">{profile?.post_count || 0}</div>
              <div className="text-slate-400 text-sm">Posts</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{profile?.follower_count || 0}</div>
              <div className="text-slate-400 text-sm">Followers</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{profile?.following_count || 0}</div>
              <div className="text-slate-400 text-sm">Following</div>
            </div>
          </div>

          {/* Follow Button */}
          {!isOwnProfile && (
            <button
              onClick={handleFollow}
              className={`w-full py-3 rounded-full font-semibold mt-4 transition ${
                profile?.is_following
                  ? 'bg-slate-600 hover:bg-slate-500 text-white'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white'
              }`}
            >
              {profile?.is_following ? 'Unfollow' : 'Follow'}
            </button>
          )}
        </div>

        {/* User's Posts */}
        <h3 className="text-lg font-semibold mb-4">Posts</h3>
        {posts.length === 0 ? (
          <p className="text-slate-400 text-center py-8">No posts yet</p>
        ) : (
          <div className="space-y-4">
            {posts.map(post => (
              <div key={post.id} className="bg-slate-800 rounded-xl p-4">
                {post.video_url && (
                  <video controls src={post.video_url} className="w-full rounded-lg mb-2" />
                )}
                <p className="text-white">{post.caption}</p>
                <div className="flex gap-4 mt-2 text-slate-400 text-sm">
                  <span>💧 {post.like_count}</span>
                  <span>💬 {post.comment_count}</span>
                  <span>⏱️ {post.hours_remaining?.toFixed(1)}h left</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
