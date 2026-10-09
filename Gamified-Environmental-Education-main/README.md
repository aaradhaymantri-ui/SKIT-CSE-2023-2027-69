## Topics

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=FFFFFF)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=FFFFFF)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=000000)
![Gamification](https://img.shields.io/badge/Gamification-FF69B4?style=for-the-badge)
![Education](https://img.shields.io/badge/Education-4B0082?style=for-the-badge)
![Sustainability](https://img.shields.io/badge/Sustainability-228B22?style=for-the-badge)
![Climate Change](https://img.shields.io/badge/Climate_Change-FF4500?style=for-the-badge)
![Waste Management](https://img.shields.io/badge/Waste_Management-808080?style=for-the-badge)
![Renewable Energy](https://img.shields.io/badge/Renewable_Energy-00FF7F?style=for-the-badge)
![Environmental Awareness](https://img.shields.io/badge/Environmental_Awareness-32CD32?style=for-the-badge)
![Educational Games](https://img.shields.io/badge/Educational_Games-1E90FF?style=for-the-badge)
![EdTech](https://img.shields.io/badge/EdTech-FF8C00?style=for-the-badge)


# EcoLearning Platform 🌱

EcoLearning Platform is an interactive and engaging educational tool designed for both students and educators. It bridges the gap between theoretical knowledge and practical application through games, learning modules, and real-time dashboards.

---

## ✨ Key Features

### For Students
- **Personalized Dashboard:** Track progress with Eco-Points, challenges completed, badges earned, and current rank.  
- **Interactive Eco-Games Hub:** Play six unique games designed to teach core environmental concepts.  
- **Games Include:**
  - **Waste Sorting Challenge:** Drag-and-drop items into Recyclable, Organic, Electronic, and Hazardous bins.  
  - **Eco Memory Match:** Match environmental causes with effects.  
  - **Green Word Puzzle:** Solve crosswords with environmental clues, revealing fun facts.  
  - **Eco Bubble Pop:** Merge eco-friendly items to create higher-level objects.  
  - **EcoCatchers:** Catch beneficial items while avoiding harmful ones.  
  - **Eco-Popper:** Pop "good" bubbles to score points and learn facts while avoiding "bad" bubbles.  
- **Structured Learning Modules:** Flashcards covering topics like Air Quality, Water Pollution, and Soil Degradation.  
- **Competitive Leaderboards:** Track rankings with filters for "This Week," "This Month," and "All Time."  
- **Rewarding Profile System:** Showcases earned badges and achievements.  
- **Smart EcoBot Assistant:** A chatbot offering sustainability tips and answering questions.
- **Eco Action Missions:** Complete daily and weekly real-world actions, submit short reflections, earn Eco-Points, and build a streak.

### For Teachers
- **Live Environmental Dashboard:** Monitor key environmental metrics such as AQI, Temperature, Humidity, and CO₂ levels in real time.  
- **Teacher-Specific Dashboard:** Monitor student progress and class performance.  
- **Custom Game Creator:** Easily create quizzes, word puzzles, and drag-and-drop activities through a step-by-step form.
- **Class Eco Missions:** Assign daily or weekly actions to your class and review completion, reflections, points, and student streaks.

To use missions, register student and teacher accounts with the same school and class name. Choose a username at signup; leaderboard entries display as `BOT <username>` and include only bots from the signed-in student's school and class. Leaderboard points come from mission completions and can be filtered by week, month, or all time. Students can sign up directly; teacher accounts require the configured `TEACHER_SIGNUP_CODE` invitation. The profile and student/teacher dashboard routes require sign-in; the profile API returns only the account identified by the signed-in session. Access JWTs live in frontend memory; refresh tokens are rotated, stored server-side as hashes, and sent only in an HttpOnly cookie. No authentication token is stored in local storage. The app has no administrator role or user-profile admin endpoint.

### Backend security configuration

Run these commands from `backend` in PowerShell for local development. Keep the generated values private; do not commit them. The local CORS defaults allow the Vite development origins on port 5173.

```powershell
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(48))"
$env:TEACHER_SIGNUP_CODE = python -c "import secrets; print(secrets.token_urlsafe(32))"
python app.py
```

Set `APP_ENV=production`, `SECRET_KEY` (at least 32 characters), and `CORS_ORIGINS` (a comma-separated list of exact trusted frontend origins) in the production environment. Production startup fails if the secret or CORS allowlist is missing; do not enable Flask debug mode in production. Production authentication cookies are Secure and require HTTPS. Teacher account creation stays disabled until a `TEACHER_SIGNUP_CODE` of at least 24 characters is configured. The frontend can be pointed at a different API origin with `VITE_API_URL`; the API origin must be listed in `CORS_ORIGINS`.

Access JWTs expire after 10 minutes. The refresh cookie has a 30-day maximum lifetime and is rotated on use; logout revokes the server-side refresh session. Refresh and logout requests require an allowlisted `Origin` and a CSRF token. Existing users may need to sign in again after upgrading because the old bearer-token sessions are not migrated.

Run backend security tests from `backend`:

```powershell
python -m unittest discover -s tests -v
```

Use the [security test tracker](./docs/SECURITY_TEST_TRACKER.md) to record automated results and manual/browser checks over time.

---

## 🗓️ Six-Week Delivery Plan

See the [six-week sprint plan](./docs/SIX_WEEK_SPRINT_PLAN.md) for the weekly goals, security work starting today, and a sprint progress board to update at each review.

---

## 🛠️ Technology Stack

- **Frontend:** React, Tailwind CSS, PostCSS  
- **Backend:** Flask, SQLAlchemy  
- **Database:** SQLite, MySQL  

---

## 🚀 Getting Started

Follow these steps to set up the project locally.

### Prerequisites
- Node.js & npm (for frontend)  
- Python & pip (for backend)  
- Git 