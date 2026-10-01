import React, { useCallback, useEffect, useState } from "react";
import StudHeader from '../components/StudHeader';
import { Link, useNavigate } from "react-router-dom";
import AnimatedBackground from "../components/AnimatedBackground.jsx";
import MissionBoard from "./MissionBoard";

function getDashboardUser() {
  try {
    const currentUser = JSON.parse(localStorage.getItem("currentUser") || "null");
    return {
      name: currentUser?.name || localStorage.getItem("userName") || "Eco Champion",
      ecoPoints: 0,
      email: currentUser?.email || "",
      className: currentUser?.class_name || ""
    };
  } catch (error) {
    console.error("Could not read the signed-in user.", error);
    return { name: "Eco Champion", ecoPoints: 0, email: "", className: "" };
  }
}

// Dashboard Cards
function DashboardCards({ user }) {
  return (
    <div>
      <h2 className="font-bold text-2xl mb-4 text-center lg:text-left" style={{ color: 'var(--text)' }}>Your Eco-Progress</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl text-center" style={{ background: 'rgba(22,163,74,0.08)', border: '1px solid rgba(0,0,0,0.06)' }}>
          <p className="text-3xl font-bold" style={{ color: 'var(--primary)' }}>{user.ecoPoints}</p>
          <p className="text-sm" style={{ color: 'var(--muted)' }}>Eco-Points 🌱</p>
        </div>
        <div className="p-4 rounded-xl text-center" style={{ background: 'rgba(6,182,212,0.08)', border: '1px solid rgba(0,0,0,0.06)' }}>
          <p className="text-3xl font-bold" style={{ color: '#0284c7' }}>{user.challengesDone}</p>
          <p className="text-sm" style={{ color: 'var(--muted)' }}>Missions Done ✅</p>
        </div>
        <div className="p-4 rounded-xl text-center" style={{ background: 'rgba(245,158,11,0.10)', border: '1px solid rgba(0,0,0,0.06)' }}>
          <p className="text-lg font-bold" style={{ color: '#ca8a04' }}>{user.className || "Not set"}</p>
          <p className="text-sm" style={{ color: 'var(--muted)' }}>Class</p>
        </div>
        <div className="p-4 rounded-xl text-center" style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(0,0,0,0.06)' }}>
          <p className="text-3xl font-bold" style={{ color: '#ef4444' }}>{user.streak}</p>
          <p className="text-sm" style={{ color: 'var(--muted)' }}>Day Streak 🔥</p>
        </div>
      </div>
    </div>
  );
}

// Quick Start Panel
function QuickStart() {
  return (
    <div>
      <h2 className="font-bold text-2xl mb-4">Quick Start</h2>
      <div className="space-y-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-800">Next Challenge: Tree Guardians</h3>
          <p className="text-sm text-gray-600">Find and report on a tree in your local park. (+75 EP)</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-800">Featured Game: Recycle Sort-Off</h3>
          <p className="text-sm text-gray-600">Test your waste sorting skills and earn (+50 EP)!</p>
        </div>
      </div>
    </div>
  );
}

// Navigation Section
function NavigationSection() {
  return (
    <nav className="px-4 py-4 rounded-t-3xl mt-4 shadow-lg" style={{ background: 'var(--panel)', border: '1px solid rgba(0,0,0,0.06)' }}>
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link to="/studentdashboard" className="nav-link active">Dashboard</Link>
            <Link to="/games" className="nav-link">Games</Link>
            <Link to="/learntopics" className="nav-link">Learn</Link>
            <Link to="/leaderboard" className="nav-link">Leaderboard</Link>
            <Link to="/profile" className="nav-link">Profile</Link>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm" style={{ color: 'var(--muted)' }}>Quick Actions</div>
            <Link to="/quiz" className="nav-btn">Quiz</Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

// Dashboard Layout
function DashboardContent({ user, onStatsChange }) {
  return (
    <div className="max-w-6xl mx-auto px-6 py-6 space-y-6">
      {/* Hero Banner */}
      <section className="rounded-3xl p-6 sm:p-8" style={{ background: 'linear-gradient(135deg, rgba(16,185,129,0.18), rgba(6,182,212,0.18))', border: '1px solid rgba(0,0,0,0.06)' }}>
        <div className="flex flex-col lg:flex-row items-center lg:items-start gap-6">
          <div className="flex-1 text-center lg:text-left">
            <h1 className="text-2xl sm:text-3xl font-extrabold" style={{ color: 'var(--text)' }}>Welcome back, {user.name}! 🌿</h1>
            <p className="mt-2" style={{ color: 'var(--muted)' }}>Keep your streak alive and earn Eco-Points with quick daily actions and games.</p>
            <div className="mt-4 flex flex-wrap gap-3 justify-center lg:justify-start">
              <Link to="/games" className="btn rounded-full px-6 py-2" style={{ background: 'linear-gradient(135deg, var(--primary), var(--secondary))', color: '#fff' }}>Play Games</Link>
              <Link to="/learntopics" className="btn rounded-full px-6 py-2" style={{ background: 'rgba(255,255,255,0.95)', border: '1px solid rgba(0,0,0,0.06)', color: 'var(--text)' }}>Learn Topics</Link>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 w-full lg:w-auto">
            <div className="rounded-2xl p-4 text-center" style={{ background: '#fff', border: '1px solid rgba(0,0,0,0.06)' }}>
              <div className="text-3xl">🎯</div>
              <div className="text-sm mt-1" style={{ color: 'var(--muted)' }}>Daily Goal</div>
              <div className="font-bold">Complete 1 challenge</div>
            </div>
            <div className="rounded-2xl p-4 text-center" style={{ background: '#fff', border: '1px solid rgba(0,0,0,0.06)' }}>
              <div className="text-3xl">🏫</div>
              <div className="text-sm mt-1" style={{ color: 'var(--muted)' }}>Your class</div>
              <div className="font-bold">{user.className || "Not set"}</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-3xl p-6" style={{ background: 'var(--panel)', border: '1px solid rgba(0,0,0,0.06)', boxShadow: '0 8px 24px rgba(22,163,74,0.06)' }}>
            <DashboardCards user={user} />
          </div>

          <MissionBoard onStatsChange={onStatsChange} />

          {/* Featured Games */}
          <section className="rounded-3xl p-6" style={{ background: '#fff', border: '1px solid rgba(0,0,0,0.06)' }}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-xl">Featured Games</h2>
              <Link to="/games" className="text-sm" style={{ color: 'var(--primary)' }}>View all →</Link>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Link to="/draganddrop" className="rounded-2xl p-4" style={{ background: 'rgba(22,163,74,0.06)', border: '1px solid rgba(0,0,0,0.06)' }}>
                <div className="text-lg font-semibold">Recycle Sort</div>
                <p className="text-sm mt-1" style={{ color: 'var(--muted)' }}>Drag items into the right bin.</p>
              </Link>
              <Link to="/memorymatch" className="rounded-2xl p-4" style={{ background: 'rgba(6,182,212,0.08)', border: '1px solid rgba(0,0,0,0.06)' }}>
                <div className="text-lg font-semibold">Eco Memory</div>
                <p className="text-sm mt-1" style={{ color: 'var(--muted)' }}>Match eco pairs to win.</p>
              </Link>
              <Link to="/wordpuzzle" className="rounded-2xl p-4" style={{ background: 'rgba(245,158,11,0.10)', border: '1px solid rgba(0,0,0,0.06)' }}>
                <div className="text-lg font-semibold">Green Words</div>
                <p className="text-sm mt-1" style={{ color: 'var(--muted)' }}>Unscramble sustainability terms.</p>
              </Link>
            </div>
          </section>
        </div>

        {/* Right Column */}
        <div className="lg:col-span-1 space-y-6">
          <div className="rounded-3xl p-6" style={{ background: 'var(--panel)', border: '1px solid rgba(0,0,0,0.06)', boxShadow: '0 8px 24px rgba(22,163,74,0.06)' }}>
            <QuickStart />
          </div>
          <div className="rounded-3xl p-6" style={{ background: '#fff', border: '1px solid rgba(0,0,0,0.06)' }}>
            <h2 className="font-bold text-xl mb-3">Learn Preview</h2>
            <div className="grid grid-cols-2 gap-3">
              <Link to="/learntopics" className="rounded-xl p-3 text-center" style={{ background: 'rgba(0,0,0,0.03)' }}>🌍 Climate</Link>
              <Link to="/learntopics" className="rounded-xl p-3 text-center" style={{ background: 'rgba(0,0,0,0.03)' }}>♻️ Recycling</Link>
              <Link to="/learntopics" className="rounded-xl p-3 text-center" style={{ background: 'rgba(0,0,0,0.03)' }}>💧 Water</Link>
              <Link to="/learntopics" className="rounded-xl p-3 text-center" style={{ background: 'rgba(0,0,0,0.03)' }}>🔆 Solar</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function StudentDash() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [user, setUser] = useState(() => ({
    ...getDashboardUser(),
    challengesDone: 0,
    badges: 0,
    streak: 0,
  }));
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;
    fetch("http://localhost:5000/profile", {
      headers: { Authorization: `Bearer ${localStorage.getItem("authToken") || ""}` }
    })
      .then(async (response) => {
        const data = await response.json();
        if (response.status === 401) {
          localStorage.removeItem("authToken");
          localStorage.removeItem("currentUser");
          localStorage.removeItem("userName");
          navigate("/signin", { replace: true });
          return null;
        }
        if (!response.ok) throw new Error(data.error || "Could not load your account.");
        return data.user;
      })
      .then((account) => {
        if (cancelled || !account) return;
        setUser((current) => ({
          ...current,
          name: account.name,
          email: account.email,
          className: account.class_name || "",
        }));
        localStorage.setItem("currentUser", JSON.stringify(account));
        localStorage.setItem("userName", account.name);
      })
      .catch((error) => {
        console.error("Could not verify the signed-in dashboard user.", error);
      });

    return () => { cancelled = true; };
  }, [navigate]);

  const updateMissionStats = useCallback((stats) => {
    setUser((current) => ({
      ...current,
      ecoPoints: stats.points,
      challengesDone: stats.completedCount,
      streak: stats.streak,
    }));
  }, []);

  return (
    <div className="min-h-screen font-sans relative" style={{ background: 'var(--bg)', color: 'var(--text)' }}>
      <AnimatedBackground />
      <div className="flex flex-col overflow-hidden relative z-10">
        <StudHeader user={user} activeTab={activeTab} />
        <NavigationSection />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-transparent rounded-t-3xl -mt-4 pt-8" style={{ background: 'linear-gradient(135deg, rgba(16,185,129,0.02), rgba(6,182,212,0.02))' }}>
          <DashboardContent user={user} onStatsChange={updateMissionStats} />
        </main>
      </div>
    </div>
  );
}
