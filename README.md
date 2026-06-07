# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║         AutoIntel v6.0 — MASTER ADVANCED PROMPT (PRODUCTION-READY)         ║
# ║     Used Car Price Intelligence Platform · Full-Stack ML Streamlit App      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

You are a **senior full-stack ML engineer and UI/UX expert**. Build a COMPLETE,
production-ready, single-file Streamlit application named `streamlit_app.py` for a
Car Price Prediction ML project called **AutoIntel v6.0**.

The app must be:
- Visually stunning with a dark theme
- Functionally rich across 9 pages + Auth
- Deployable out of the box with zero configuration
- Bug-free, error-handled, and demo-mode capable when ML files are missing
- Fully authenticated with user profiles saved in a local JSON file

---

════════════════════════════════════
SECTION 0 — AUTHENTICATION SYSTEM (IMPLEMENT FIRST)
════════════════════════════════════

### Overview
Before ANY page of the app renders, the user must pass through an authentication
gate. Authentication state is stored in `st.session_state` and persisted across
the session. All user data (accounts, profiles, activity) is stored in a local
JSON file: `users_db.json`.

---

### 0.1 — `users_db.json` Schema

The file is created automatically if it does not exist. Structure:

```json
{
  "users": {
    "user_id_uuid4": {
      "user_id": "uuid4-string",
      "username": "johndoe",
      "email": "john@example.com",
      "password_hash": "bcrypt-or-sha256-hash",
      "full_name": "John Doe",
      "role": "user",           // "user" | "admin"
      "avatar_color": "#e85d04",// random from palette on signup
      "created_at": "2024-01-15T10:30:00",
      "last_login": "2024-06-01T08:45:00",
      "login_count": 42,
      "preferences": {
        "default_model": "xgboost",
        "confidence_interval": "±15%",
        "expert_mode": false,
        "theme_accent": "#e85d04"
      },
      "prediction_history": [
        {
          "timestamp": "2024-06-01T08:50:00",
          "company": "Maruti",
          "name": "Swift",
          "year": 2019,
          "kms_driven": 45000,
          "fuel_type": "Petrol",
          "model_used": "xgboost",
          "predicted_price": 485000,
          "session_id": "sess_uuid4"
        }
      ],
      "saved_comparisons": [
        {
          "comparison_id": "comp_uuid4",
          "name": "My Comparison 1",
          "car_a": {...},
          "car_b": {...},
          "created_at": "2024-06-01T09:00:00"
        }
      ],
      "page_visits": {
        "Dashboard": 12,
        "Dataset Explorer": 5,
        "Price Predictor": 20
      }
    }
  },
  "meta": {
    "total_users": 3,
    "total_predictions": 156,
    "app_version": "6.0",
    "last_updated": "2024-06-01T10:00:00"
  }
}
```

---

### 0.2 — Auth Helper Functions

Implement ALL of these in a dedicated section at the top of the file:

```python
# ── Auth helpers ──────────────────────────────────────────────────────────────

import json, uuid, hashlib
from datetime import datetime
from pathlib import Path

USERS_DB_PATH = Path("users_db.json")

def load_users_db() -> dict:
    """Load users DB from JSON. Create file with empty structure if missing."""
    if not USERS_DB_PATH.exists():
        db = {"users": {}, "meta": {"total_users": 0, "total_predictions": 0,
                                     "app_version": "6.0",
                                     "last_updated": datetime.now().isoformat()}}
        save_users_db(db)
        return db
    with open(USERS_DB_PATH, "r") as f:
        return json.load(f)

def save_users_db(db: dict):
    """Persist users DB to JSON file atomically."""
    db["meta"]["last_updated"] = datetime.now().isoformat()
    with open(USERS_DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

def hash_password(password: str) -> str:
    """SHA-256 hash. In production, use bcrypt."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def username_exists(db: dict, username: str) -> bool:
    return any(u["username"].lower() == username.lower()
               for u in db["users"].values())

def email_exists(db: dict, email: str) -> bool:
    return any(u["email"].lower() == email.lower()
               for u in db["users"].values())

def get_user_by_username(db: dict, username: str) -> dict | None:
    for u in db["users"].values():
        if u["username"].lower() == username.lower():
            return u
    return None

AVATAR_COLORS = ["#e85d04","#4895ef","#52b788","#9b5de5","#f48c06","#ff6b6b"]

def create_user(db: dict, username: str, email: str, password: str,
                full_name: str) -> dict:
    """Create a new user, save to DB, return user dict."""
    uid = str(uuid.uuid4())
    user = {
        "user_id": uid, "username": username, "email": email,
        "password_hash": hash_password(password), "full_name": full_name,
        "role": "admin" if len(db["users"]) == 0 else "user",
        "avatar_color": AVATAR_COLORS[len(db["users"]) % len(AVATAR_COLORS)],
        "created_at": datetime.now().isoformat(),
        "last_login": datetime.now().isoformat(),
        "login_count": 1,
        "preferences": {"default_model": "xgboost",
                        "confidence_interval": "±15%",
                        "expert_mode": False,
                        "theme_accent": "#e85d04"},
        "prediction_history": [],
        "saved_comparisons": [],
        "page_visits": {}
    }
    db["users"][uid] = user
    db["meta"]["total_users"] = len(db["users"])
    save_users_db(db)
    return user

def login_user(db: dict, username: str, password: str) -> tuple[bool, str, dict]:
    """
    Returns (success: bool, message: str, user: dict | {})
    """
    user = get_user_by_username(db, username)
    if not user:
        return False, "Username not found.", {}
    if not verify_password(password, user["password_hash"]):
        return False, "Incorrect password.", {}
    user["last_login"] = datetime.now().isoformat()
    user["login_count"] = user.get("login_count", 0) + 1
    db["users"][user["user_id"]] = user
    save_users_db(db)
    return True, "Login successful!", user

def save_prediction_to_history(user_id: str, prediction: dict):
    """Append a prediction record to user's history and save."""
    db = load_users_db()
    if user_id in db["users"]:
        db["users"][user_id]["prediction_history"].append(prediction)
        db["meta"]["total_predictions"] += 1
        save_users_db(db)

def update_user_preferences(user_id: str, prefs: dict):
    db = load_users_db()
    if user_id in db["users"]:
        db["users"][user_id]["preferences"].update(prefs)
        save_users_db(db)

def track_page_visit(user_id: str, page_name: str):
    db = load_users_db()
    if user_id in db["users"]:
        visits = db["users"][user_id].get("page_visits", {})
        visits[page_name] = visits.get(page_name, 0) + 1
        db["users"][user_id]["page_visits"] = visits
        save_users_db(db)

def save_comparison(user_id: str, name: str, car_a: dict, car_b: dict):
    db = load_users_db()
    if user_id in db["users"]:
        comp = {"comparison_id": str(uuid.uuid4()), "name": name,
                "car_a": car_a, "car_b": car_b,
                "created_at": datetime.now().isoformat()}
        db["users"][user_id]["saved_comparisons"].append(comp)
        save_users_db(db)

def delete_user(user_id: str):
    db = load_users_db()
    if user_id in db["users"]:
        del db["users"][user_id]
        db["meta"]["total_users"] = len(db["users"])
        save_users_db(db)

def update_user_profile(user_id: str, full_name: str, email: str,
                        avatar_color: str):
    db = load_users_db()
    if user_id in db["users"]:
        db["users"][user_id]["full_name"] = full_name
        db["users"][user_id]["email"] = email
        db["users"][user_id]["avatar_color"] = avatar_color
        save_users_db(db)
```

---

### 0.3 — Auth Session State Keys

Initialize ALL of these in `main()` before anything else:

```python
defaults = {
    "authenticated": False,
    "user": {},                    # full user dict from DB
    "auth_page": "login",          # "login" | "signup" | "forgot"
    "session_id": str(uuid.uuid4()),
    "current_page": "Dashboard",
    "last_model": "xgboost",
    "last_prediction_inputs": {},
    "last_prediction_result": None,
    "global_company_filter": [],
    "global_fuel_filter": [],
    "global_year_range": (2000, 2024),
    "expert_mode": False,
    "comparison_car_a": None,
    "comparison_car_b": None,
    "page_visits": {},             # local session tracker
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
```

---

### 0.4 — Auth UI Pages

#### LOGIN PAGE (`render_login_page()`)

Full-page centered layout. NO sidebar. Use `st.columns([1,2,1])` center column.

Visual design:
- Large animated "🚗 AutoIntel" logo at top center with gradient text
- Tagline: "Your AI-powered used car intelligence platform"
- Glass-morphism card: `background: rgba(20,25,40,0.9)`, `border: 1px solid rgba(232,93,4,0.3)`, `border-radius: 16px`, `padding: 2.5rem`
- Form fields styled dark with orange focus ring
- Login button: full-width gradient orange pill
- Below button: "Don't have an account? → Sign Up" and "Forgot password?" links
- These links change `st.session_state.auth_page` to `"signup"` or `"forgot"`
- At very bottom: demo credentials hint in a subtle muted box:
  `💡 Demo: username = demo | password = demo123`
- Create the demo user automatically if it doesn't exist in users_db.json

Form fields:
- Username (text_input, placeholder="Enter your username")
- Password (text_input, type="password", placeholder="Enter your password")
- "Remember me" checkbox (visual only — session lasts until browser close)
- Submit via button OR Enter key (use `on_click` pattern with form)

Validation:
- Empty field check → red inline warning
- Wrong credentials → red animated banner: "❌ Invalid username or password"
- After 5 failed attempts → show CAPTCHA hint: "Too many attempts. Try after 30s"
  (implement with `time.time()` in session_state, no actual lockout needed — just UI)

On success:
- Update session_state.authenticated = True
- Update session_state.user = user dict
- Show brief success toast: st.toast("Welcome back, {name}! 🚗", icon="✅")
- Immediately re-render the main app

---

#### SIGNUP PAGE (`render_signup_page()`)

Same centered card layout as login.

Form fields:
1. Full Name (text_input, placeholder="John Doe")
2. Username (text_input, placeholder="johndoe" — no spaces, lowercase enforced)
3. Email (text_input, placeholder="john@example.com")
4. Password (text_input, type="password")
5. Confirm Password (text_input, type="password")
6. "I agree to terms" checkbox (must be checked)
7. "Create Account" button (full-width gradient orange)

Real-time validation (check on each field change using session_state):
- Username: min 3 chars, alphanumeric + underscore only, show ✅/❌ icon inline
- Email: basic format check (contains @ and .)
- Password: strength meter (weak/medium/strong) based on length + complexity
  → Show as colored progress bar: red=weak, yellow=medium, green=strong
  → Rules: <6 chars = weak, 6-10 = medium, >10 with mixed case/digit = strong
- Confirm password: match indicator ✅/❌
- All errors shown as inline red text below the relevant field, NOT as st.error

Password strength bar HTML (inject via st.markdown):
```html
<div class="pwd-strength">
  <div class="pwd-bar" style="width:{pct}%; background:{color}"></div>
</div>
<p style="color:{color}; font-size:0.75rem">{label}</p>
```

On success:
- Call `create_user()`, auto-login, set session state
- Show confetti animation via st.balloons()
- Welcome toast: "🎉 Account created! Welcome, {name}!"
- First-time users land on a brief "Welcome Tour" modal (3-step overlay)

Welcome Tour Modal (use st.markdown + HTML overlay):
- Step 1: "👋 Welcome to AutoIntel! Here's what you can do..."
- Step 2: "🔮 Predict car prices with AI in seconds"
- Step 3: "📊 Explore market intelligence and trends"
- "Get Started →" button closes modal

---

#### FORGOT PASSWORD PAGE (`render_forgot_password_page()`)

Simplified page:
- Email input field
- "Send Reset Link" button
- On submit: check if email exists → show: "✅ If that email exists, a reset link was sent"
  (no actual email sending needed — this is a portfolio project, just show the message)
- "Back to Login" link

---

### 0.5 — Auth Gate Logic in `main()`

```python
def main():
    # 1. Initialize session state
    init_session_state()

    # 2. Inject global CSS
    inject_css()

    # 3. Auth gate
    if not st.session_state.authenticated:
        page = st.session_state.get("auth_page", "login")
        if page == "signup":
            render_signup_page()
        elif page == "forgot":
            render_forgot_password_page()
        else:
            render_login_page()
        st.stop()  # CRITICAL: stop execution here if not authenticated

    # 4. Track page visit
    track_page_visit(st.session_state.user["user_id"],
                     st.session_state.current_page)

    # 5. Render sidebar + selected page
    render_sidebar()
    render_current_page()
```

---

### 0.6 — User Profile Page (PAGE 9 — 👤 My Profile)

Add a 9th page to the sidebar navigation: "👤 My Profile"

Layout: `st.columns([1, 2])` — left = profile card, right = settings tabs

**LEFT — Profile Card:**
- Large colored circle avatar showing user's initials (use HTML):
  ```html
  <div class="avatar-circle" style="background:{color}">
    <span>{initials}</span>
  </div>
  ```
- Full name (large), username (muted), email
- Role badge: gold "👑 Admin" or silver "👤 User"
- Member since date
- Login count + last login
- "Total Predictions Made: {n}"
- "Most visited page: {page}"

**RIGHT — Settings Tabs (use st.tabs):**

Tab A — ✏️ Edit Profile:
- Full Name input (pre-filled)
- Email input (pre-filled)
- Avatar color picker (6 preset swatches as clickable colored buttons)
- "Save Changes" button → calls `update_user_profile()` → st.success toast

Tab B — 🔐 Change Password:
- Current password input
- New password input + strength meter
- Confirm new password
- "Update Password" button → verify current → update hash → save
- On success: st.success + re-login prompt

Tab C — ⚙️ Preferences:
- Default prediction model selector
- Confidence interval preference
- Expert Mode toggle (synced to sidebar toggle)
- Theme accent color picker (changes primary orange accent across app)
- "Save Preferences" button → calls `update_user_preferences()`

Tab D — 📜 Prediction History:
- Show full prediction_history as a styled dataframe
  Columns: Date, Car, Year, Fuel, KMs, Model Used, Predicted Price
- Sort by date descending
- "Clear History" button (with confirmation: `st.checkbox("Confirm clear")`)
- "Download History as CSV" button
- Mini chart: predictions over time (line chart of dates vs predicted prices)

Tab E — 💾 Saved Comparisons:
- List all saved_comparisons as expandable cards
- Each card shows: comparison name, date, Car A vs Car B summary
- "Delete" button per comparison
- "Re-run comparison" button → navigates to Page 6 with pre-filled inputs

Tab F — 🗑️ Danger Zone (only shown to admin or self):
- "Delete My Account" button with red styling
- Requires typing username to confirm
- On confirm: calls `delete_user()`, clears session, redirects to login

---

### 0.7 — Admin Panel (shown only to role="admin")

Add "🛡️ Admin Panel" as the LAST sidebar item, visible ONLY if
`st.session_state.user.get("role") == "admin"`.

Layout: Full-width with tabs:

Tab A — 👥 All Users:
- Table: username, email, full_name, role, created_at, login_count,
         prediction_count, last_login
- Color rows: admin=gold tint, user=normal
- Per-row actions: "View Profile" (expander) + "Delete User" (red button)
- "Export Users CSV" button
- Total users KPI card at top

Tab B — 📊 Usage Analytics:
- Total predictions made (across all users)
- Most active user
- Most used model (bar chart: model name vs count of times used)
- Predictions per day (line chart, last 30 days)
- Page visit heatmap: user × page grid (cell = visit count)

Tab C — 🔧 App Settings (cosmetic):
- App version display
- DB path display
- "Backup DB" button → downloads users_db.json as file
- "Clear all prediction histories" button (admin only, with confirmation)

---

════════════════════════════════════
SECTION 1 — CONTEXT: PROJECT FACTS
════════════════════════════════════

Dataset: 11,149 Indian used car listings (Cleaned_Car_data.csv)
Columns: name, company, year, Price, kms_driven, fuel_type
Preprocessing: log1p(Price), StandardScaler, one-hot encoding → 39 features
Models trained & saved in ml_ready/models/:
  • gradient_boosting.pkl  (R²=0.7373, RMSE=₹2.62L, lr=0.05, depth=5, n_est=200)
  • xgboost.pkl            (R²=0.7463, RMSE=₹2.57L, lr=0.1, depth=3, n_est=300)
  • random_forest.pkl      (R²=0.5850, RMSE=₹3.29L, depth=15, n_est=300)
  • linear_regression.pkl  (R²=0.7654 — best overall)
  • ridge.pkl              (R²=0.7605)
Saved artifacts:
  ml_ready/preprocessor.pkl, X_train.npy, X_test.npy, y_train.npy, y_test.npy,
  y_train_original.npy, y_test_original.npy, feature_names.npy
Report assets: report_output/images/ (14 charts, used as fallback images)

DEMO MODE: If ml_ready/ directory does not exist, generate all synthetic data
inline using numpy/pandas with fixed random seed (42). ALL pages must work
in demo mode with clearly visible "⚠️ Demo Mode — No ML files detected" banner.

---

════════════════════════════════════
SECTION 2 — VISUAL DESIGN SYSTEM
════════════════════════════════════

Theme: Dark mode
Base background: #0c0f14
Surface: #131720
Card surface: rgba(20, 25, 40, 0.85)
Sidebar: #0a0d12

Accent palette:
  Primary: Flame orange #e85d04
  Warm:    Amber         #f48c06
  Success: Teal          #52b788
  Info:    Blue          #4895ef
  Purple:  #9b5de5
  Danger:  #ef233c

Text: #e8eaf0 (primary), #9da3b4 (muted), #ffffff (headings)

Typography:
  Body: DM Sans (Google Fonts)
  Headings: Syne Bold (Google Fonts)
  Import via st.markdown at top of inject_css()

### Full CSS Block (inject via st.markdown unsafe_allow_html=True)

The CSS must cover ALL of the following — write complete declarations:

```css
/* Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Syne:wght@700;800&display=swap');

/* Global reset + base */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  background-color: #0c0f14;
  color: #e8eaf0;
}

/* Hide Streamlit default chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Custom scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0c0f14; }
::-webkit-scrollbar-thumb { background: #e85d04; border-radius: 3px; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: #0a0d12 !important;
  border-right: 1px solid rgba(232,93,4,0.15);
}

/* Glass card */
.glass-card {
  background: rgba(20, 25, 40, 0.85);
  border: 1px solid rgba(232,93,4,0.2);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  transition: box-shadow 0.3s ease, transform 0.2s ease;
}
.glass-card:hover {
  box-shadow: 0 0 20px rgba(232,93,4,0.15);
  transform: translateY(-2px);
}

/* KPI metric */
.kpi-card {
  background: rgba(20,25,40,0.9);
  border: 1px solid rgba(232,93,4,0.25);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  text-align: center;
}
.kpi-value {
  font-family: 'Syne', sans-serif;
  font-size: 2rem;
  font-weight: 800;
  color: #e85d04;
}
.kpi-label {
  font-size: 0.8rem;
  color: #9da3b4;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* Gradient hero header */
.hero-header {
  background: linear-gradient(135deg, #0c0f14 0%, #1a1f35 50%, #0f1520 100%);
  border: 1px solid rgba(232,93,4,0.2);
  border-radius: 16px;
  padding: 2.5rem;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.hero-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 50%, rgba(232,93,4,0.08) 0%, transparent 60%),
              radial-gradient(circle at 70% 50%, rgba(72,149,239,0.06) 0%, transparent 60%);
  animation: pulse 8s ease-in-out infinite alternate;
}
@keyframes pulse {
  from { transform: scale(1); }
  to   { transform: scale(1.05); }
}
.hero-title {
  font-family: 'Syne', sans-serif;
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(90deg, #e85d04, #f48c06, #4895ef);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Gradient orange button */
.orange-btn {
  background: linear-gradient(135deg, #e85d04, #f48c06);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 0.6rem 2rem;
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.orange-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(232,93,4,0.4);
}

/* Badge classes */
.badge-luxury  { background: rgba(155,93,229,0.2); color:#9b5de5; border:1px solid #9b5de5; border-radius:20px; padding:2px 10px; font-size:0.75rem; }
.badge-premium { background: rgba(232,93,4,0.2);   color:#e85d04; border:1px solid #e85d04; border-radius:20px; padding:2px 10px; font-size:0.75rem; }
.badge-mid     { background: rgba(72,149,239,0.2);  color:#4895ef; border:1px solid #4895ef; border-radius:20px; padding:2px 10px; font-size:0.75rem; }
.badge-budget  { background: rgba(82,183,136,0.2);  color:#52b788; border:1px solid #52b788; border-radius:20px; padding:2px 10px; font-size:0.75rem; }

/* Auth card */
.auth-card {
  background: rgba(20,25,40,0.95);
  border: 1px solid rgba(232,93,4,0.3);
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(232,93,4,0.08);
}

/* Avatar circle */
.avatar-circle {
  width: 80px; height: 80px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Syne', sans-serif;
  font-size: 1.8rem; font-weight: 800;
  color: white;
  margin: 0 auto 1rem;
  box-shadow: 0 0 20px rgba(232,93,4,0.3);
}

/* Animated shimmer for price reveal */
@keyframes shimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}
.price-reveal {
  font-family: 'Syne', sans-serif;
  font-size: 3.5rem;
  font-weight: 800;
  background: linear-gradient(90deg, #e85d04 0%, #f48c06 30%, #ffffff 50%, #f48c06 70%, #e85d04 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 2s linear infinite;
}

/* Password strength bar */
.pwd-strength { background: rgba(255,255,255,0.1); border-radius: 4px; height: 6px; margin: 4px 0; overflow: hidden; }
.pwd-bar { height: 100%; border-radius: 4px; transition: width 0.3s ease, background 0.3s ease; }

/* Sidebar nav active */
.nav-active {
  border-left: 3px solid #e85d04;
  background: rgba(232,93,4,0.1);
  border-radius: 0 8px 8px 0;
}

/* Progress bar gradient */
[data-testid="stProgress"] > div > div {
  background: linear-gradient(90deg, #e85d04, #f48c06) !important;
}

/* Streamlit metric overrides */
[data-testid="metric-container"] {
  background: rgba(20,25,40,0.85);
  border: 1px solid rgba(232,93,4,0.2);
  border-radius: 12px;
  padding: 1rem;
}
[data-testid="stMetricValue"] {
  font-family: 'Syne', sans-serif;
  color: #e85d04 !important;
  font-size: 1.8rem !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(10,13,18,0.8);
  border-bottom: 1px solid rgba(232,93,4,0.2);
}
.stTabs [data-baseweb="tab"] {
  color: #9da3b4;
}
.stTabs [aria-selected="true"] {
  color: #e85d04 !important;
  border-bottom: 2px solid #e85d04 !important;
}

/* Input fields */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stMultiSelect > div > div {
  background: rgba(20,25,40,0.9) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  color: #e8eaf0 !important;
  border-radius: 8px !important;
}
.stTextInput > div > div > input:focus {
  border-color: #e85d04 !important;
  box-shadow: 0 0 0 1px rgba(232,93,4,0.3) !important;
}

/* Table */
.stDataFrame { border: 1px solid rgba(255,255,255,0.08) !important; }
```

---

════════════════════════════════════
SECTION 3 — SIDEBAR DESIGN
════════════════════════════════════

`render_sidebar()` must:

1. At top: display user avatar circle (HTML) + "Hi, {first_name}!" greeting
   below it in small muted text: "{role} · {login_count} logins"

2. App logo: "🚗 AutoIntel" in Syne font, gradient orange text, bold

3. Gradient divider (st.markdown `<hr style="border:1px solid rgba(232,93,4,0.2)">`)

4. Navigation buttons — ONE per page, all 9 pages + Admin (if admin):
   Use `st.button()` for each with full-width and custom key.
   On click: update `st.session_state.current_page` and `st.rerun()`
   Show active page with left orange border (via custom CSS class toggle)
   Pages:
   ```
   🏠 Dashboard
   📊 Dataset Explorer
   🔍 EDA Deep-Dive
   🤖 Model Lab
   🧪 Residual Analysis
   🔮 Price Predictor
   📈 Market Intelligence
   ⚙️ Pipeline Inspector
   👤 My Profile
   🛡️ Admin Panel  ← only if admin
   ```

5. Collapsible "⚡ Quick Stats" section (st.expander):
   - Total Records: 11,149
   - Models Loaded: 5 (or "Demo Mode")
   - Your Predictions: {len(user.prediction_history)}
   - App Version: 6.0

6. Collapsible "🎛️ Global Filters" section (st.expander):
   - Company multiselect (persist in session_state.global_company_filter)
   - Fuel type multiselect (persist in session_state.global_fuel_filter)
   - "Apply" button → st.rerun()
   - "Reset" button → clears filters

7. Expert Mode toggle (st.toggle):
   - Synced with session_state.expert_mode
   - When ON: shows a subtle orange indicator badge "⚡ Expert"
   - Persists preferences to user DB on change

8. Bottom section:
   ```
   ─────────────────────────────
   📅 Data processed: Jun 2024
   🧠 Trained on: 8,919 samples
   ─────────────────────────────
   Built with ❤️ using Streamlit
   v6.0 · MIT License
   ─────────────────────────────
   [🚪 Logout] button (full-width, dark red border)
   ```
   Logout button: clears session_state.authenticated, user, resets all state,
   calls st.rerun()

---

════════════════════════════════════
SECTION 4 — PAGE IMPLEMENTATIONS
════════════════════════════════════

### BUG-FIX REQUIREMENTS (apply across ALL pages)
These bugs commonly occur in Streamlit ML apps — fix proactively:

1. **Pickle loading**: Wrap ALL pkl loads in try/except. If file missing → demo mode.
2. **NumPy version mismatch**: When loading .npy files, use `allow_pickle=False`
   for arrays and `allow_pickle=True` only for object arrays. Catch ValueError.
3. **Feature mismatch**: Before calling `model.predict(X)`, assert
   `X.shape[1] == expected_features`. If mismatch → show error + skip prediction.
4. **Log-space inversion**: ALWAYS apply `np.expm1()` after prediction to convert
   from log1p space back to original price. Never forget this.
5. **Preprocessor transform**: Pass input through `preprocessor.transform()` BEFORE
   predicting. Catch ValueError with helpful message.
6. **Plotly empty data**: Before creating any chart, check `len(df) > 0`.
   If empty → show `st.info("No data matches current filters")` instead of crashing.
7. **Session state key errors**: Always use `.get()` with defaults, never direct `[]`
   on session_state for optional keys.
8. **DataFrame column access**: Use `.get()` equivalent — check `col in df.columns`
   before accessing. Never assume column exists.
9. **Integer overflow in price display**: Use `int()` not numpy int types for
   f-string formatting of prices.
10. **Rerun loops**: Never call `st.rerun()` inside a conditional that will always
    be true. Always set a flag first, then rerun.

---

### PAGE 1 — 🏠 Dashboard Home

`render_dashboard()`

Section A — Hero Banner:
```html
<div class="hero-header">
  <div class="hero-title">🚗 AutoIntel</div>
  <p style="color:#9da3b4; font-size:1.1rem">
    Used Car Price Intelligence · AI-Powered · Indian Market
  </p>
  <div style="display:flex; gap:1rem; justify-content:center; margin-top:1rem">
    <span class="badge-luxury">v6.0</span>
    <span class="badge-mid">5 ML Models</span>
    <span class="badge-premium">11,149 Records</span>
  </div>
</div>
```
Render via `st.markdown(..., unsafe_allow_html=True)`

Section B — 5 KPI Cards (st.columns(5)):
Use `st.components.v1.html()` to inject animated counter JS for each KPI.
The JS animation: count from 0 to final value over 1.5 seconds using
`requestAnimationFrame`. Each KPI in a `.kpi-card` div.

KPIs:
1. Total Records → 11,149
2. Cleaned Records → 9,014
3. Best R² → 0.7654 (LinearReg) — color: teal
4. Price Range → ₹20K–₹1Cr
5. Features → 39

Section C — 3 Insight Cards (st.columns(3)):
- Card 1: "📈 Log Transform Boost"
  Body: "Raw price R²: 0.66 → Log-transformed R²: 0.77 (+16.7% improvement)"
  Color accent: orange
- Card 2: "🏆 Top Predictor"
  Body: "car_age is the strongest predictor. Feature importance: 0.42 (XGBoost)"
  Color accent: teal
- Card 3: "💎 Luxury Premium"
  Body: "Luxury brands fetch 8× higher prices vs. economy segment (₹85L vs ₹10L)"
  Color accent: purple

Each card as `.glass-card` with colored left border.

Section D — Project Pipeline Timeline:
Horizontal scrollable div showing 8 pipeline stages as connected boxes:
```
[Raw CSV] → [Dedup] → [Feature Eng.] → [Log Transform] → [Scale] → [Train/Test] → [GridSearch] → [Deploy]
```
Use st.markdown with HTML. Each stage box: rounded, dark bg, orange border on
hover. Animate the connecting arrows with a CSS animation.

Section E — Quick Predict Widget (st.expander "⚡ Quick Predict"):
- Company selectbox (top 10 companies)
- Year slider (2010–2024)
- Kms driven number input
- Fuel type radio
- "Predict" button → uses default model (xgboost or first available)
- Shows predicted price inline below in large orange font
- On predict → also saves to session_state.last_prediction_result
- "Full Predictor →" link to navigate to Page 6

Section F — Recent Activity (if user has prediction history):
- st.subheader "🕐 Your Recent Predictions"
- Show last 3 predictions as compact cards (company, year, price, model used)
- "View All →" link to profile page prediction history tab

---

### PAGE 2 — 📊 Dataset Explorer

`render_dataset_explorer()`

Load data: `@st.cache_data(show_spinner="Loading dataset...")` on CSV load.
Apply global filters from session_state if set.

Sub-section A — Sidebar Filter Panel:
Use a `with st.sidebar:` block inside this page to render page-specific filters:
(Note: this APPENDS to the sidebar below the navigation)
- Company multiselect (sorted alphabetically, pre-select global filter if set)
- Fuel type multiselect: ["Petrol", "Diesel", "CNG", "Electric", "LPG"]
- Year range slider (min=dataset_min, max=dataset_max)
- Price range slider (₹0 to ₹max, step=50000, format="{:,}")
- Kms driven range slider (0 to 300000)
- "🔀 Surprise Me!" button: pick random filter combo, apply, rerun
- "Reset Filters" button

Sub-section B — Live Row Count Banner:
```python
st.markdown(f"""
<div class="glass-card" style="text-align:center; padding:0.75rem">
  <span style="font-size:1.1rem; color:#e85d04; font-weight:700">
    {len(filtered_df):,}
  </span>
  <span style="color:#9da3b4"> of {len(df):,} records match your filters</span>
</div>
""", unsafe_allow_html=True)
```

Sub-section C — Interactive Table (st.dataframe with column_config):
```python
st.dataframe(
    filtered_df,
    column_config={
        "Price": st.column_config.ProgressColumn(
            "Price (₹)", format="₹{:,.0f}",
            min_value=0, max_value=int(df["Price"].max())
        ),
        "kms_driven": st.column_config.NumberColumn(
            "KMs Driven", format="%d km"
        ),
        "company": st.column_config.TextColumn("Brand"),
        "year": st.column_config.NumberColumn("Year", format="%d"),
        "fuel_type": st.column_config.SelectboxColumn(
            "Fuel", options=["Petrol","Diesel","CNG","Electric","LPG"]
        ),
    },
    use_container_width=True,
    height=400,
    hide_index=True,
)
```

Sub-section D — 3 Dynamic Mini-Charts (st.columns(3)):
All charts filtered by current filter state, all use Plotly dark template.

Chart 1: Price Distribution Histogram
  - go.Histogram, nbinsx=30, color=#e85d04, opacity=0.8
  - x-axis: Price in ₹, y-axis: Count
  - Title: f"Price Distribution ({len(filtered_df):,} cars)"

Chart 2: Fuel Type Donut
  - go.Pie, hole=0.55, colors=[#e85d04, #4895ef, #52b788, #9b5de5, #f48c06]
  - Labels: fuel types, values: counts
  - Show count + % in legend

Chart 3: Year Distribution Bar
  - go.Bar, year on x, count on y, color scale orange→blue by year
  - Title: "Cars by Manufacturing Year"

Sub-section E — Actions:
```python
col1, col2 = st.columns(2)
with col1:
    csv_bytes = filtered_df.to_csv(index=False).encode()
    st.download_button("📥 Download Filtered Data", csv_bytes,
                       "filtered_cars.csv", "text/csv")
with col2:
    if st.button("🔀 Surprise Me!"):
        # pick random company, random fuel, random year range
        st.session_state["surprise_applied"] = True
        st.rerun()
```

---

### PAGE 3 — 🔍 EDA Deep-Dive

`render_eda()`

Use `st.tabs(["💰 Price Analysis", "🏢 Brand Intelligence",
              "🔗 Correlations", "📉 Outliers", "📅 Year & Mileage"])`

**Tab A — Price Analysis:**

Row 1: Side-by-side histograms (st.columns(2)):
- Left: Raw price histogram, skewness annotation:
  ```python
  from scipy.stats import skew
  raw_skew = skew(df["Price"].dropna())
  # Add annotation: f"Skewness: {raw_skew:.2f}"
  ```
  Use go.Histogram + fig.add_annotation for skewness label
- Right: Log-transformed price histogram with skewness annotation
  Log prices = np.log1p(df["Price"])
  Annotate: "After log1p transform: skewness ≈ -0.12"
  Both: color=#e85d04, template=plotly_dark

Row 2: Price Percentile Explorer:
  st.slider("Explore Percentile", 10, 99, 50, key="pct_slider")
  Compute np.percentile(df["Price"], pct_val)
  Show in glass card:
  ```
  P{pct}: ₹{value:,.0f}
  "At this percentile, you could buy: {suggested_car_type}"
  ```
  suggested_car_type logic:
  - <2L: "Budget hatchback (Maruti Alto, Hyundai Eon)"
  - 2-5L: "Mid-range hatchback (Swift, i20)"
  - 5-10L: "Premium sedan / SUV (Creta, City)"
  - >10L: "Luxury vehicle (BMW, Mercedes)"

**Tab B — Brand Intelligence:**

Chart 1: Top 20 Companies by Median Price (horizontal bar):
- Compute median price per company, sort descending, take top 20
- Color bars by tier: >15L=luxury(#9b5de5), 7-15L=premium(#e85d04),
  3-7L=mid(#4895ef), <3L=budget(#52b788)
- go.Bar with orientation='h', sorted ascending (plotly shows top at top)
- Add median price labels on bars

Chart 2: Brand Bubble Chart:
- x=avg_price, y=count, size=count, color=tier
- go.Scatter with mode='markers', marker=dict(size=..., color=..., opacity=0.8)
- Add text labels for top 10 brands by count
- Hover: brand name, avg price, total listings

Chart 3: Brand Comparison Box Plots:
- st.multiselect("Select brands to compare", companies, default=top3)
- For selected brands, go.Box per brand, overlaid on one figure
- colors: cycle through [#e85d04, #4895ef, #52b788, #9b5de5, #f48c06]
- violinmode='overlay' for density view toggle (st.checkbox)

**Tab C — Feature Correlations:**

Chart 1: Correlation Heatmap:
- Compute: df[["Price","year","kms_driven","car_age"]].corr()
- go.Heatmap with colorscale=[[0,"#4895ef"],[0.5,"#131720"],[1,"#e85d04"]]
- zmin=-1, zmax=1, texttemplate="%{z:.2f}", textfont_size=12
- Title: "Feature Correlation Matrix"

Chart 2: Scatter Matrix:
- go.Splom (scatter plot matrix) for Price, car_age, kms_driven
- Color by fuel_type: map to colors dict
- dimensions=[price, car_age, kms_driven]
- marker=dict(size=3, opacity=0.5)
- Limit to 2000 random samples (performance)

Chart 3: VIF Table:
- Compute manually:
  ```python
  from numpy.linalg import inv
  # simplified VIF = 1/(1 - R²) for each feature vs others
  # or use statsmodels if available, else approximate
  ```
- Display as st.dataframe with color coding: VIF>10=red, 5-10=yellow, <5=green
  Use st.dataframe with background color via pandas Styler

**Tab D — Outlier Analysis:**

Chart 1: IQR Outlier Count Table:
- For each numeric column: compute Q1, Q3, IQR, count of outliers
- Display as styled table with outlier count colored red if >5% of data

Chart 2: Before/After kms_driven Scatter:
- st.columns(2): left=raw scatter, right=capped at P99
- go.Scatter: x=kms_driven, y=Price, mode='markers', marker=dict(size=3, opacity=0.5)
- Highlight outlier points in red (beyond P99)
- Caption: "After capping kms_driven at 99th percentile (P99 = {val:,} km)"

Chart 3: Box Plots per Feature with Outliers:
- st.selectbox to pick feature: [Price, kms_driven, year]
- go.Box with boxpoints='outliers', marker_color='#ef233c' for outliers
- Main box color: #e85d04

**Tab E — Year & Mileage Trends:**

Chart 1: Median Price by Year (Animated Line Chart):
- Compute median_by_year = df.groupby("year")["Price"].median().reset_index()
- Use go.Scatter with mode='lines+markers'
- Add play animation via Plotly frames:
  ```python
  frames = [go.Frame(data=[go.Scatter(x=median_by_year["year"][:k],
                                       y=median_by_year["Price"][:k])],
                     name=str(k)) for k in range(1, len(median_by_year)+1)]
  fig.frames = frames
  fig.update_layout(updatemenus=[dict(type="buttons",
    buttons=[dict(label="▶ Play", method="animate",
                  args=[None, {"frame":{"duration":200},"fromcurrent":True}])])])
  ```
- Line color: #e85d04, markers: #f48c06, size=8

Chart 2: Hexbin-Style KMs vs Price (2D Histogram Heatmap):
- go.Histogram2dContour or go.Histogram2d
- x=kms_driven, y=Price (both log-scaled for readability)
- colorscale from dark navy to orange
- Title: "Density: KMs Driven vs Price"
- Limit to 5000 samples

---

### PAGE 4 — 🤖 Model Comparison Lab

`render_model_lab()`

Model metrics dict (hardcoded from your training results — use these exact values):
```python
MODEL_METRICS = {
    "Linear Regression": {"r2":0.7654,"rmse":245000,"mae":168000,"train_time":0.3,"params":"None"},
    "Ridge Regression":  {"r2":0.7605,"rmse":249000,"mae":171000,"train_time":0.4,"params":"alpha=1.0"},
    "XGBoost":           {"r2":0.7463,"rmse":257000,"mae":175000,"train_time":12.5,"params":"lr=0.1,depth=3,n=300"},
    "Gradient Boosting": {"r2":0.7373,"rmse":262000,"mae":179000,"train_time":18.2,"params":"lr=0.05,depth=5,n=200"},
    "Random Forest":     {"r2":0.5850,"rmse":329000,"mae":221000,"train_time":22.1,"params":"depth=15,n=300"},
}
```

Section A — Summary Table:
- pd.DataFrame from MODEL_METRICS, styled with:
  - R² column: color green if >0.75, yellow 0.6-0.75, red <0.6
  - RMSE: format as "₹{v/100000:.2f}L"
  - Highlight best row (Linear Regression) with gold border
- st.dataframe with column_config for each column

Section B — Visual Comparisons (st.tabs):

Tab "R² Comparison":
  go.Bar: model names on x, R² on y
  Color bars: linear/ridge=teal(#52b788), xgb/gb=orange(#e85d04), rf=gray(#9da3b4)
  Add horizontal reference line at R²=0.75 (dashed, color=#f48c06)
  Annotate each bar with R² value

Tab "RMSE / MAE":
  Grouped go.Bar (two trace groups)
  Trace 1: RMSE, color=#e85d04
  Trace 2: MAE, color=#4895ef
  barmode='group', y-axis: "₹ (Indian Rupees)"

Tab "Speed vs Accuracy":
  go.Scatter: x=train_time, y=R², mode='markers+text'
  marker=dict(size=15, color=[...colors by model...])
  text=[model names], textposition='top center'
  Add quadrant annotations: "Fast & Accurate" (top-left), etc.

Tab "Radar Chart":
  go.Scatterpolar for each model with 5 dimensions:
  [R²_score(0-10), Speed(10-train_time), RMSE_score(10-rmse_rank),
   Interpretability(manual), Stability(manual)]
  Use polar area chart with opacity=0.3 fills
  Legend shows all 5 models

Section C — Log Transform Impact:
- st.columns(2): show Linear Regression before (R²=0.66) vs after (R²=0.77)
- Animate R² improvement with progress bars
- Show price distribution skewness: before=5.64, after=-0.12

Section D — Hyperparameter Tuning:
- Table: model, param_grid tested, best_params, before_r2, after_r2, delta
- Color delta column: green if positive, red if negative
- Improvement call-outs in glass cards:
  "+0.0104 R² from tuning XGBoost"

Section E — Model Recommendation Engine:
- st.radio or pill buttons: "What matters most to you?"
  Options: [🎯 Best Accuracy, ⚡ Fastest Prediction, 📖 Explainability,
            ⚖️ Balanced, 🔬 Research/Full Analysis]
- Based on choice, highlight recommended model with styled card:
  ```
  ✅ Recommended: Linear Regression
  Reason: Highest R² (0.7654), fastest inference, most interpretable
  ```

---

### PAGE 5 — 🧪 Residual Analysis

`render_residual_analysis()`

Model selector: `st.selectbox("Select Model", list(MODEL_METRICS.keys()))`

Load the selected model and compute predictions on X_test.
Apply np.expm1() to both y_pred and y_test for original scale.
residuals = y_test_orig - y_pred_orig

Section A — Residual Scatter (Predicted vs Actual):
- go.Scatter: x=y_pred, y=y_test, mode='markers'
- Color points by abs(residual) using a colorscale (blue=small, red=large)
- Add diagonal line (perfect prediction): go.Scatter x=[min,max], y=[min,max],
  line=dict(color='#52b788', dash='dash')
- Axes: "Predicted Price (₹)", "Actual Price (₹)"

Section B — Residual Distribution:
- go.Histogram of residuals, color=#4895ef
- Overlay normal distribution curve: go.Scatter
- Add annotations: f"Mean: ₹{mean:,.0f}", f"Std: ₹{std:,.0f}"
- st.columns(2): histogram left, stats card right

Section C — QQ Plot:
- Compute theoretical quantiles vs sample quantiles
  ```python
  from scipy.stats import probplot
  qq_result = probplot(residuals)
  theoretical_q, sample_q = qq_result[0]
  ```
- go.Scatter: x=theoretical_q, y=sample_q, mode='markers', color=#9b5de5
- Reference line: go.Scatter for perfect normality
- Title: "Q-Q Plot: Residual Normality Check"

Section D — Top 20 Worst Predictions:
- Compute error% = abs(actual - predicted) / actual × 100
- Sort descending, show top 20
- st.dataframe with column_config:
  - error%: colored red for >50%, yellow 20-50%, green <20%
  - Show: car name, company, year, fuel, actual_price, predicted_price, error%

Section E — Error by Feature (st.columns(2)):
- Chart 1: Error vs car_age (scatter + trend line)
- Chart 2: Error vs kms_driven (scatter with trend)
- Chart 3: Error by company (bar chart, top 15 companies, mean abs error)
- Chart 4: Error by fuel_type (bar chart)

All charts: plotly dark template, limit to 2000 sample points.

Section F — Calibration Curve:
- Compute prediction intervals at ±10%, ±15%, ±20%
- For each interval width, count what % of actual prices fall within it
- go.Scatter: x=interval_widths, y=coverage_pct
- Add diagonal reference line for perfect calibration
- Interpret: "At ±20% confidence, {coverage:.1f}% of predictions are correct"

---

### PAGE 6 — 🔮 Price Predictor

`render_price_predictor()`

CRITICAL BUG FIXES for this page:
1. Never crash if preprocessor is missing — use demo mode calculation
2. Ensure feature vector matches exactly what preprocessor expects (39 features)
3. Always invert log with np.expm1()
4. Validate all inputs before predicting

Layout: st.columns([1.2, 0.8]) — inputs left, results right

**LEFT COLUMN — Input Panel:**

```python
with col_input:
    st.markdown("### 🎛️ Configure Your Car")

    company = st.selectbox("🏢 Company", sorted(df["company"].unique()))
    # Filter car names by selected company
    company_cars = df[df["company"]==company]["name"].unique()
    car_name = st.selectbox("🚗 Car Model", sorted(company_cars))

    col_year, col_kms = st.columns(2)
    with col_year:
        year = st.slider("📅 Year", 1996, 2024, 2018)
        year_input = st.number_input("", min_value=1996, max_value=2024,
                                      value=year, key="year_num")
        # Sync slider and number input via session_state
    with col_kms:
        kms = st.slider("🛣️ KMs Driven", 0, 300000, 45000, step=1000)
        st.markdown(f"<p style='color:#9da3b4; font-size:0.85rem'>"
                    f"{kms:,} km · ~{kms//15000:.0f} years avg driving</p>",
                    unsafe_allow_html=True)

    # Fuel type as pill buttons (HTML radio)
    fuel_type = st.radio("⛽ Fuel Type", ["Petrol","Diesel","CNG","LPG","Electric"],
                          horizontal=True)

    model_choice = st.selectbox("🤖 Prediction Model",
                                  list(MODEL_METRICS.keys()),
                                  index=list(MODEL_METRICS.keys()).index("XGBoost")
                                  if "XGBoost" in MODEL_METRICS else 0)

    with st.expander("⚙️ Advanced Options"):
        ci_option = st.select_slider("Confidence Interval",
                                      ["±10%","±15%","±20%"], value="±15%")
        show_similar = st.checkbox("Show similar cars from dataset", value=True)
        compare_all  = st.checkbox("Compare predictions across all models", value=False)
        show_depreciation = st.checkbox("Show 5-year depreciation curve", value=True)

    predict_btn = st.button("🔮 Predict Price", type="primary",
                             use_container_width=True)
```

Input validations (run when predict_btn is True):
- If year < 2010 and kms < 10000: st.warning("⚠️ Low KMs for an older car")
- If kms > 200000: st.warning("⚠️ High mileage — affects resale significantly")
- If year > 2022 and kms > 100000: st.warning("⚠️ Unusually high KMs for a new car")
- Compute car_age = 2024 - year; if car_age > 20: st.info("💡 Vintage car detected")

**RIGHT COLUMN — Results Panel (sticky):**

Only render if `st.session_state.last_prediction_result is not None` or after predict:

```python
with col_result:
    if predict_btn:
        with st.spinner("Computing price..."):
            result = run_prediction(company, car_name, year, kms, fuel_type,
                                     model_choice)
            st.session_state.last_prediction_result = result
            # Save to user history
            save_prediction_to_history(st.session_state.user["user_id"], {
                "timestamp": datetime.now().isoformat(),
                "company": company, "name": car_name, "year": year,
                "kms_driven": kms, "fuel_type": fuel_type,
                "model_used": model_choice,
                "predicted_price": result["price"],
                "session_id": st.session_state.session_id
            })

    if st.session_state.last_prediction_result:
        result = st.session_state.last_prediction_result
        price = result["price"]

        # Animated price display
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:2rem">
          <p style="color:#9da3b4; font-size:0.85rem; margin:0">ESTIMATED PRICE</p>
          <div class="price-reveal">₹{int(price):,}</div>
          <p style="color:#9da3b4; font-size:0.8rem">{result['price_lakh']:.2f} Lakhs</p>
        </div>
        """, unsafe_allow_html=True)

        # Price tier badge
        tier = get_price_tier(price)
        st.markdown(f'<div style="text-align:center; margin:0.5rem 0">'
                    f'<span class="badge-{tier["class"]}">{tier["label"]}</span>'
                    f'</div>', unsafe_allow_html=True)

        # Confidence range
        ci_pct = int(ci_option.replace("±","").replace("%","")) / 100
        low, high = int(price * (1 - ci_pct)), int(price * (1 + ci_pct))
        st.markdown(f"""
        <div class="glass-card">
          <p style="color:#9da3b4; font-size:0.8rem">CONFIDENCE RANGE ({ci_option})</p>
          <div style="display:flex; justify-content:space-between">
            <span style="color:#52b788">₹{low:,}</span>
            <span style="color:#e85d04; font-weight:700">₹{int(price):,}</span>
            <span style="color:#ef233c">₹{high:,}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Smart Price Explainer (Feature A)
        st.markdown("#### 💬 Why This Price?")
        car_age = 2024 - year
        explain_text = generate_price_explanation(company, car_name, year,
                                                   kms, fuel_type, price, car_age)
        st.markdown(f'<div class="glass-card"><p style="color:#9da3b4">'
                    f'{explain_text}</p></div>', unsafe_allow_html=True)

        # Deal Score Gauge (Feature B)
        deal_score = compute_deal_score(price, company, year, kms, fuel_type, df)
        render_deal_score_gauge(deal_score)

        # Depreciation curve
        if show_depreciation:
            render_depreciation_curve(price, year, company)

        # Compare all models
        if compare_all:
            render_all_model_comparison(company, car_name, year, kms, fuel_type)

        # Similar cars
        if show_similar:
            render_similar_cars(company, year, kms, fuel_type, price, df)

        # SHAP-lite waterfall (Feature D)
        render_shap_lite(company, car_name, year, kms, fuel_type, price)
```

**Helper functions for Page 6:**

```python
def get_price_tier(price: float) -> dict:
    if price >= 3000000: return {"class":"luxury",  "label":"💎 Luxury"}
    if price >= 1000000: return {"class":"premium",  "label":"⭐ Premium"}
    if price >= 400000:  return {"class":"mid",      "label":"🚗 Mid-Range"}
    return                      {"class":"budget",   "label":"💰 Budget"}

def generate_price_explanation(company, name, year, kms, fuel, price, car_age) -> str:
    """Generate natural language explanation for the predicted price."""
    parts = [f"This {year} {company} ({fuel}) is estimated at ₹{int(price):,}."]
    if car_age <= 3:
        parts.append(f"Being only {car_age} years old contributes positively (+₹{int(car_age*20000):,} impact).")
    elif car_age >= 10:
        parts.append(f"At {car_age} years, age reduces value (−₹{int(car_age*15000):,} impact).")
    if kms > 100000:
        parts.append(f"High mileage ({kms:,} km) discounts the price by approx −₹{int((kms-50000)*0.3):,}.")
    elif kms < 30000:
        parts.append(f"Low mileage ({kms:,} km) adds a premium of approx +₹{int((50000-kms)*0.3):,}.")
    if fuel == "Diesel":
        parts.append("Diesel engines command higher resale due to fuel efficiency.")
    elif fuel == "Electric":
        parts.append("Electric vehicles carry a green premium in the current market.")
    luxury_brands = ["BMW","Mercedes","Audi","Jaguar","Land Rover","Volvo"]
    if company in luxury_brands:
        parts.append(f"{company} is a luxury brand — premium pricing applies.")
    return " ".join(parts)

def compute_deal_score(price, company, year, kms, fuel_type, df) -> int:
    """Score 1-100: how good a deal is this vs similar cars."""
    similar = df[(df["company"]==company) &
                 (df["fuel_type"]==fuel_type) &
                 (abs(df["year"]-year)<=2) &
                 (abs(df["kms_driven"]-kms)<=30000)]
    if len(similar) < 3:
        similar = df[(df["company"]==company) & (df["fuel_type"]==fuel_type)]
    if len(similar) == 0:
        return 50
    market_median = similar["Price"].median()
    ratio = market_median / price if price > 0 else 1
    score = int(min(100, max(1, 50 + (ratio - 1) * 100)))
    return score

def render_deal_score_gauge(score: int):
    color = "#52b788" if score>=70 else "#f48c06" if score>=40 else "#ef233c"
    label = "Great Deal! 🎉" if score>=70 else "Fair Price 🤔" if score>=40 else "Overpriced ⚠️"
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title={"text": "Deal Score", "font":{"color":"#e8eaf0","family":"DM Sans"}},
        gauge={"axis":{"range":[0,100],"tickcolor":"#9da3b4"},
               "bar":{"color":color},
               "bgcolor":"rgba(20,25,40,0.8)",
               "steps":[{"range":[0,40],"color":"rgba(239,35,60,0.2)"},
                        {"range":[40,70],"color":"rgba(244,140,6,0.2)"},
                        {"range":[70,100],"color":"rgba(82,183,136,0.2)"}],
               "threshold":{"line":{"color":"white","width":2},"value":score}},
    ))
    apply_plotly_dark_theme(fig)
    fig.update_layout(height=220, margin=dict(t=40,b=10,l=20,r=20))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f'<p style="text-align:center; color:{color}; font-weight:700">'
                f'{label}</p>', unsafe_allow_html=True)

def render_depreciation_curve(base_price, manufacture_year, company):
    current_year = 2024
    car_age = current_year - manufacture_year
    years = list(range(current_year, current_year + 6))
    # Depreciation: 15% year 1, 10% thereafter for standard; 8% for luxury
    luxury = ["BMW","Mercedes","Audi","Jaguar","Land Rover","Volvo"]
    dep_rate = 0.08 if company in luxury else 0.12
    prices = [base_price * ((1 - dep_rate) ** i) for i in range(6)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=prices, mode='lines+markers',
                              line=dict(color='#e85d04', width=3),
                              marker=dict(size=8, color='#f48c06'),
                              fill='tozeroy',
                              fillcolor='rgba(232,93,4,0.1)',
                              name="Projected Value"))
    fig.add_annotation(x=years[0], y=prices[0],
                       text=f"Now: ₹{int(prices[0]):,}", showarrow=True,
                       arrowcolor='#52b788', font=dict(color='#52b788'))
    fig.add_annotation(x=years[-1], y=prices[-1],
                       text=f"2029: ₹{int(prices[-1]):,}", showarrow=True,
                       arrowcolor='#ef233c', font=dict(color='#ef233c'))
    apply_plotly_dark_theme(fig)
    fig.update_layout(title="📉 5-Year Value Projection", height=250,
                      xaxis_title="Year", yaxis_title="Est. Value (₹)")
    st.plotly_chart(fig, use_container_width=True)

def render_similar_cars(company, year, kms, fuel_type, predicted_price, df):
    st.markdown("#### 🔍 Similar Cars in Dataset")
    mask = ((df["company"] == company) &
            (df["fuel_type"] == fuel_type) &
            (abs(df["year"] - year) <= 2) &
            (abs(df["kms_driven"] - kms) <= 50000))
    similar = df[mask].head(5)
    if len(similar) == 0:
        similar = df[df["company"] == company].head(5)
    if len(similar) == 0:
        st.info("No similar cars found in dataset.")
        return
    for _, row in similar.iterrows():
        price_delta = int(row["Price"]) - int(predicted_price)
        delta_color = "#52b788" if price_delta < 0 else "#ef233c"
        delta_text  = f"−₹{abs(price_delta):,}" if price_delta < 0 else f"+₹{price_delta:,}"
        st.markdown(f"""
        <div class="glass-card" style="margin:0.4rem 0; padding:0.75rem 1rem">
          <div style="display:flex; justify-content:space-between; align-items:center">
            <div>
              <strong style="color:#e8eaf0">{row['name']}</strong>
              <span style="color:#9da3b4; font-size:0.8rem"> · {int(row['year'])} · {row['fuel_type']} · {int(row['kms_driven']):,} km</span>
            </div>
            <div style="text-align:right">
              <div style="color:#e85d04; font-weight:700">₹{int(row['Price']):,}</div>
              <div style="color:{delta_color}; font-size:0.8rem">{delta_text} vs prediction</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

def render_shap_lite(company, name, year, kms, fuel_type, price):
    st.markdown("#### 📊 Feature Contributions (SHAP-Lite)")
    car_age = 2024 - year
    base = price * 0.5
    contributions = {
        "Base Value":     base,
        "Car Age":        -car_age * 18000,
        "KMs Driven":     -(kms / 1000) * 2500,
        f"Company ({company})": price * 0.15 if company in ["BMW","Audi","Mercedes"] else price * 0.05,
        f"Fuel ({fuel_type})":  price * 0.08 if fuel_type == "Diesel" else price * 0.03,
        "Year Premium":   (year - 2010) * 12000,
    }
    contributions["Residual"] = price - sum(contributions.values())

    feats = list(contributions.keys())
    vals  = list(contributions.values())
    colors = ["#52b788" if v >= 0 else "#ef233c" for v in vals]
    colors[0] = "#4895ef"  # base always blue

    fig = go.Figure(go.Bar(
        y=feats, x=vals, orientation='h',
        marker_color=colors,
        text=[f"₹{int(v):+,}" for v in vals],
        textposition='outside',
        textfont=dict(color='#e8eaf0', size=11)
    ))
    apply_plotly_dark_theme(fig)
    fig.update_layout(title="How features affect this price",
                      height=300, margin=dict(l=120,r=80,t=40,b=20),
                      xaxis_title="Price Impact (₹)")
    st.plotly_chart(fig, use_container_width=True)
```

---

### PAGE 7 — 📈 Market Intelligence

`render_market_intelligence()`

Section A — Price Trend Forecast (2025–2027):
- Compute yearly median prices from dataset
- Fit a linear trend (np.polyfit) and extrapolate 3 years
- go.Scatter: historical (solid orange line), forecast (dashed amber line)
- Add shaded uncertainty band: ±15% around forecast
  Using go.Scatter with fill='tonexty' for band
- Annotations for 2025, 2026, 2027 forecast points

Section B — Brand × Year Heatmap:
- Compute pivot: df.groupby(["company","year"])["Price"].median().unstack()
- Take top 15 companies by count
- go.Heatmap: x=years, y=companies, z=median_price
- colorscale: [[0,"#131720"],[0.5,"#4895ef"],[1,"#e85d04"]]
- Add text annotations showing price in lakhs (z/100000:.1f L)

Section C — Best Value Finder:
- st.slider "Your Budget (₹)", 100000, 2000000, 500000, step=50000
- Format display: f"Budget: ₹{budget:,.0f} ({budget/100000:.1f} L)"
- Filter: df[df["Price"] <= budget * 1.1]
- Compute value_score per car:
  ```
  age_score = 1 / (car_age + 1)
  mileage_score = 1 / (1 + kms/100000)
  price_score = 1 - (price / budget)
  value_score = (age_score * 0.4 + mileage_score * 0.3 + price_score * 0.3) * 100
  ```
- Show top 5 as styled cards with value_score badge

Section D — Depreciation Calculator:
- st.multiselect "Compare cars (up to 3)", company names, max 3
- For each selected company + selectbox for car model + year input
- Plot overlaid depreciation curves (one per selected car)
- Each curve different color from palette

Section E — Price Alert Simulator:
- st.columns(2)
  Left: configure a car (company, year, fuel, kms) + price input "My asking price"
  Right: shows:
  - Model prediction for that config
  - % deviation: (asking - prediction) / prediction × 100
  - Verdict:
    ✅ "Good Deal! {pct:.1f}% below market" (green, if under 10% below)
    ⚠️ "Fair Price ({pct:.1f}% above market)" (yellow, if 0-15% above)
    ❌ "Overpriced! {pct:.1f}% above market" (red, if >15% above)
  - go.Indicator gauge showing deviation

Section F — Brand Tier Positioning:
- Compute per company: avg_price, count
- go.Scatter: x=count, y=avg_price, mode='markers+text'
- marker: size scaled by count, color by tier
- text: company names
- Add quadrant lines (median count, median price) with labels:
  "High Volume · High Price (Premium Mass Market)"
  "Low Volume · High Price (Luxury)"
  "High Volume · Low Price (Economy Mass Market)"
  "Low Volume · Low Price (Budget)"

---

### PAGE 8 — ⚙️ Pipeline Inspector

`render_pipeline_inspector()`

Section A — Interactive Pipeline Diagram:
Use st.markdown HTML + Streamlit columns to render a clickable pipeline.
Each stage is a button. On click: show detailed info below.

Stages:
1. 📂 Raw CSV (11,914 rows, 6 cols)
2. 🔄 Deduplication (removed 2,135 duplicates → 9,779 rows)
3. ⚙️ Feature Engineering (car_age = 2024 - year; 7 features)
4. 📊 Log Transform (Price → log1p(Price); skewness 5.64 → -0.12)
5. 📐 Scaling (StandardScaler on numeric features)
6. ✂️ Train/Test Split (80/20 → 7,823 / 1,956 rows)
7. 🔍 GridSearchCV (3-fold CV, tuned XGB/GB/RF)
8. 💾 Model Export (5 .pkl files + preprocessor.pkl)
9. 🚀 Dashboard (You are here!)

When a stage button is clicked (via session_state):
- Show a detailed glass card explaining that stage
- Show before/after stats if applicable
- Show relevant code snippet in st.code()

Section B — Preprocessing Stats Table:
| Step            | Before              | After               | Change     |
|-----------------|---------------------|---------------------|------------|
| Duplicates      | 11,914 rows         | 9,779 rows          | −2,135     |
| Null values     | 0                   | 0                   | ✅ Clean   |
| Price skewness  | 5.64                | -0.12               | Log1p ✅  |
| Feature count   | 6                   | 39 (after OHE)      | +33        |
| Price range     | ₹20K–₹1Cr           | ₹20K–₹1Cr           | Preserved  |

Render as styled HTML table.

Section C — Feature Engineering Explainer:
- Show how car_age is derived with a visual:
  `car_age = 2024 − year`  →  "A 2019 car has car_age = 5"
- Interactive: st.slider (year 1996–2024) → shows car_age in real time

Section D — Log Transform Deep-Dive:
- st.slider "Box-Cox λ", -2.0, 2.0, 0.0, 0.1, key="lambda_slider"
- For λ=0: equivalent to log transform
- Compute transformed prices using: (price^λ - 1) / λ if λ≠0 else log(price)
- Show skewness of transformed distribution in real time
- Plot: go.Histogram of transformed prices, title updates with skewness

Section E — Training Data Profiler:
- Use synthetically computed stats (or real if available):
  - st.dataframe of feature distributions: name, min, max, mean, std, null%
  - All null% = 0% → show green ✅
  - Color code: mean/std columns with background gradients

Section F — Model Cards:
For each of the 5 models, render an expandable glass card:
```
┌─────────────────────────────────────────────────────┐
│ 🤖 XGBoost                    [v1.7.3]              │
│ Architecture: Gradient Boosted Decision Trees        │
│ Hyperparameters: n_estimators=300, max_depth=3,      │
│   learning_rate=0.1, subsample=0.8, colsample=0.8   │
│ Performance: R²=0.7463 | RMSE=₹2.57L | MAE=₹1.75L  │
│ Training time: ~12.5s on 7,823 samples               │
│ Best for: Balanced accuracy + speed                  │
│ Strengths: Handles outliers, feature importance      │
│ Weaknesses: Less interpretable than linear models   │
└─────────────────────────────────────────────────────┘
```

Section G — Environment Info:
```python
import sys, platform
st.code(f"""
Python:     {sys.version}
Platform:   {platform.platform()}
Streamlit:  {st.__version__}
Working dir: {Path('.').resolve()}
ML files:   {'Found ✅' if Path('ml_ready').exists() else 'Not found ⚠️ (Demo Mode)'}
Users DB:   {USERS_DB_PATH} ({'exists' if USERS_DB_PATH.exists() else 'will be created'})
""")
```

Section H — Links & Credits:
Render styled buttons:
- "📁 View on GitHub" (link button)
- "📄 Read Report" (download button for a sample PDF)
- "💼 LinkedIn"
All as HTML anchor tags with `.orange-btn` class styling.

---

════════════════════════════════════
SECTION 5 — ENHANCED FEATURES
════════════════════════════════════

### Feature A — Smart Price Explainer
(Already integrated into Page 6 — `generate_price_explanation()`)

### Feature B — Deal Score System
(Already integrated into Page 6 — `compute_deal_score()` + `render_deal_score_gauge()`)

### Feature C — Ensemble Prediction Confidence
In Page 6, when `compare_all=True`:
- Run all 5 models (or available ones in demo mode)
- Compute ensemble = weighted average (weights proportional to R²)
- Compute spread = (max_pred - min_pred) / ensemble * 100
- Color-code confidence:
  - spread < 10%: green badge "🟢 High Confidence"
  - spread 10–20%: yellow badge "🟡 Medium Confidence"
  - spread > 20%: red badge "🔴 Low Confidence"
- Show as go.Bar with each model's prediction + ensemble line

### Feature D — Interactive SHAP-lite
(Already integrated into Page 6 — `render_shap_lite()`)

### Feature E — Data Quality Report
On app startup (render in Dashboard and Dataset Explorer):
```python
def render_data_quality_badge():
    st.markdown("""
    <div class="glass-card" style="padding:0.75rem 1.25rem">
      <strong style="color:#e8eaf0">📋 Data Quality Report</strong><br>
      <span style="color:#52b788">✅ No null values found</span><br>
      <span style="color:#52b788">✅ 2,135 duplicates removed</span><br>
      <span style="color:#52b788">✅ Outliers capped at 99th percentile</span><br>
      <span style="color:#f48c06">⚠️ 3 rare fuel types grouped as "Alternative"</span>
    </div>
    """, unsafe_allow_html=True)
```

### Feature F — Bulk Prediction Upload
In Page 6, add a second tab: "📦 Bulk Predict"
- st.file_uploader("Upload CSV", type=["csv"])
- Expected columns: name, company, year, kms_driven, fuel_type
- On upload: validate columns, run all models, show results table
- st.download_button: download Excel with all predictions + ensemble
  (use openpyxl/xlsxwriter: `df.to_excel(buffer, index=False)`)

### Feature G — Model Drift Simulator
In Page 7, Section G — "Time Machine":
- st.slider "Fast forward to year:", 2024, 2030, 2024
- For each year increment: car_age += (target_year - 2024)
- Run predictions on a sample of 100 cars
- Show before/after price distribution overlay (go.Histogram with opacity=0.6)
- Caption: "In {year}, median car value shifts by {delta:+.1f}%"

### Feature H — A/B Comparison Mode
In Page 6, add a third tab: "⚖️ Compare Two Cars"
- Two side-by-side input panels (col_a, col_b)
- Each with: company, car name, year, kms, fuel
- "Compare" button → run prediction for both
- Show:
  - Winner badge on cheaper/better-value car
  - Price delta card: "Car A is ₹{delta:,} more expensive"
  - Feature diff table: side-by-side comparison of all inputs + predictions
  - Save comparison button → calls `save_comparison()`

### Feature I — Explainability Mode Toggle
Sidebar toggle: "⚡ Expert Mode"
- When OFF (Simple Mode):
  - Hide R², RMSE, statistical terms
  - Replace with plain English: "This model is X% accurate"
  - Show colored emojis instead of numbers
- When ON (Expert Mode):
  - Show all metrics, residuals, feature importances
  - Show model architecture details
  - Show statistical annotations on charts

### Feature J — Price History Simulation
In Page 7, Section J:
- Pick company + model + manufacture_year
- Show hypothetical: "When was the best time to buy this car?"
- Plot: estimated market price from manufacture_year to 2024
  Using depreciation model in reverse + market trend overlay
- Mark best buying years with ▼ indicators (color: teal)
- Mark worst buying years with ▲ indicators (color: red)

---

════════════════════════════════════
SECTION 6 — GLOBAL TECHNICAL REQUIREMENTS
════════════════════════════════════

### 6.1 — Single File Structure

One file: `streamlit_app.py`
Target: ~2000 lines (use tight, efficient helper functions)
Organization order:
```
1. IMPORTS (all at top, grouped: stdlib, third-party, local)
2. CONSTANTS (colors, MODEL_METRICS, paths)
3. AUTH HELPERS (load_users_db → delete_user)
4. CSS INJECTION (inject_css)
5. DATA LOADING (@st.cache_data functions)
6. MODEL LOADING (@st.cache_resource functions)
7. PLOTLY HELPERS (apply_plotly_dark_theme, etc.)
8. PREDICTION HELPERS (run_prediction, etc.)
9. PAGE RENDERERS (render_login_page → render_admin_panel)
10. SIDEBAR (render_sidebar)
11. MAIN (main function, if __name__ == "__main__": st....)
```

### 6.2 — Caching Strategy

```python
@st.cache_data(show_spinner="📊 Loading dataset...", ttl=3600)
def load_data() -> pd.DataFrame: ...

@st.cache_resource(show_spinner="🤖 Loading models...")
def load_models() -> dict: ...

@st.cache_data(show_spinner="⚙️ Loading preprocessor...")
def load_preprocessor(): ...

@st.cache_data(ttl=600)
def load_test_data() -> tuple: ...

@st.cache_data(ttl=3600)
def get_filtered_data(company_filter, fuel_filter, year_min, year_max,
                       price_min, price_max, kms_min, kms_max) -> pd.DataFrame: ...
```

### 6.3 — Plotly Helper

Apply to ALL charts:
```python
def apply_plotly_dark_theme(fig, height=400):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,16,25,0.8)",
        font=dict(family="DM Sans", color="#e8eaf0", size=12),
        height=height,
        margin=dict(t=40, b=40, l=40, r=40),
        legend=dict(bgcolor="rgba(20,25,40,0.8)",
                    bordercolor="rgba(232,93,4,0.3)", borderwidth=1),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", gridwidth=1,
                   linecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", gridwidth=1,
                   linecolor="rgba(255,255,255,0.1)"),
    )
    return fig

PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}
```

### 6.4 — Demo Mode

If `not Path("ml_ready").exists()`:
```python
def generate_demo_data() -> pd.DataFrame:
    np.random.seed(42)
    n = 500
    companies = ["Maruti","Hyundai","Honda","Toyota","Ford","Tata","Mahindra","BMW","Audi","Volkswagen"]
    fuels = ["Petrol","Diesel","CNG","LPG","Electric"]
    years = np.random.randint(2005, 2024, n)
    ...
    return df

def demo_predict(company, year, kms, fuel_type) -> float:
    """Simple heuristic prediction for demo mode."""
    base = 500000
    base += (year - 2010) * 25000
    base -= kms * 0.8
    if fuel_type == "Diesel": base *= 1.1
    if fuel_type == "Electric": base *= 1.3
    if company in ["BMW","Audi","Mercedes"]: base *= 3.5
    return max(50000, base + np.random.normal(0, 20000))
```

Show persistent demo banner:
```python
st.warning("⚠️ **Demo Mode** — ML model files not found. "
           "Using synthetic data and heuristic predictions. "
           "Place `ml_ready/` folder in the same directory to enable full mode.")
```

### 6.5 — run_prediction() Function

```python
def run_prediction(company: str, car_name: str, year: int, kms: int,
                   fuel_type: str, model_name: str) -> dict:
    """
    Build feature vector, transform, predict, invert log, return dict.
    Falls back to demo_predict() if models not loaded.
    """
    models = load_models()
    preprocessor = load_preprocessor()

    if not models or not preprocessor:
        price = demo_predict(company, year, kms, fuel_type)
        return {"price": price, "price_lakh": price/100000,
                "model": model_name, "demo": True}

    try:
        # Build raw input DataFrame matching training schema
        car_age = 2024 - year
        input_df = pd.DataFrame([{
            "name": car_name, "company": company, "year": year,
            "kms_driven": kms, "fuel_type": fuel_type, "car_age": car_age
        }])
        # Transform via preprocessor
        X = preprocessor.transform(input_df)
        # Get model
        model_key_map = {
            "Linear Regression":"linear_regression",
            "Ridge Regression":"ridge",
            "XGBoost":"xgboost",
            "Gradient Boosting":"gradient_boosting",
            "Random Forest":"random_forest",
        }
        pkl_key = model_key_map.get(model_name, "xgboost")
        model = models.get(pkl_key)
        if model is None:
            raise ValueError(f"Model {pkl_key} not found")
        # Predict in log space, invert
        log_pred = model.predict(X)[0]
        price = float(np.expm1(log_pred))
        price = max(10000, price)  # floor at ₹10K
        return {"price": price, "price_lakh": price/100000,
                "model": model_name, "demo": False}
    except Exception as e:
        st.error(f"Prediction error: {e}. Falling back to demo mode.")
        price = demo_predict(company, year, kms, fuel_type)
        return {"price": price, "price_lakh": price/100000,
                "model": model_name, "demo": True}
```

### 6.6 — Model Loading

```python
@st.cache_resource(show_spinner="🤖 Loading ML models...")
def load_models() -> dict:
    models = {}
    model_path = Path("ml_ready/models")
    if not model_path.exists():
        return {}
    for name in ["gradient_boosting","xgboost","random_forest",
                 "linear_regression","ridge"]:
        try:
            with open(model_path / f"{name}.pkl", "rb") as f:
                models[name] = pickle.load(f)
        except Exception as e:
            st.warning(f"Could not load {name}: {e}")
    return models

@st.cache_data(show_spinner="⚙️ Loading preprocessor...")
def load_preprocessor():
    try:
        with open("ml_ready/preprocessor.pkl", "rb") as f:
            return pickle.load(f)
    except Exception:
        return None
```

### 6.7 — Requirements

Include as a comment block at the end of the file:
```python
# ─── requirements.txt ──────────────────────────────────────────────
# streamlit>=1.32.0
# pandas>=2.0.0
# numpy>=1.24.0
# plotly>=5.18.0
# scikit-learn>=1.3.0
# xgboost>=2.0.0
# scipy>=1.11.0
# openpyxl>=3.1.0
# Pillow>=10.0.0
# ──────────────────────────────────────────────────────────────────
```

---

════════════════════════════════════
SECTION 7 — COMPLETE MAIN FUNCTION
════════════════════════════════════

```python
def main():
    st.set_page_config(
        page_title="AutoIntel v6.0",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    init_session_state()

    # Auth gate
    if not st.session_state.get("authenticated", False):
        auth_page = st.session_state.get("auth_page", "login")
        if auth_page == "signup":
            render_signup_page()
        elif auth_page == "forgot":
            render_forgot_password_page()
        else:
            render_login_page()
        st.stop()

    # Main app
    track_page_visit(
        st.session_state.user.get("user_id",""),
        st.session_state.get("current_page","Dashboard")
    )
    render_sidebar()

    page = st.session_state.get("current_page", "Dashboard")
    page_map = {
        "Dashboard":           render_dashboard,
        "Dataset Explorer":    render_dataset_explorer,
        "EDA Deep-Dive":       render_eda,
        "Model Lab":           render_model_lab,
        "Residual Analysis":   render_residual_analysis,
        "Price Predictor":     render_price_predictor,
        "Market Intelligence": render_market_intelligence,
        "Pipeline Inspector":  render_pipeline_inspector,
        "My Profile":          render_profile_page,
        "Admin Panel":         render_admin_panel,
    }
    renderer = page_map.get(page, render_dashboard)
    renderer()

if __name__ == "__main__":
    main()
```

---

════════════════════════════════════
DELIVERABLE CHECKLIST
════════════════════════════════════

Produce the COMPLETE `streamlit_app.py`. Verify before output:

- [ ] Auth gate works: login/signup/forgot password
- [ ] users_db.json created automatically on first run
- [ ] Demo user created if no users exist
- [ ] All 9 pages + Admin Panel implemented (no TODOs)
- [ ] All charts use go.* (not px.*), plotly_dark template
- [ ] apply_plotly_dark_theme() called on every fig
- [ ] All predictions invert log with np.expm1()
- [ ] Feature mismatch handled gracefully
- [ ] Demo mode activated when ml_ready/ missing
- [ ] Session state keys initialized with defaults
- [ ] Prediction history saved to users_db.json per user
- [ ] Profile page with 6 tabs implemented
- [ ] Admin panel shows only for role="admin"
- [ ] Logout clears all session state
- [ ] CSS block covers all elements listed in Section 2
- [ ] Sidebar shows avatar, quick stats, global filters, logout
- [ ] All st.cache_data / st.cache_resource applied
- [ ] Bulk CSV upload + Excel download in Price Predictor
- [ ] A/B comparison saves to user saved_comparisons
- [ ] All BUG-FIX REQUIREMENTS from Section 4 addressed
- [ ] requirements.txt comment block at bottom
- [ ] App runs with: `streamlit run streamlit_app.py`
- [ ] No import errors on fresh install of requirements

Run command: `streamlit run streamlit_app.py`