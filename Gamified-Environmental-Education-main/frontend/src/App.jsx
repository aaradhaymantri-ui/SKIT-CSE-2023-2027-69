import React from "react";
import { BrowserRouter as Router, Routes, Route, useLocation, Navigate } from "react-router-dom";

import Signin from "./pages/Signin";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import StudentDash from "./pages/StudentDash";
import Leaderboard from "./pages/Leaderboard";
import Profile from "./pages/Profile";
import Quiz from "./pages/Quiz";
import DragAndDrop from "./pages/games/DragAndDrop";
import MemoryMatch from "./pages/games/MemoryMatch";
import WordPuzzle from "./pages/games/WordPuzzle";
import EcoCatcher from "./pages/games/EcoCatcher";
import EcoPopper from "./pages/games/EcoPopper";
import EcoBubble from "./pages/games/EcoBubble";
import FlashCardPage from "./pages/FlashCardPage";
import Deck from "./pages/Deck";
import Games from "./pages/GameLayout";
import TeacherDashboard from "./pages/TeacherDashboard";
import CreateGame from "./pages/CreateGame";
import Landing from "./pages/Landing";
import FloatingChatbot from "./components/FloatingChatbot";
import { AuthProvider, useAuth } from "./auth/AuthContext";


// Component to conditionally render chatbot
function ConditionalChatbot() {
  const location = useLocation();
  const excludedPaths = ['/', '/signup', '/signin'];
  
  if (excludedPaths.includes(location.pathname)) {
    return null;
  }
  
  return <FloatingChatbot />;
}

function ProtectedRoute({ children, role }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <p role="status" className="p-8 text-center">Checking your session…</p>;
  }
  if (!user?.id) {
    return <Navigate to="/signin" replace />;
  }
  if (role && user.role !== role) {
    return <Navigate to={user.role === "teacher" ? "/teacherdashboard" : "/studentdashboard"} replace />;
  }
  return children;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="relative">
          <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/signin" element={<Signin />} />
          <Route path="/studentdashboard" element={<ProtectedRoute role="student"><StudentDash /></ProtectedRoute>} />
          <Route path="/livedashboard" element={<Dashboard />} />
          <Route path="/leaderboard" element={<ProtectedRoute role="student"><Leaderboard /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/quiz" element={<Quiz />} />
          <Route path="/draganddrop" element={<DragAndDrop />} />  
          <Route path="/memorymatch" element={<MemoryMatch />} />
          <Route path="/wordpuzzle" element={<WordPuzzle />} />
          <Route path="/ecocatcher" element={<EcoCatcher />} />
          <Route path="/ecobubble" element={<EcoBubble />} />
          <Route path="/ecopopper" element={<EcoPopper />} />
          <Route path="/learntopics" element={<FlashCardPage />} />
          <Route path="/deck/:topic" element={<Deck />} />
          <Route path="/games" element={<Games />} />
          <Route path="/teacherdashboard" element={<ProtectedRoute role="teacher"><TeacherDashboard /></ProtectedRoute>} />
          <Route path="/creategame" element={<CreateGame />} />
          </Routes>
          <ConditionalChatbot />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
