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

// Unified landing + welcome experience
function LandingPage() {
  const { isAuthenticated, loginWithPopup } = useAuth0();
  const navigate = useNavigate();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);

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
      {/* Scenic background */}
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage:
            "url('https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1600&q=80')",
        }}
      />
      {/* Soft gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-emerald-900/80 via-emerald-900/60 to-slate-900/90" />

      {/* Content */}
      <div className="relative flex min-h-screen items-center justify-center px-4 py-10">
        <div className="max-w-3xl w-full text-center text-emerald-50 space-y-8">
          <div className="flex flex-col items-center gap-3">
            <span className="text-5xl md:text-6xl">🌱</span>
            <h1 className="text-4xl md:text-5xl font-semibold tracking-tight">
              Garden
            </h1>
            <p className="text-lg md:text-xl text-emerald-100/90">
              Grow what matters, together.
            </p>
          </div>

          <p className="mx-auto max-w-xl text-sm md:text-base text-emerald-100/80">
            Tiny rituals, honest check-ins, and a community that quietly roots for your next small step.
          </p>

          <div className="flex flex-col items-center gap-4 md:flex-row md:justify-center">
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

          <p className="text-xs text-emerald-100/70">
            No long forms up front—simply pick a path and start planting small habits.
          </p>
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

// MVP Profile page
const Profile = () => {
  const { user, logout } = useAuth0();
  return (
    <div className="min-h-screen bg-slate-900 text-white p-4">
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-4">My Profile</h1>
        <div className="bg-slate-800 rounded-lg p-4 mb-4">
          <p className="text-slate-300">Email: {user?.email}</p>
          <p className="text-slate-300">Name: {user?.name || 'Not set'}</p>
        </div>
        <button
          onClick={() => logout({ returnTo: window.location.origin })}
          className="w-full py-2 bg-red-600 hover:bg-red-500 rounded-lg font-medium"
        >
          Logout
        </button>
        <a href="/feed" className="block text-center mt-4 text-emerald-400 hover:underline">
          ← Back to Feed
        </a>
      </div>
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
};

// Protected Route wrapper
function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading, loginWithRedirect } = useAuth0();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      loginWithRedirect();
    }
  }, [isLoading, isAuthenticated, loginWithRedirect]);

  if (isLoading) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div>Loading...</div>
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
