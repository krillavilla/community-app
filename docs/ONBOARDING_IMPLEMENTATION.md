# 🌱 Onboarding Implementation Roadmap

## ✅ Created So Far

### Components Created
1. **Welcome.jsx** - Warm, inclusive welcome screen
2. **ChoosePath.jsx** - Opt-in path selection (personal/emotional/spiritual)

---

## 🚧 Still To Create

### 3. Profile Setup (CreateProfile.jsx)
- Display name
- Optional bio
- Avatar upload (optional)
- Save to backend

### 4. First Seed (PlantFirstSeed.jsx)
- Choose first growth habit
- Examples across all paths
- Set frequency (daily, weekly, etc.)
- Motivational onboarding

### 5. Onboarding Complete (Complete.jsx)
- Celebration screen
- "Your garden is ready!"
- Enter garden button

---

## 🔧 Integration Steps

### Update App.jsx
Add onboarding routes:
```jsx
<Route path="/onboarding/welcome" element={<Welcome />} />
<Route path="/onboarding/path" element={<ChoosePath />} />
<Route path="/onboarding/profile" element={<CreateProfile />} />
<Route path="/onboarding/seed" element={<PlantFirstSeed />} />
<Route path="/onboarding/complete" element={<Complete />} />
```

### Update index.css
Add Tailwind directives:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Configure tailwind.config.js
```js
content: [
  "./index.html",
  "./src/**/*.{js,ts,jsx,tsx}",
],
```

---

## 📊 User Flow

```
Landing Page (/)
    ↓ (Click "Begin Journey")
Welcome (/onboarding/welcome)
    ↓
Choose Path (/onboarding/path)
    ↓
Create Profile (/onboarding/profile) 
    ↓ (Auth0 login triggered)
Plant First Seed (/onboarding/seed)
    ↓
Complete (/onboarding/complete)
    ↓
Dashboard → My Garden
```

---

## 🎨 Design System

### Colors
- **Primary Green**: #059669 (green-600)
- **Light Green**: #D1FAE5 (green-50)
- **Emerald**: #10B981 (emerald-500)
- **Purple** (spiritual): #9333EA (purple-600)

### Typography
- **Headings**: Bold, large (text-4xl, text-5xl)
- **Body**: Regular, readable (text-lg, text-base)
- **Accent**: Semibold highlights

### Spacing
- Generous padding and margins
- Breathing room between elements
- Mobile-responsive (p-4, max-w-* containers)

---

## 🔒 Backend Integration

### API Endpoints Needed

#### Save User Preferences
```
POST /api/v1/users/me/preferences
{
  "growth_paths": ["personal", "emotional", "spiritual"],
  "content_filters": {...}
}
```

#### Update Profile
```
PATCH /api/v1/users/me
{
  "display_name": "...",
  "bio": "...",
  "avatar_url": "..."
}
```

#### Create First Habit
```
POST /api/v1/garden/habits
{
  "name": "Morning meditation",
  "frequency": "daily",
  "category": "spiritual"
}
```

---

## ✅ Next Steps

1. Configure Tailwind properly
2. Create remaining 3 components
3. Update App.jsx with routes
4. Test onboarding flow
5. Connect to backend APIs
6. Add animations/transitions
7. Test on mobile

---

## 🎯 Success Criteria

- [ ] User can complete onboarding in < 2 minutes
- [ ] Spiritual content is clearly opt-in
- [ ] Mobile-responsive design
- [ ] Warm, welcoming tone throughout
- [ ] No technical jargon
- [ ] Clear progress indicators
- [ ] Can skip/go back easily
