/**
 * Main App Component - Garden Platform MVP
 *
 * Simplified for user testing:
 * - Auth0 login
 * - Video feed
 * - Posts, likes, comments, follows
 * - No complex onboarding or lifecycle features
 */
import { Auth0Provider, useAuth0 } from '@auth0/auth0-react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { setTokenGetter } from './services/api';
import SimpleFeed from './components/feed/SwipeableFeed';
import UserProfile from './pages/UserProfile';
import './App.css';

// Scenic backgrounds mapped to regions/landscape types
// TODO: Consider adding more regional variations
const SCENIC_BACKGROUNDS = {
  ocean: {
    primary: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=2000&q=80',
    secondary: 'https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=2000&q=80',
    greeting: 'by the shore',
  },
  mountain: {
    primary: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=2000&q=80',
    secondary: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=2000&q=80',
    greeting: 'in the mountains',
  },
  forest: {
    primary: 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=2000&q=80',
    secondary: 'https://images.unsplash.com/photo-1502082553048-f009c37129b9?auto=format&fit=crop&w=2000&q=80',
    greeting: 'among the trees',
  },
  desert: {
    primary: 'https://images.unsplash.com/photo-1509316785289-025f5b846b35?auto=format&fit=crop&w=2000&q=80',
    secondary: 'https://images.unsplash.com/photo-1473580044384-7ba9967e16a0?auto=format&fit=crop&w=2000&q=80',
    greeting: 'under open skies',
  },
  vineyard: {
    primary: 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=2000&q=80',
    secondary: 'https://images.unsplash.com/photo-1560493676-04071c5f467b?auto=format&fit=crop&w=2000&q=80',
    greeting: 'in the vineyard',
  },
  prairie: {
    primary: 'https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=2000&q=80',
    secondary: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?auto=format&fit=crop&w=2000&q=80',
    greeting: 'on the plains',
  },
  tropical: {
    primary: 'https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?auto=format&fit=crop&w=2000&q=80',
    secondary: 'https://images.unsplash.com/photo-1516815231560-8f41ec531527?auto=format&fit=crop&w=2000&q=80',
    greeting: 'in paradise',
  },
  lake: {
    primary: 'https://images.unsplash.com/photo-1439066615861-d1af74d74000?auto=format&fit=crop&w=2000&q=80',
    secondary: 'https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=2000&q=80',
    greeting: 'by the water',
  },
};

// Determine landscape type from coordinates
// TODO: This is a simplified heuristic - could integrate with a real geography API
function getSceneFromCoordinates(lat, lon) {
  // Coastal regions (within ~100km of major coastlines - simplified)
  const isCoastal = (
    (lon < -115 && lat > 32 && lat < 49) || // US West Coast
    (lon > -82 && lon < -70 && lat > 25 && lat < 45) || // US East Coast
    (lon > -10 && lon < 5 && lat > 35 && lat < 60) || // Western Europe
    (lon > 130 && lat > -40 && lat < -10) || // Australia East
    (lat < -20 && lon > -50 && lon < -30) // Brazil Coast
  );
  
  // Tropical regions (near equator)
  const isTropical = lat > -23.5 && lat < 23.5;
  
  // Mountain regions (simplified - major ranges)
  const isMountain = (
    (lon > -125 && lon < -100 && lat > 35 && lat < 50) || // Rockies
    (lon > 5 && lon < 20 && lat > 43 && lat < 48) || // Alps
    (lon > 70 && lon < 100 && lat > 25 && lat < 40) // Himalayas
  );
  
  // Desert regions
  const isDesert = (
    (lon > -120 && lon < -105 && lat > 30 && lat < 40) || // US Southwest
    (lon > -10 && lon < 40 && lat > 15 && lat < 35) || // Sahara
    (lon > 115 && lon < 140 && lat > -30 && lat < -20) // Australian Outback
  );

  // Wine regions (simplified)
  const isVineyard = (
    (lon > -125 && lon < -120 && lat > 34 && lat < 42) || // California
    (lon > -5 && lon < 10 && lat > 42 && lat < 48) || // France
    (lon > 10 && lon < 15 && lat > 40 && lat < 45) // Italy
  );

  if (isCoastal) return 'ocean';
  if (isTropical) return 'tropical';
  if (isMountain) return 'mountain';
  if (isDesert) return 'desert';
  if (isVineyard) return 'vineyard';
  
  // Default based on latitude
  if (lat > 45 || lat < -45) return 'forest'; // Northern/Southern forests
  if (lat > 30 || lat < -30) return 'prairie'; // Temperate zones
  return 'lake'; // Default fallback
}

// Unified landing + welcome experience
function LandingPage() {
  const { isAuthenticated, loginWithPopup } = useAuth0();
  const navigate = useNavigate();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [sceneType, setSceneType] = useState('ocean'); // Default scene
  const [locationGreeting, setLocationGreeting] = useState('');

  // Get user's location and set appropriate scene
  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          const scene = getSceneFromCoordinates(latitude, longitude);
          setSceneType(scene);
          setLocationGreeting(SCENIC_BACKGROUNDS[scene]?.greeting || '');
        },
        (error) => {
          // Geolocation denied or failed - use default
          console.log('Geolocation not available:', error.message);
          // TODO: Could use IP-based geolocation as fallback
        },
        { timeout: 5000, enableHighAccuracy: false }
      );
    }
  }, []);

  const currentScene = SCENIC_BACKGROUNDS[sceneType];

  // MVP: After login, go directly to feed
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/feed', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const startJourney = () => {
    if (isAuthenticated) {
      navigate('/onboarding/path');
    } else {
      setShowLoginModal(true);
    }
  };

  const openLogin = () => {
    setShowLoginModal(true);
  };

  const handleLogin = async () => {
    try {
      setIsLoggingIn(true);
      await loginWithPopup();
      setIsLoggingIn(false);
      setShowLoginModal(false);
      navigate('/feed');
    } catch (error) {
      console.error('Login failed', error);
      setIsLoggingIn(false);
      // TODO: Surface login error to the user if needed
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Animated background - geo-located single scene */}
      <div
        className="absolute inset-0 bg-cover bg-center animate-slow-pan transition-all duration-1000"
        style={{
          backgroundImage: `url('${currentScene?.primary}')`,
          backgroundSize: '120% 120%',
        }}
      />
      {/* Soft gradient overlay with breathing effect */}
      <div className="absolute inset-0 bg-gradient-to-b from-emerald-900/70 via-teal-900/50 to-slate-900/80 animate-breathe" />

      {/* Content */}
      <div className="relative flex min-h-screen items-center justify-center px-4 py-10">
        <div className="max-w-3xl w-full text-center text-emerald-50 space-y-8">
          {/* Floating logo and title */}
          <div className="flex flex-col items-center gap-3 animate-fade-in-up">
            <span className="text-5xl md:text-7xl animate-float drop-shadow-2xl">🌱</span>
            <h1 className="text-4xl md:text-6xl font-semibold tracking-tight drop-shadow-lg">
              Garden
            </h1>
            <p className="text-lg md:text-2xl text-emerald-100/90 font-light">
              Grow what matters, together{locationGreeting ? ` ${locationGreeting}` : ''}.
            </p>
          </div>

          <p className="mx-auto max-w-xl text-sm md:text-lg text-emerald-100/80 animate-fade-in-up animation-delay-200">
            Tiny rituals, honest check-ins, and a community that quietly roots for your next small step.
          </p>

          <div className="flex flex-col items-center gap-4 md:flex-row md:justify-center animate-fade-in-up animation-delay-400">
            <button
              type="button"
              onClick={startJourney}
              className="px-10 py-3 rounded-full bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-semibold shadow-lg shadow-emerald-900/40 transform transition hover:scale-105 active:scale-95"
            >
              Begin your journey
            </button>
            <button
              type="button"
              onClick={openLogin}
              className="px-8 py-3 rounded-full border border-emerald-200/70 text-emerald-100 hover:bg-emerald-900/40 font-medium transition"
            >
              Already growing? Sign in
            </button>
          </div>

        </div>
      </div>

      {/* Login modal */}
      {showLoginModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl space-y-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-1">Sign in to continue</h2>
            <p className="text-sm text-gray-600">
              We will save your garden, your paths, and your progress so you can pick up right where you left off.
            </p>
            <button
              type="button"
              onClick={handleLogin}
              disabled={isLoggingIn}
              className={`w-full px-4 py-3 rounded-full font-semibold text-white shadow-md transition ${
                isLoggingIn ? 'bg-emerald-400 cursor-wait' : 'bg-emerald-600 hover:bg-emerald-500'
              }`}
            >
              {isLoggingIn ? 'Connecting…' : 'Continue with secure login'}
            </button>
            <button
              type="button"
              onClick={() => setShowLoginModal(false)}
              className="w-full text-sm text-gray-500 hover:text-gray-700 mt-1"
            >
              Maybe later
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// MVP Profile page with full CRUD
const Profile = () => {
  const { user, logout, getAccessTokenSilently } = useAuth0();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [profile, setProfile] = useState({
    displayName: user?.name || '',
    bio: '',
    location: '',
    website: '',
    gardenGoal: '',
  });
  const [tempProfile, setTempProfile] = useState({ ...profile });

  // TODO: Load profile from backend on mount
  useEffect(() => {
    if (user) {
      setProfile(prev => ({
        ...prev,
        displayName: user.name || user.nickname || '',
      }));
      setTempProfile(prev => ({
        ...prev,
        displayName: user.name || user.nickname || '',
      }));
    }
  }, [user]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // TODO: Call API to save profile
      // const token = await getAccessTokenSilently();
      // await mvpAPI.updateProfile(token, tempProfile);
      setProfile({ ...tempProfile });
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to save profile:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setTempProfile({ ...profile });
    setIsEditing(false);
  };

  const handleDeleteAccount = async () => {
    try {
      // TODO: Call API to delete account
      // const token = await getAccessTokenSilently();
      // await mvpAPI.deleteAccount(token);
      logout({ returnTo: window.location.origin });
    } catch (error) {
      console.error('Failed to delete account:', error);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-slate-900/95 backdrop-blur border-b border-slate-800">
        <div className="max-w-lg mx-auto flex justify-between items-center p-4">
          <a href="/feed" className="text-emerald-400 hover:text-emerald-300">
            ← Back to Garden
          </a>
          <h1 className="text-xl font-bold">My Profile</h1>
          <div className="w-20" /> {/* Spacer for centering */}
        </div>
      </header>

      <div className="max-w-lg mx-auto p-4 space-y-6">
        {/* Avatar Section */}
        <div className="flex flex-col items-center py-6">
          <div className="w-24 h-24 bg-gradient-to-br from-emerald-500 to-emerald-700 rounded-full flex items-center justify-center text-4xl font-bold shadow-lg mb-4">
            {profile.displayName?.charAt(0)?.toUpperCase() || '🌱'}
          </div>
          <p className="text-slate-400 text-sm">{user?.email}</p>
        </div>

        {/* Profile Card */}
        <div className="bg-slate-800 rounded-xl p-6 space-y-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Profile Information</h2>
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 rounded-full text-sm font-medium transition"
              >
                Edit
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={handleCancel}
                  className="px-4 py-1.5 bg-slate-600 hover:bg-slate-500 rounded-full text-sm font-medium transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 rounded-full text-sm font-medium transition"
                >
                  {isSaving ? 'Saving...' : 'Save'}
                </button>
              </div>
            )}
          </div>

          {/* Display Name */}
          <div>
            <label className="block text-sm text-slate-400 mb-1">Display Name</label>
            {isEditing ? (
              <input
                type="text"
                value={tempProfile.displayName}
                onChange={(e) => setTempProfile({ ...tempProfile, displayName: e.target.value })}
                className="w-full bg-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="Your name"
              />
            ) : (
              <p className="text-white">{profile.displayName || 'Not set'}</p>
            )}
          </div>

          {/* Bio */}
          <div>
            <label className="block text-sm text-slate-400 mb-1">Bio</label>
            {isEditing ? (
              <textarea
                value={tempProfile.bio}
                onChange={(e) => setTempProfile({ ...tempProfile, bio: e.target.value })}
                className="w-full bg-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none h-24"
                placeholder="Tell us about yourself..."
                maxLength={200}
              />
            ) : (
              <p className="text-white">{profile.bio || 'No bio yet'}</p>
            )}
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm text-slate-400 mb-1">Location</label>
            {isEditing ? (
              <input
                type="text"
                value={tempProfile.location}
                onChange={(e) => setTempProfile({ ...tempProfile, location: e.target.value })}
                className="w-full bg-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="City, Country"
              />
            ) : (
              <p className="text-white">{profile.location || 'Not set'}</p>
            )}
          </div>

          {/* Website */}
          <div>
            <label className="block text-sm text-slate-400 mb-1">Website</label>
            {isEditing ? (
              <input
                type="url"
                value={tempProfile.website}
                onChange={(e) => setTempProfile({ ...tempProfile, website: e.target.value })}
                className="w-full bg-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="https://yoursite.com"
              />
            ) : (
              <p className="text-white">
                {profile.website ? (
                  <a href={profile.website} target="_blank" rel="noopener noreferrer" className="text-emerald-400 hover:underline">
                    {profile.website}
                  </a>
                ) : 'Not set'}
              </p>
            )}
          </div>

          {/* Garden Goal */}
          <div>
            <label className="block text-sm text-slate-400 mb-1">🌱 Garden Goal</label>
            {isEditing ? (
              <input
                type="text"
                value={tempProfile.gardenGoal}
                onChange={(e) => setTempProfile({ ...tempProfile, gardenGoal: e.target.value })}
                className="w-full bg-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="What are you growing towards?"
              />
            ) : (
              <p className="text-white">{profile.gardenGoal || 'Set your growth intention'}</p>
            )}
          </div>
        </div>

        {/* Account Actions */}
        <div className="bg-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold mb-4">Account</h2>
          
          <button
            onClick={() => logout({ returnTo: window.location.origin })}
            className="w-full py-3 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition"
          >
            Sign Out
          </button>

          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="w-full py-3 bg-red-900/50 hover:bg-red-900 text-red-400 hover:text-red-300 rounded-lg font-medium transition"
          >
            Delete Account
          </button>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
          <div className="w-full max-w-sm bg-slate-800 rounded-2xl p-6 shadow-2xl">
            <h3 className="text-xl font-bold text-red-400 mb-2">Delete Account?</h3>
            <p className="text-slate-300 mb-6">
              This will permanently delete your garden, seeds, and all data. This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 py-3 bg-slate-600 hover:bg-slate-500 rounded-lg font-medium transition"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAccount}
                className="flex-1 py-3 bg-red-600 hover:bg-red-500 rounded-lg font-medium transition"
              >
                Delete Forever
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Auth0 configuration
const auth0Config = {
  domain: import.meta.env.VITE_AUTH0_DOMAIN || 'dev-garden.us.auth0.com',
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID || 'YOUR_CLIENT_ID',
  authorizationParams: {
    redirect_uri: window.location.origin,
    audience: import.meta.env.VITE_AUTH0_AUDIENCE,
  },
  // Persist session in localStorage to prevent re-auth on navigation
  cacheLocation: 'localstorage',
  // Use refresh tokens for better session management
  useRefreshTokens: true,
};

// Protected Route wrapper
function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading, loginWithRedirect } = useAuth0();
  const [hasAttemptedLogin, setHasAttemptedLogin] = useState(false);

  useEffect(() => {
    // Only trigger login redirect once, not on every render/navigation
    if (!isLoading && !isAuthenticated && !hasAttemptedLogin) {
      setHasAttemptedLogin(true);
      // Redirect to landing page instead of triggering Auth0 directly
      // User can initiate login from there
      window.location.href = '/';
    }
  }, [isLoading, isAuthenticated, hasAttemptedLogin]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-lg">Loading...</div>
      </div>
    );
  }

  return isAuthenticated ? children : null;
}

// App content with Auth0 hooks
function AppContent() {
  const { getAccessTokenSilently } = useAuth0();

  useEffect(() => {
    // Set token getter for API service
    setTokenGetter(getAccessTokenSilently);
  }, [getAccessTokenSilently]);

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      
      {/* MVP: Main feed */}
      <Route
        path="/feed"
        element={
          <ProtectedRoute>
            <SimpleFeed />
          </ProtectedRoute>
        }
      />
      
      {/* MVP: Own profile */}
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        }
      />
      
      {/* MVP: View other user's profile */}
      <Route
        path="/user/:userId"
        element={
          <ProtectedRoute>
            <UserProfile />
          </ProtectedRoute>
        }
      />

      {/* Fallback - redirect to landing or feed */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

// Main App component
function App() {
  return (
    <Auth0Provider {...auth0Config}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </QueryClientProvider>
    </Auth0Provider>
  );
}

export default App;
