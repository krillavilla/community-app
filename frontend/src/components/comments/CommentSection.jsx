import { useState } from 'react';
import { createComment, voteComment } from '../../services/api';
export default function CommentSection({ postId }) {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const handleSubmit = async () => {
    const result = await createComment(postId, newComment);
    setComments([...comments, result]);
    setNewComment('');
  };
  const handleVote = async (commentId, type) => {
    await voteComment(commentId, type);
    // Refresh comments
  };
  return (
    <div className="p-4 space-y-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add comment..."
          className="flex-1 px-4 py-2 border rounded-full"
        />
        <button
          onClick={handleSubmit}
          className="px-6 py-2 bg-green-600 text-white rounded-full"
        >
          Post
        </button>
      </div>
      
      {comments.map(comment => (
        <div key={comment.id} className="flex justify-between items-center">
          <p>{comment.content}</p>
          <div className="flex gap-2">
            <button onClick={() => handleVote(comment.id, 'up')}>👍</button>
            <button onClick={() => handleVote(comment.id, 'down')}>👎</button>
          </div>
        </div>
      ))}
    </div>
  );
}
