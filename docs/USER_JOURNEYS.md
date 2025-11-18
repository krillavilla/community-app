# User Journey Maps - Community App
## Text-Based Flow Documentation

> These journeys map the emotional + technical path users take through your app.  
> Use this as your "network topology" for user experience.

---

## Journey 1: New User Onboarding (Phase 1 MVP)

```
═══════════════════════════════════════════════════════════════
JOURNEY: First-Time Visitor → Registered User → First Habit
═══════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Landing Page Discovery                              │
└──────────────────────────────────────────────────────────────┘
Entry Point:      User finds site (search, referral, social)
Mental State:     Curious but skeptical ("Is this another app?")
User Goals:       Understand what this is, decide if it's for me
Emotional Needs:  Safety, clarity, authenticity

User Actions:
├─ Reads hero text ("Grow Your Roots, Share Your Harvest")
├─ Scans 3 key benefits (Garden, Flourish, Orchard)
├─ Checks "Is this religious?" / "Will my data be safe?"
└─ Decides: Click "Start Growing" or leave

UI Elements:
├─ Hero section (large, inviting typography)
├─ Benefit cards (icon + short text, 3 cards)
├─ Trust signals (privacy badge, "No ads" note)
└─ CTA button (primary, center, "Start Growing")

Safety Cues:
├─ "No commitment. Explore first."
├─ Link: "How we protect your privacy"
└─ Gentle language (no aggressive sales)

Data Captured:   None (public page)
Exit Condition:  User clicks CTA → Auth page
Failure Point:   User bounces (unclear value, feels salesy)


┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Authentication (Sign Up / Log In)                   │
└──────────────────────────────────────────────────────────────┘
Entry Point:      User clicked "Start Growing"
Mental State:     Cautiously willing to share email
User Goals:       Create account quickly, minimal friction
Emotional Needs:  Trust, simplicity, control

User Actions:
├─ Sees tab toggle: "Sign Up" (default) | "Log In"
├─ Enters email + password
├─ (Optional) Agrees to terms via checkbox
├─ Clicks "Create Account"
└─ Waits for server response

UI Elements:
├─ Tabbed interface (Sign Up active by default)
├─ Input fields: email (type=email), password (type=password)
├─ Checkbox: "I agree to Terms & Privacy Policy" (links open in modal)
├─ Submit button: "Create Account"
├─ Loading state: button → spinner
└─ Link below: "Already have an account? Log in"

Safety Cues:
├─ "Privacy-first. We never sell your data."
├─ Password strength indicator (visual, non-judgmental)
└─ Error messages: "Email already registered. Try logging in?"

Technical Flow:
1. Frontend validates input (email format, password length ≥8)
2. POST /api/auth/signup → Backend
3. Backend hashes password, creates user record
4. Returns JWT token + user_id
5. Frontend stores token (httpOnly cookie or secure localStorage)
6. Redirects to Onboarding page

Data Captured:
├─ email (hashed in DB)
├─ password (bcrypt hashed)
├─ created_at timestamp
└─ user_id (UUID)

Exit Condition:  Success → Onboarding | Error → Show message
Failure Point:   Password too weak, email typo, server error


┌──────────────────────────────────────────────────────────────┐
│ STEP 3: Profile Onboarding (3-Step Wizard)                  │
└──────────────────────────────────────────────────────────────┘
Entry Point:      Just signed up, user is hopeful
Mental State:     Willing to share, but cautious about oversharing
User Goals:       Set up profile to unlock matching
Emotional Needs:  Guidance, control, no shame

User Actions:
├─ Sees progress indicator: "Step 1 of 3"
├─ Answers questions (multi-step form)
│   Step 1: "What brings you here?" (select tags)
│   Step 2: "What are you working on?" (habits/goals)
│   Step 3: "How would you describe your journey?" (text area)
├─ Clicks "Next" between steps (or "Skip" for optional)
└─ Final step: "Complete Profile" → Garden page

UI Elements:
├─ Progress bar: visual (1/3 filled → 2/3 → 3/3)
├─ Question cards: one visible at a time
├─ Input types:
│   - Step 1: Multi-select tags (bubbles: "Family", "Career", "Spirituality", "Mental Health")
│   - Step 2: Checkbox list + "Other" text input
│   - Step 3: Text area (max 300 chars)
├─ Navigation: "Back" (muted) | "Next" (primary) | "Skip" (link)
└─ Final CTA: "Complete Profile" (celebration tone)

Safety Cues:
├─ "You can change this anytime in Settings."
├─ Privacy toggles: "Who can see this? [Only connections | Everyone]"
├─ "We'll only show what you allow."
└─ No required fields except Step 1 (at least 1 tag)

Technical Flow:
1. Each step: local state update (React)
2. Final submit: POST /api/profile → Backend
3. Backend validates + stores profile_tags, preferences
4. Returns profile_id
5. Frontend updates auth context (user now "complete")
6. Redirects to Garden page

Data Captured:
├─ profile_tags (array: ["family", "career"])
├─ current_goals (array: ["meditation", "exercise"])
├─ journey_description (text)
├─ privacy_settings (object: {tags_visible: "connections"})
└─ onboarding_completed_at (timestamp)

Exit Condition:  Success → Garden (first login view)
Failure Point:   User overwhelmed (too many questions), server error


┌──────────────────────────────────────────────────────────────┐
│ STEP 4: First Garden View (Welcome Experience)              │
└──────────────────────────────────────────────────────────────┘
Entry Point:      Just completed onboarding
Mental State:     Accomplished, curious, ready to engage
User Goals:       Understand what to do next
Emotional Needs:  Celebration, clear next action

User Actions:
├─ Sees empty garden (visual: blank plot with gentle prompt)
├─ Reads welcome message: "Your garden is ready! Plant your first habit."
├─ Clicks "Plant a Habit" button (large, primary)
├─ Modal opens: "What would you like to grow?"
│   Input: habit name (e.g., "Morning meditation")
│   Optional: frequency ("Daily", "Weekly", "Custom")
├─ Submits → Modal closes, habit card appears in garden
└─ (Optional) Tooltip: "Want to see who else is here? Visit the Orchard →"

UI Elements:
├─ Empty state illustration (simple, hand-drawn garden plot)
├─ Welcome card (soft background, friendly copy)
├─ CTA button: "Plant Your First Habit"
├─ Modal: form with 2 fields (name, frequency)
├─ Success toast: "🌱 Habit planted! You're growing."
└─ Navigation hint: Subtle link to Orchard page

Safety Cues:
├─ "Start small. Add one thing."
├─ No pressure language ("You're growing at your own pace")
└─ Cancel/skip option (user can explore first)

Technical Flow:
1. GET /api/habits → Backend (returns empty array)
2. Frontend shows empty state
3. User clicks "Plant a Habit" → Modal opens
4. POST /api/habits {name, frequency} → Backend
5. Backend creates habit record, returns habit_id
6. Frontend updates local state, shows new habit card
7. (Optional) POST /api/events {type: "first_habit"} for analytics

Data Captured:
├─ habit_id (UUID)
├─ user_id (FK)
├─ habit_name (string)
├─ frequency (enum: daily, weekly, custom)
├─ created_at (timestamp)
└─ completed_dates (array, initially empty)

Exit Condition:  Habit planted → User now in active state
Failure Point:   Confused about what to do, server error

```

---

## Journey 2: Returning User - Daily Engagement

```
═══════════════════════════════════════════════════════════════
JOURNEY: Returning User → Check Habits → Mark Complete
═══════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Login (Returning User)                              │
└──────────────────────────────────────────────────────────────┘
Entry Point:      User returns to site (bookmark, habit)
Mental State:     Familiar, routine ("Let me check in")
User Goals:       Quick login, see progress
Emotional Needs:  Continuity, recognition

User Actions:
├─ Navigates to site
├─ (If already logged in) → Redirect to Garden
├─ (If not) → Enters email + password on Auth page
└─ Clicks "Log In"

UI Elements:
├─ Auth page (same as signup, "Log In" tab active)
├─ "Remember me" checkbox (optional)
├─ "Forgot password?" link
└─ Success → Redirect to Garden

Technical Flow:
1. POST /api/auth/login {email, password}
2. Backend verifies credentials
3. Returns JWT token + user_id
4. Frontend stores token, updates auth context
5. GET /api/habits → Fetch user's habits
6. Redirect to Garden page

Exit Condition:  Success → Garden | Error → Show message


┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Garden View (Active State)                          │
└──────────────────────────────────────────────────────────────┘
Entry Point:      Logged in, user sees their habits
Mental State:     Motivated, checking off tasks
User Goals:       Mark habits complete, see streaks
Emotional Needs:  Progress, satisfaction

User Actions:
├─ Sees list of habit cards (each with checkbox + name)
├─ Clicks checkbox to mark habit complete today
├─ Sees visual feedback (checkmark, subtle animation)
├─ (Optional) Clicks habit card to see details/history
└─ Navigates to other pages (Flourish, Orchard) via nav

UI Elements:
├─ Habit cards (grid or list layout)
│   Each card:
│   ├─ Checkbox (large, easy to tap)
│   ├─ Habit name
│   ├─ Frequency indicator ("Daily", "Weekly")
│   └─ Streak count ("🔥 5 day streak")
├─ Floating "+" button (add new habit)
└─ Top nav: Garden | Flourish | Orchard | Settings

Safety Cues:
├─ "No judgment. Every step counts."
├─ If habit not done today, no red/negative indicators
└─ Undo button (if accidentally clicked)

Technical Flow:
1. User clicks checkbox
2. POST /api/habits/{habit_id}/complete → Backend
3. Backend adds today's date to completed_dates array
4. Returns updated habit object
5. Frontend updates UI (checkbox filled, streak count updates)
6. Optional: Celebration toast for streaks (3, 7, 30 days)

Exit Condition:  User satisfied, navigates away or closes app
Failure Point:   Habit not saving (network error)

```

---

## Journey 3: Discovery - Finding Connections (Orchard)

```
═══════════════════════════════════════════════════════════════
JOURNEY: User → Orchard Page → View Matches → Connect
═══════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Navigate to Orchard                                 │
└──────────────────────────────────────────────────────────────┘
Entry Point:      User clicks "Orchard" in nav
Mental State:     Curious, open to connections
User Goals:       See who else is here, find shared experiences
Emotional Needs:  Safety, control, genuine connection

User Actions:
├─ Clicks "Orchard" tab in navigation
├─ Sees loading state (skeleton cards)
├─ Matches load (3-5 user cards)
└─ Scrolls through match cards

UI Elements:
├─ Page title: "The Orchard - Discover Your People"
├─ Subtitle: "Based on your shared roots and experiences"
├─ Match cards (grid layout, 3 columns on desktop)
└─ Each card:
    ├─ Profile picture (or initials if none)
    ├─ Name (first name only, or username)
    ├─ Shared tags (pills: "Family", "Career")
    ├─ Bio snippet (first 100 chars)
    └─ "Connect" button (primary)

Technical Flow:
1. GET /api/matches?limit=5 → Backend
2. Backend runs matching logic:
   - Rule-based: overlap in profile_tags
   - (Future) ML-based: similarity score
3. Returns array of user profiles (sanitized)
4. Frontend renders match cards

Data Shown (Privacy Filtered):
├─ profile_id (not user_id)
├─ display_name (first name or username)
├─ shared_tags (intersection with current user)
├─ bio_snippet (truncated)
├─ profile_picture_url (optional, blurred if private)
└─ match_reason ("You both care about family and mental health")


┌──────────────────────────────────────────────────────────────┐
│ STEP 2: View Match Profile (Modal or Page)                  │
└──────────────────────────────────────────────────────────────┘
Entry Point:      User clicks on a match card
Mental State:     Interested, evaluating ("Is this my person?")
User Goals:       Learn more, decide to connect
Emotional Needs:  Authenticity, respect for privacy

User Actions:
├─ Clicks match card → Opens profile modal/page
├─ Reads full bio, sees extended tags
├─ (Optional) Views shared habits (if user allows)
├─ Decides: "Connect" or "Not Now"
└─ Clicks "Send Connection Request"

UI Elements:
├─ Modal/page with:
│   ├─ Larger profile picture
│   ├─ Full name (if public) or username
│   ├─ Bio (full text)
│   ├─ Tags (all visible tags)
│   ├─ Shared journey highlights
│   └─ CTA: "Send Connection Request"
├─ Message input (optional): "Want to say hi?"
└─ Cancel/close button

Safety Cues:
├─ "Connection requests are opt-in. They can decline."
├─ Privacy indicator: "This user shares [X] publicly"
└─ Report button (in case of inappropriate content)

Technical Flow:
1. User clicks "Send Connection Request"
2. POST /api/connections/request {to_user_id, message}
3. Backend creates connection_request record
4. (Optional) Notification sent to recipient
5. Frontend shows success: "Request sent! They'll be notified."
6. Match card updates: "Request Pending"

Exit Condition:  Request sent, user returns to Orchard
Failure Point:   User feels matches are irrelevant, too shy to connect

```

---

## Journey 4: Progress Review (Flourish Page)

```
═══════════════════════════════════════════════════════════════
JOURNEY: User → Flourish Page → See Growth Over Time
═══════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Navigate to Flourish                                │
└──────────────────────────────────────────────────────────────┘
Entry Point:      User clicks "Flourish" in nav
Mental State:     Reflective, seeking validation
User Goals:       See progress, celebrate growth
Emotional Needs:  Encouragement, no shame for gaps

User Actions:
├─ Clicks "Flourish" tab
├─ Sees loading state (skeleton charts)
├─ Dashboard loads: habit completion trends, streaks
└─ Scrolls through insights

UI Elements:
├─ Page title: "Your Flourish - Growth Over Time"
├─ Summary cards (top row):
│   ├─ "Total Habits Planted: 5"
│   ├─ "Current Streaks: 3"
│   └─ "Days Active: 14"
├─ Chart: Completion trend (line chart, last 30 days)
├─ Habit breakdown (bar chart: habits by completion rate)
└─ Insights section:
    "You're most consistent on weekends!"
    "You've completed meditation 12 times this month 🌸"

Technical Flow:
1. GET /api/user/progress → Backend
2. Backend aggregates habit completion data
3. (Future) ML time-series analysis for insights
4. Returns summary stats + chart data
5. Frontend renders charts (use Chart.js or Recharts)

Safety Cues:
├─ "Growth isn't linear. You're doing great."
├─ No red/negative visuals for incomplete days
└─ Optional: "Privacy: Only you can see this."

Exit Condition:  User feels encouraged, motivated to continue
Failure Point:   User feels judged by gaps in data

```

---

## Journey 5: Error Recovery (User Forgot Password)

```
═══════════════════════════════════════════════════════════════
JOURNEY: User Forgot Password → Reset → Log In
═══════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Request Password Reset                              │
└──────────────────────────────────────────────────────────────┘
Entry Point:      User clicks "Forgot password?" on Auth page
Mental State:     Frustrated, needs quick fix
User Goals:       Reset password, regain access
Emotional Needs:  Support, clear instructions

User Actions:
├─ Clicks "Forgot password?" link
├─ Enters email address
├─ Clicks "Send Reset Link"
└─ Sees confirmation: "Check your email"

UI Elements:
├─ Reset page: simple form (email input + submit)
├─ Success message: "We sent a reset link to your email"
└─ Link: "Didn't get it? Resend"

Technical Flow:
1. POST /api/auth/reset-request {email}
2. Backend generates reset token (expires in 1 hour)
3. Sends email with reset link: /reset-password?token=...
4. Frontend shows success message

Exit Condition:  User checks email, clicks link
Failure Point:   Email not sent, wrong email entered


┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Reset Password                                      │
└──────────────────────────────────────────────────────────────┘
Entry Point:      User clicks reset link in email
Mental State:     Relieved, wants to finish quickly
User Goals:       Set new password, log in
Emotional Needs:  Simplicity, security

User Actions:
├─ Clicks link → Opens /reset-password page
├─ Token validates (or error: "Link expired")
├─ Enters new password (confirm field)
├─ Clicks "Reset Password"
└─ Redirects to Login page with success message

Technical Flow:
1. GET /reset-password?token=... validates token
2. User enters new password
3. POST /api/auth/reset-password {token, new_password}
4. Backend verifies token, updates password (hashed)
5. Returns success
6. Frontend redirects to Login with toast: "Password updated!"

Exit Condition:  User logs in successfully
Failure Point:   Token expired, password mismatch

```

---

## Summary: Journey Prioritization for MVP

| Priority | Journey | Why | Effort |
|----------|---------|-----|--------|
| 🔴 P0 | Onboarding (Journey 1) | Must-have for any user | High |
| 🟠 P1 | Daily Engagement (Journey 2) | Core value loop | Medium |
| 🟡 P2 | Orchard Discovery (Journey 3) | Differentiator (matching) | High |
| 🟢 P3 | Flourish Progress (Journey 4) | Retention driver | Medium |
| 🔵 P4 | Error Recovery (Journey 5) | User support | Low |

---

## Next Steps

1. **Implement Journey 1 first** (Onboarding flow)
2. Use this doc as your "spec" for building pages
3. Test each step with a friend/family member
4. Iterate based on friction points
5. Build Journey 2 next (daily loop)
