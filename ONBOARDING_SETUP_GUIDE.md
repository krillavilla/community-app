# 🌱 Onboarding Setup Guide - Step by Step

## ✅ What's Already Done

- ✅ Welcome.jsx created in `frontend/src/components/onboarding/`
- ✅ ChoosePath.jsx created in `frontend/src/components/onboarding/`
- ✅ Tailwind CSS installed

---

## 📝 Step 1: Configure Tailwind CSS (5 minutes)

### 1a. Update `frontend/tailwind.config.js`

**File**: `frontend/tailwind.config.js`

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        green: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          900: '#14532d',
        },
      },
    },
  },
  plugins: [],
}
```

### 1b. Update `frontend/src/index.css`

**File**: `frontend/src/index.css`

Replace entire content with:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Optional: Custom base styles */
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

---

## 📝 Step 2: Create Remaining Onboarding Components

### 2a. Create Profile Setup Component

**File**: `frontend/src/components/onboarding/CreateProfile.jsx`

```jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';

export default function CreateProfile() {
  const navigate = useNavigate();
  const { user, loginWithRedirect, isAuthenticated } = useAuth0();
  const [displayName, setDisplayName] = useState('');
  const [bio, setBio] = useState('');

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
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Share a bit about your growth journey..."
              rows={4}
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
```

### 2b. Create First Seed Component

**File**: `frontend/src/components/onboarding/PlantFirstSeed.jsx`

```jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function PlantFirstSeed() {
  const navigate = useNavigate();
  const [selectedSeed, setSelectedSeed] = useState(null);
  const [customSeed, setCustomSeed] = useState('');
  const [frequency, setFrequency] = useState('daily');

  const userPaths = JSON.parse(localStorage.getItem('userPaths') || '[]');

  const seedSuggestions = {
    personal: [
      { id: 'read', icon: '📚', name: 'Daily Reading', description: '15 minutes of reading' },
      { id: 'exercise', icon: '🏃', name: 'Exercise', description: 'Physical activity' },
      { id: 'learn', icon: '🎓', name: 'Learn Something New', description: 'Skill development' },
    ],
    emotional: [
      { id: 'gratitude', icon: '🙏', name: 'Gratitude Journal', description: 'Write 3 things daily' },
      { id: 'meditate', icon: '🧘', name: 'Meditation', description: 'Mindfulness practice' },
      { id: 'selfcare', icon: '💆', name: 'Self-Care', description: 'Me-time activities' },
    ],
    spiritual: [
      { id: 'prayer', icon: '🙏', name: 'Prayer Time', description: 'Connect with God' },
      { id: 'scripture', icon: '📖', name: 'Scripture Reading', description: 'Study the Word' },
      { id: 'worship', icon: '🎵', name: 'Worship', description: 'Praise and worship' },
    ],
  };

  // Get relevant suggestions based on selected paths
  const relevantSeeds = userPaths.flatMap(path => seedSuggestions[path] || []);

  const handlePlant = () => {
    const seedName = selectedSeed 
      ? relevantSeeds.find(s => s.id === selectedSeed)?.name 
      : customSeed;

    // TODO: Save to backend
    localStorage.setItem('firstSeed', JSON.stringify({
      name: seedName,
      frequency,
      createdAt: new Date().toISOString()
    }));

    navigate('/onboarding/complete');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-emerald-50 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="text-5xl">🌱</div>
          <h1 className="text-4xl font-bold text-green-900">
            Plant Your First Seed
          </h1>
          <p className="text-lg text-gray-700">
            Choose a growth habit to start nurturing
          </p>
        </div>

        {/* Seed Suggestions */}
        {relevantSeeds.length > 0 && (
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Suggested Seeds</h3>
            <div className="grid md:grid-cols-3 gap-4">
              {relevantSeeds.map((seed) => (
                <div
                  key={seed.id}
                  onClick={() => setSelectedSeed(seed.id)}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedSeed === seed.id
                      ? 'border-green-500 bg-green-50 shadow-lg'
                      : 'border-gray-200 bg-white hover:border-green-300'
                  }`}
                >
                  <div className="text-3xl mb-2">{seed.icon}</div>
                  <h4 className="font-semibold text-gray-900">{seed.name}</h4>
                  <p className="text-sm text-gray-600">{seed.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Custom Seed */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Or create your own</h3>
          <input
            type="text"
            value={customSeed}
            onChange={(e) => {
              setCustomSeed(e.target.value);
              setSelectedSeed(null);
            }}
            placeholder="Type your custom habit..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>

        {/* Frequency */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">How often?</h3>
          <div className="flex gap-4">
            {['daily', 'weekly', 'as-needed'].map((freq) => (
              <button
                key={freq}
                onClick={() => setFrequency(freq)}
                className={`px-6 py-2 rounded-full font-medium capitalize ${
                  frequency === freq
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {freq.replace('-', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Buttons */}
        <div className="flex flex-col items-center space-y-4">
          <button
            onClick={handlePlant}
            disabled={!selectedSeed && !customSeed.trim()}
            className={`
              px-12 py-4 rounded-full font-semibold text-lg shadow-lg
              transform transition hover:scale-105 active:scale-95
              ${(selectedSeed || customSeed.trim())
                ? 'bg-green-600 hover:bg-green-700 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }
            `}
          >
            Plant Seed 🌱
          </button>

          <button
            onClick={() => navigate('/onboarding/profile')}
            className="text-gray-600 hover:text-gray-800 underline text-sm"
          >
            ← Back
          </button>
        </div>
      </div>
    </div>
  );
}
```

### 2c. Create Completion Screen

**File**: `frontend/src/components/onboarding/Complete.jsx`

```jsx
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

export default function Complete() {
  const navigate = useNavigate();
  const [profile] = useState(() => JSON.parse(localStorage.getItem('userProfile') || '{}'));
  const [seed] = useState(() => JSON.parse(localStorage.getItem('firstSeed') || '{}'));

  useEffect(() => {
    // TODO: Mark onboarding as complete in backend
    localStorage.setItem('onboardingComplete', 'true');
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-emerald-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full text-center space-y-8">
        {/* Celebration */}
        <div className="text-8xl mb-4">🎉</div>
        
        <h1 className="text-5xl font-bold text-green-900">
          Your Garden is Ready!
        </h1>
        
        <p className="text-xl text-gray-700">
          Welcome, <span className="font-semibold text-green-700">{profile.displayName}</span>!
        </p>

        {/* Summary */}
        <div className="bg-white rounded-2xl shadow-lg p-8 space-y-4">
          <h3 className="text-2xl font-semibold text-gray-900">
            Your First Seed 🌱
          </h3>
          <p className="text-lg text-gray-700">
            {seed.name}
          </p>
          <p className="text-sm text-gray-500 capitalize">
            {seed.frequency}
          </p>
        </div>

        {/* Encouragement */}
        <div className="bg-green-50 rounded-xl p-6">
          <p className="text-lg text-green-800">
            "Every great tree was once a small seed. Your journey of growth starts today."
          </p>
        </div>

        {/* CTA */}
        <button
          onClick={() => navigate('/dashboard')}
          className="bg-green-600 hover:bg-green-700 text-white font-semibold 
                     text-lg px-12 py-4 rounded-full shadow-lg 
                     transform transition hover:scale-105 active:scale-95"
        >
          Enter My Garden 🌿
        </button>
      </div>
    </div>
  );
}
```

---

## 📝 Step 3: Update App.jsx with Routes

**File**: `frontend/src/App.jsx`

Add these imports at the top:

```jsx
// Add to existing imports
import Welcome from './components/onboarding/Welcome';
import ChoosePath from './components/onboarding/ChoosePath';
import CreateProfile from './components/onboarding/CreateProfile';
import PlantFirstSeed from './components/onboarding/PlantFirstSeed';
import Complete from './components/onboarding/Complete';
```

Add these routes inside the `<Routes>` component (around line 116):

```jsx
{/* Onboarding Routes */}
<Route path="/onboarding/welcome" element={<Welcome />} />
<Route path="/onboarding/path" element={<ChoosePath />} />
<Route path="/onboarding/profile" element={<CreateProfile />} />
<Route path="/onboarding/seed" element={<PlantFirstSeed />} />
<Route path="/onboarding/complete" element={<Complete />} />
```

Update the LandingPage component (around line 14):

```jsx
const LandingPage = () => {
  const { isAuthenticated } = useAuth0();
  
  // Check if onboarding is complete
  const onboardingComplete = localStorage.getItem('onboardingComplete');
  
  // Redirect authenticated users
  if (isAuthenticated && onboardingComplete) {
    return <Navigate to="/dashboard" replace />;
  }
  
  if (isAuthenticated && !onboardingComplete) {
    return <Navigate to="/onboarding/welcome" replace />;
  }
  
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>🌱 Garden</h1>
      <p>A platform for growth</p>
      <button 
        onClick={() => window.location.href = '/onboarding/welcome'}
        style={{ 
          padding: '12px 24px', 
          fontSize: '16px', 
          cursor: 'pointer',
          backgroundColor: '#16a34a',
          color: 'white',
          border: 'none',
          borderRadius: '8px'
        }}
      >
        Begin Your Journey
      </button>
    </div>
  );
};
```

---

## 🚀 Step 4: Test It!

### 4a. Rebuild Frontend

```bash
cd /home/krillavilla/Documents/community-app
docker compose down frontend
docker compose build --no-cache frontend
docker compose up -d frontend
```

### 4b. Test in Browser

1. Go to: http://localhost
2. Click "Begin Your Journey"
3. Flow through: Welcome → Choose Path → Profile → Plant Seed → Complete
4. Should end at Dashboard

---

## 🐛 Troubleshooting

### If Tailwind styles don't work:
```bash
cd frontend
npm run build
```

### If routes don't work:
Check that all imports are correct in App.jsx

### If Auth0 login fails:
- Clear localStorage: `localStorage.clear()`
- Check Auth0 .env variables

---

## 📊 Commit Your Work

```bash
cd /home/krillavilla/Documents/community-app
git add .
git commit -m "feat: Complete onboarding flow with 5 screens

- Welcome, ChoosePath, CreateProfile, PlantFirstSeed, Complete
- Tailwind CSS configured
- Full user flow functional
- Spiritual content opt-in
- Mobile responsive"
git push
```

---

## ✅ Success! You now have a complete onboarding flow! 🎉
