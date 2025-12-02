import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
export default function CreateProfile() {
  const navigate = useNavigate();
  const { user, loginWithRedirect, isAuthenticated } = useAuth0();
  const [displayName, setDisplayName] = useState('');
  const [bio, setBio] = useState('');

  // Light-touch defaults so users can tap through quickly
  useEffect(() => {
    if (!user) return;
    if (!displayName) {
      const fallbackName =
        user.given_name ||
        user.nickname ||
        (user.email ? user.email.split('@')[0] : '');
      setDisplayName(fallbackName || '');
    }
  }, [user, displayName]);

  const quickBios = [
    'Here to build steady, sustainable habits.',
    'Looking for a gentle place to check in and grow.',
    'Exploring what balance and wellbeing look like for me.',
  ];

  const handleContinue = async () => {
    // TODO: Save profile to backend
    // For now, save to localStorage
    localStorage.setItem('userProfile', JSON.stringify({
      displayName,
      bio,
      email: user?.email
    }));
    navigate('/onboarding/seed');
  };
  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    loginWithRedirect({
      appState: { returnTo: '/onboarding/profile' }
    });
    return <div className="min-h-screen flex items-center justify-center">Redirecting to login...</div>;
  }
  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-emerald-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="text-5xl">👤</div>
          <h1 className="text-4xl font-bold text-green-900">
            Create Your Profile
          </h1>
          <p className="text-lg text-gray-700">
            Tell us a bit about yourself
          </p>
        </div>
        {/* Form */}
        <div className="bg-white rounded-2xl shadow-lg p-8 space-y-6">
          {/* Display Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Display Name *
            </label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="How should we call you?"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              required
            />
          </div>
          {/* Bio */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bio (Optional)
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {quickBios.map((text) => (
                <button
                  key={text}
                  type="button"
                  onClick={() => setBio(text)}
                  className={`px-3 py-1 rounded-full text-xs border transition ${
                    bio === text
                      ? 'bg-green-600 text-white border-green-600'
                      : 'bg-green-50 text-green-800 border-green-200 hover:bg-green-100'
                  }`}
                >
                  {text}
                </button>
              ))}
            </div>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Share a bit about your growth journey... (optional)"
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
          {/* Email (read-only) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              value={user?.email || ''}
              disabled
              className="w-full px-4 py-3 border border-gray-200 rounded-lg bg-gray-50 text-gray-600"
            />
          </div>
        </div>
        {/* Buttons */}
        <div className="flex flex-col items-center space-y-4">
          <button
            onClick={handleContinue}
            disabled={!displayName.trim()}
            className={`
              px-12 py-4 rounded-full font-semibold text-lg shadow-lg
              transform transition hover:scale-105 active:scale-95
              ${displayName.trim()
                ? 'bg-green-600 hover:bg-green-700 text-white cursor-pointer'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }
            `}
          >
            Continue →
          </button>
          <button
            onClick={() => navigate('/onboarding/path')}
            className="text-gray-600 hover:text-gray-800 underline text-sm"
          >
            ← Back
          </button>
        </div>
      </div>
    </div>
  );
}
