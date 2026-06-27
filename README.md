# PrepBuddy

PrepBuddy is an intelligent, personalized career preparation and tutoring assistant. Unlike standard chatbot solutions that immediately provide answers, PrepBuddy acts as an AI Socratic Tutor to guide students towards deep logical understanding and problem-solving.

The application also features a Course Explorer to search online educational material and log practicing progress statistics.

---

## Technical Stack

- **Frontend**: Vanilla HTML5, CSS3, JavaScript (Local-first browser rendering).
- **Backend**: Python, FastAPI (High performance REST endpoints).
- **Database**: SQLite (Local file-based system).
- **ORM**: SQLAlchemy.
- **Authentication**: JWT (JSON Web Tokens) & password hashing using direct `bcrypt` libraries.
- **AI Tutoring**: Google Gemini API.
- **Course Finder**: Google Custom Search JSON API.

---

## Core Features

1. **Socratic AI Tutoring**: Buddy AI tracks chat logs and answers questions using guided prompts and hints instead of immediate code blocks.
2. **Course Search Registry**: Indexes online courses (Coursera, Udemy, YouTube, etc.) matching target skills.
3. **Bookmarks Board**: Save and delete recommended learning materials to your study library.
4. **Learning Progress Analytics**: Automatically tracks topics discussed, chat totals, and bookmarks counts.
5. **Robust Security**: Uses hashed password logic and JWT route guards.
6. **Resilient Fallback Mode**: If external Google API keys are not set, the backend switches automatically to offline simulations, ensuring 100% features testability out-of-the-box.

---

## Project Directory Structure

```
prepbuddy/
├── archive/              # Obsolete command-line prototype files
├── backend/
│   ├── main.py          # FastAPI application routes & endpoints
│   ├── config.py        # Environment variables loader
│   ├── database.py      # SQLite configuration & session provider
│   ├── models.py        # SQLAlchemy schema definitions
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── auth.py          # Direct bcrypt hashing & JWT tokens
│   ├── ai.py            # Gemini API & Socratic fallbacks
│   ├── course.py        # Custom Search crawler & mock fallbacks
│   └── progress.py      # Progress tracking increments
│
├── database/
│   └── prepbuddy.db     # Primary SQLite database (generated automatically)
│
├── frontend/
│   ├── css/
│   │   ├── global.css   # Dark theme settings, variables, global layout
│   │   ├── auth.css     # Registration and sign-in cards
│   │   ├── dashboard.css# Statistics widgets & activity grids
│   │   ├── chat.css     # Conversational bubble layout & prompt tags
│   │   └── courses.css  # Search box & courses grid
│   ├── js/
│   │   ├── auth.js      # Auth checks, login forms, & authFetch wrapper
│   │   ├── dashboard.js # Progress dashboard data loader
│   │   ├── chat.js      # AI dialog submission & suggestions helper
│   │   └── courses.js   # Searches & bookmark managers
│   ├── index.html       # Entry dispatcher (auto-redirects to login/dash)
│   ├── login.html       # Login view
│   ├── register.html    # Registration view
│   ├── dashboard.html   # Main dashboard portal view
│   ├── chat.html        # Socratic Chat view
│   ├── courses.html     # Course Explorer view
│   └── profile.html     # Settings & logout view
│
├── landing_page/
│   ├── index.html       # Interactive Product landing page
│   ├── style.css        # Gradient visual themes
│   └── script.js        # Dynamic landing script
│
├── .env                 # Secret environment keys config
├── .env.example         # Template environment config variables
├── .gitignore           # Exclusions rules for git
├── requirements.txt     # Python requirements list
└── README.md            # Master project guide
```

---

## Local Setup & Installation

### Step 1: Create Virtual Environment
Run from the root `prepbuddy/` directory:
- **Windows**:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Step 2: Install Packages
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and enter your API keys. If you do not have keys, leave them blank, and PrepBuddy will run in offline fallback simulation mode:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_API_KEY=your_google_search_key_here
GOOGLE_CSE_ID=your_custom_engine_id_here
SECRET_KEY=generate_a_random_jwt_hash_key_here
```

---

## Running the Application

### 1. Launch FastAPI Backend
Navigate to the `backend/` directory and execute:
```bash
uvicorn main:app --reload
```
- API Endpoint: `http://127.0.0.1:8000`
- Interactive Swagger docs: `http://127.0.0.1:8000/docs`
- *On startup, the SQLite database `database/prepbuddy.db` is created automatically.*

### 2. Launch Web Interface
Open [landing_page/index.html](file:///c:/projects_&_coding/prepbuddy/landing_page/index.html) directly in any modern web browser.
- Click **"Launch App"** or **"Get Started"** to access the dashboard.
- The browser will automatically guide you through `login.html`, account registration, and dashboard access.
