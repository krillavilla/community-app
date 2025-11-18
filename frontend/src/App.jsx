/**
 * Main App Component - Garden Platform
 * 
 * Configures Auth0, routing, and global providers.
 */
import { Auth0Provider, useAuth0 } from '@auth0/auth0-react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect } from 'react';
import { setTokenGetter } from './services/api';
import './App.css';

// Placeholder pages
const LandingPage = () => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h1>🌱 Garden Platform</h1>
    <p>Growth-oriented community platform</p>
    <Auth0LoginButton />
  </div>
);

const Dashboard = () => (
  <div style={{ padding: '2rem' }}>
    <h1>Dashboard</h1>
    <p>Welcome to your Garden Platform dashboard!</p>
    <nav>
      <a href="/garden" style={{ marginRight: '1rem' }}>My Garden</a>
      <a href="/profile">Profile</a>
    </nav>
  </div>
);

const Garden = () => (
  <div style={{ padding: '2rem' }}>
    <h1>🌱 My Garden</h1>
    <p>Track your habits here</p>
  </div>
);

const Profile = () => {
  const { user } = useAuth0();
  return (
    <div style={{ padding: '2rem' }}>
      <h1>Profile</h1>
      <p>Email: {user?.email}</p>
    </div>
  );
};

const Auth0LoginButton = () => {
  const { loginWithRedirect, isAuthenticated, logout } = useAuth0();
  
  if (isAuthenticated) {
    return (
      <div>
        <a href="/dashboard" style={{ marginRight: '1rem' }}>Go to Dashboard</a>
        <button onClick={() => logout({ returnTo: window.location.origin })}>Logout</button>
      </div>
    );
  }
  
  return <button onClick={() => loginWithRedirect()}>Login / Sign Up</button>;
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
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
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
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/garden"
        element={
          <ProtectedRoute>
            <Garden />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        }
      />
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
