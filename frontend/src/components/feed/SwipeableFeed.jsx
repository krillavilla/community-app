import React, { useState, useEffect, useRef } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { Link } from 'react-router-dom';
import { mvpAPI } from '../../services/mvpAPI';

// Create Post Modal Component
function CreatePostModal({ isOpen, onClose, onPostCreated }) {
  const { getAccessTokenSilently } = useAuth0();
  const [caption, setCaption] = useState('');
  const [isPublic, setIsPublic] = useState(true);
  const [videoFile, setVideoFile] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const recordVideoRef = useRef(null); // For recording new video
  const uploadVideoRef = useRef(null); // For uploading existing video

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!caption.trim() && !videoFile) {
      setError('Please add a message or video');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const token = await getAccessTokenSilently();
      await mvpAPI.createPost(token, caption, isPublic, videoFile);
      setCaption('');
      setVideoFile(null);
      setIsPublic(true);
      onPostCreated();
      onClose();
    } catch (err) {
      console.error('Error creating post:', err);
      setError('Failed to create post. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleVideoSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setVideoFile(file);
    }
  };

  const clearVideo = () => {
    setVideoFile(null);
    if (recordVideoRef.current) recordVideoRef.current.value = '';
    if (uploadVideoRef.current) uploadVideoRef.current.value = '';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
      <div className="w-full max-w-lg bg-slate-800 rounded-2xl p-6 shadow-2xl">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-white">Create Post</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-2xl">&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            placeholder="How are you doing today?"
            className="w-full h-32 bg-slate-700 text-white rounded-lg p-3 resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500"
            maxLength={500}
          />

          {/* Video Section */}
          {videoFile ? (
            <div className="bg-slate-700 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <span className="text-emerald-400 text-sm truncate flex-1">
                  🎬 {videoFile.name}
                </span>
                <button
                  type="button"
                  onClick={clearVideo}
                  className="text-red-400 hover:text-red-300 ml-2 text-sm"
                >
                  Remove
                </button>
              </div>
            </div>
          ) : (
            <div className="flex gap-3">
              {/* Record New Video - opens camera */}
              <input
                type="file"
                ref={recordVideoRef}
                onChange={handleVideoSelect}
                accept="video/*"
                capture="user"
                className="hidden"
              />
              <button
                type="button"
                onClick={() => recordVideoRef.current?.click()}
                className="flex-1 py-4 bg-slate-700 hover:bg-slate-600 rounded-xl text-white transition flex flex-col items-center gap-2"
              >
                <span className="text-2xl">+</span>
                <span className="text-xs text-slate-400">Record Video</span>
              </button>

              {/* Upload Existing Video */}
              <input
                type="file"
                ref={uploadVideoRef}
                onChange={handleVideoSelect}
                accept="video/*"
                className="hidden"
              />
              <button
                type="button"
                onClick={() => uploadVideoRef.current?.click()}
                className="flex-1 py-4 bg-slate-700 hover:bg-slate-600 rounded-xl text-white transition flex flex-col items-center gap-2"
              >
                <span className="text-2xl">📁</span>
                <span className="text-xs text-slate-400">Upload Video</span>
              </button>
            </div>
          )}

          <div className="flex items-center gap-4">
            <span className="text-slate-300">Privacy:</span>
            <button
              type="button"
              onClick={() => setIsPublic(true)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition ${isPublic ? 'bg-emerald-600 text-white' : 'bg-slate-700 text-slate-300'}`}
            >
              🌍 Public
            </button>
            <button
              type="button"
              onClick={() => setIsPublic(false)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition ${!isPublic ? 'bg-emerald-600 text-white' : 'bg-slate-700 text-slate-300'}`}
            >
              👥 Friends Only
            </button>
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 text-white rounded-full font-semibold transition"
          >
            {isSubmitting ? 'Posting...' : 'Post (expires in 24h)'}
          </button>
        </form>
      </div>
    </div>
  );
}

// Comments Panel Component
function CommentsPanel({ postId, isOpen, onClose }) {
  const { getAccessTokenSilently } = useAuth0();
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) loadComments();
  }, [isOpen, postId]);

  const loadComments = async () => {
    try {
      const token = await getAccessTokenSilently();
      const response = await mvpAPI.getComments(token, postId);
      setComments(response.data.comments || []);
    } catch (error) {
      console.error('Error loading comments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setSubmitting(true);
    try {
      const token = await getAccessTokenSilently();
      await mvpAPI.addComment(token, postId, newComment);
      setNewComment('');
      loadComments();
    } catch (error) {
      console.error('Error adding comment:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleVote = async (commentId, voteType) => {
    try {
      const token = await getAccessTokenSilently();
      await mvpAPI.voteComment(token, commentId, voteType);
      loadComments();
    } catch (error) {
      console.error('Error voting:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
      <div className="w-full max-w-lg bg-slate-800 rounded-2xl max-h-[80vh] flex flex-col shadow-2xl">
        <div className="flex justify-between items-center p-4 border-b border-slate-700">
          <h3 className="text-lg font-semibold text-white">Comments</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-2xl">&times;</button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {loading ? (
            <p className="text-slate-400 text-center">Loading...</p>
          ) : comments.length === 0 ? (
            <p className="text-slate-400 text-center">No comments yet. Be the first!</p>
          ) : (
            comments.map(comment => (
              <div key={comment.id} className="bg-slate-700 rounded-lg p-3">
                <div className="flex justify-between items-start mb-2">
                  <span className="font-medium text-emerald-400">{comment.author_name}</span>
                  <span className="text-xs text-slate-400">
                    {new Date(comment.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-white mb-2">{comment.content}</p>
                <div className="flex gap-4 text-sm">
                  <button
                    onClick={() => handleVote(comment.id, comment.user_vote === 'up' ? 'remove' : 'up')}
                    className={`flex items-center gap-1 ${comment.user_vote === 'up' ? 'text-emerald-400' : 'text-slate-400 hover:text-emerald-400'}`}
                  >
                    👍 {comment.upvote_count}
                  </button>
                  <button
                    onClick={() => handleVote(comment.id, comment.user_vote === 'down' ? 'remove' : 'down')}
                    className={`flex items-center gap-1 ${comment.user_vote === 'down' ? 'text-red-400' : 'text-slate-400 hover:text-red-400'}`}
                  >
                    👎 {comment.downvote_count}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        <form onSubmit={handleAddComment} className="p-4 border-t border-slate-700">
          <div className="flex gap-2">
            <input
              type="text"
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Add a comment..."
              className="flex-1 bg-slate-700 text-white rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
            <button
              type="submit"
              disabled={submitting || !newComment.trim()}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-600 text-white rounded-full font-medium"
            >
              Post
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Post Card Component
function PostCard({ post, onLike, onOpenComments }) {
  return (
    <div className="bg-slate-800 rounded-xl overflow-hidden shadow-lg">
      {/* Header */}
      <div className="flex justify-between items-center p-4">
        <a href={`/user/${post.author_id}`} className="flex items-center gap-3 hover:opacity-80">
          <div className="w-10 h-10 bg-emerald-600 rounded-full flex items-center justify-center text-white font-bold">
            {post.author_name?.charAt(0)?.toUpperCase() || '?'}
          </div>
          <span className="font-medium text-white">{post.author_name}</span>
        </a>
        {/* TODO: Timer hidden for cleaner UX - can be re-enabled in settings */}
        {/* Timer is tracked internally but not shown to avoid pressure */}
      </div>

      {/* Video */}
      {post.video_url && (
        <video
          controls
          src={post.video_url}
          className="w-full max-h-96 bg-black"
          poster={post.thumbnail_url}
        />
      )}

      {/* Caption */}
      {post.caption && (
        <p className="px-4 py-3 text-white">{post.caption}</p>
      )}

      {/* Actions */}
      {/* TODO: Consider adding animation feedback on water/nurture actions */}
      <div className="flex justify-around p-3 border-t border-slate-700">
        <button
          onClick={() => onLike(post.id)}
          title="Water this seed to help it grow"
          className={`flex items-center gap-2 px-4 py-2 rounded-full transition ${post.is_liked ? 'text-blue-400 bg-blue-900/30' : 'text-slate-300 hover:bg-slate-700'}`}
        >
          💧 Water <span>{post.like_count}</span>
        </button>
        <button
          onClick={() => onOpenComments(post.id)}
          title="Add nutrients with a thoughtful comment"
          className="flex items-center gap-2 px-4 py-2 rounded-full text-slate-300 hover:bg-slate-700 transition"
        >
          🌱 Nurture <span>{post.comment_count}</span>
        </button>
        <span className="flex items-center gap-2 px-4 py-2 text-slate-400" title="Views">
          👁️ <span>{post.view_count}</span>
        </span>
      </div>
    </div>
  );
}

// Main Feed Component
export default function SimpleFeed() {
  const { getAccessTokenSilently } = useAuth0();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [selectedPostForComments, setSelectedPostForComments] = useState(null);

  useEffect(() => {
    loadFeed();
  }, []);

  const loadFeed = async () => {
    try {
      const token = await getAccessTokenSilently();
      const response = await mvpAPI.getFeed(token);
      setPosts(response.data.posts || []);
      setError('');
    } catch (err) {
      console.error('Error loading feed:', err);
      setError('Failed to load feed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (postId) => {
    try {
      const token = await getAccessTokenSilently();
      await mvpAPI.likePost(token, postId);
      // Optimistic update
      setPosts(posts.map(p => {
        if (p.id === postId) {
          return {
            ...p,
            is_liked: !p.is_liked,
            like_count: p.is_liked ? p.like_count - 1 : p.like_count + 1
          };
        }
        return p;
      }));
    } catch (err) {
      console.error('Error liking post:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-lg">Loading your feed...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-slate-900/95 backdrop-blur border-b border-slate-800">
        <div className="max-w-lg mx-auto flex justify-between items-center p-4">
          <h1 className="text-xl font-bold text-white">🌱 Garden</h1>
          <div className="flex gap-2">
            <button
              onClick={() => setShowCreatePost(true)}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-full font-medium text-sm"
            >
              🌱 Plant
            </button>
            <Link
              to="/profile"
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-full font-medium text-sm"
            >
              Profile
            </Link>
          </div>
        </div>
      </header>

      {/* Feed */}
      <main className="max-w-lg mx-auto p-4 space-y-4 pb-20">
        {error && (
          <div className="bg-red-900/50 text-red-200 p-4 rounded-lg text-center">
            {error}
            <button onClick={loadFeed} className="block mx-auto mt-2 underline">Retry</button>
          </div>
        )}

        {posts.length === 0 ? (
          <div className="text-center py-20">
            {/* TODO: Consider adding subtle animation to the seed icon */}
            <span className="text-6xl mb-4 block">🌱</span>
            <p className="text-emerald-400 text-xl font-medium mb-2">Your garden is waiting</p>
            <p className="text-slate-400 text-sm mb-6">Plant the first seed and watch it grow</p>
            <button
              onClick={() => setShowCreatePost(true)}
              className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-full font-medium"
            >
              🌱 Plant a Seed
            </button>
          </div>
        ) : (
          posts.map(post => (
            <PostCard
              key={post.id}
              post={post}
              onLike={handleLike}
              onOpenComments={setSelectedPostForComments}
            />
          ))
        )}
      </main>

      {/* Create Post Modal */}
      <CreatePostModal
        isOpen={showCreatePost}
        onClose={() => setShowCreatePost(false)}
        onPostCreated={loadFeed}
      />

      {/* Comments Panel */}
      <CommentsPanel
        postId={selectedPostForComments}
        isOpen={!!selectedPostForComments}
        onClose={() => setSelectedPostForComments(null)}
      />

      {/* Floating Action Button - always visible for quick post creation */}
      <button
        onClick={() => setShowCreatePost(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-emerald-600 hover:bg-emerald-500 text-white rounded-full shadow-lg shadow-emerald-900/50 flex items-center justify-center text-2xl transition-transform hover:scale-110 active:scale-95 z-30"
        title="Plant a new seed"
      >
        +
      </button>
    </div>
  );
}
