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

To use missions, register student and teacher accounts with the same school and class name. Choose a username at signup; leaderboard entries display as `BOT <username>` and include only bots from the signed-in student's school and class. Leaderboard points come from mission completions and can be filtered by week, month, or all time. Sign in to a teacher account to assign missions; students sign in to submit a reflection after completing an action. Existing accounts are treated as students and receive a generated username if they do not already have one. Configure a stable `SECRET_KEY` environment variable for the Flask backend so signed-in sessions remain valid across restarts. The profile and student/teacher dashboard routes require sign-in; the profile API returns only the account identified by the signed-in session. Sessions are kept in that browser's local storage, and the app has no administrator role or user-profile admin endpoint.

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