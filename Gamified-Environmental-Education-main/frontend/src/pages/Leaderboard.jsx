import React, { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import StudHeader from "../components/StudHeader";
import AnimatedBackground from "../components/AnimatedBackground.jsx";
import { API_URL, authFetch } from "../auth/api";
const periods = [
  { value: "weekly", label: "This Week" },
  { value: "monthly", label: "This Month" },
  { value: "allTime", label: "All Time" }
];

function clearSession() {
  localStorage.removeItem("currentUser");
  localStorage.removeItem("userName");
}

function getSignedInUser() {
  try {
    return JSON.parse(localStorage.getItem("currentUser") || "null");
  } catch (error) {
    console.error("Could not read the signed-in user.", error);
    return null;
  }
}

export default function Leaderboard() {
  const navigate = useNavigate();
  const [period, setPeriod] = useState("weekly");
  const [bots, setBots] = useState([]);
  const [user, setUser] = useState(getSignedInUser);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadLeaderboard = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [profileResponse, leaderboardResponse] = await Promise.all([
        authFetch(`${API_URL}/profile`),
        authFetch(`${API_URL}/leaderboard?period=${period}`)
      ]);
      const [profileData, leaderboardData] = await Promise.all([
        profileResponse.json(),
        leaderboardResponse.json()
      ]);

      if (profileResponse.status === 401 || leaderboardResponse.status === 401) {
        clearSession();
        navigate("/signin", { replace: true });
        return;
      }
      if (!profileResponse.ok) {
        throw new Error(profileData.error || "Could not verify your account.");
      }
      if (!leaderboardResponse.ok) {
        throw new Error(leaderboardData.error || "Could not load the bot leaderboard.");
      }
      setUser(profileData.user);
      setBots(leaderboardData.bots);
    } catch (loadError) {
      console.error("Could not load the bot leaderboard.", loadError);
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }, [navigate, period]);

  useEffect(() => {
    loadLeaderboard();
  }, [loadLeaderboard]);

  const rankedBots = bots.map((bot, index) => ({ ...bot, rank: index + 1 }));
  const podiumOrder = rankedBots.length > 1
    ? [rankedBots[1], rankedBots[0], rankedBots[2]].filter(Boolean)
    : rankedBots;

  return (
    <div className="min-h-screen font-sans relative" style={{ background: "var(--bg)", color: "var(--text)" }}>
      <AnimatedBackground />
      <div className="relative z-10 flex flex-col overflow-hidden">
        <StudHeader user={{ name: user?.name || "Student", ecoPoints: 0, badges: 0 }} activeTab="leaderboard" />
        <nav className="mx-auto mt-4 flex w-full max-w-6xl flex-wrap items-center gap-6 rounded-2xl px-6 py-4 shadow-lg" style={{ background: "var(--panel)", border: "1px solid rgba(0,0,0,0.06)" }}>
          <Link to="/studentdashboard" className="nav-link">Dashboard</Link>
          <Link to="/games" className="nav-link">Games</Link>
          <Link to="/learntopics" className="nav-link">Learn</Link>
          <span className="nav-link active" aria-current="page">Leaderboard</span>
          <Link to="/profile" className="nav-link">Profile</Link>
        </nav>

        <main className="mx-auto w-full max-w-6xl px-6 py-8">
          <section className="rounded-3xl p-6 text-center sm:p-8" style={{ background: "linear-gradient(135deg, rgba(16,185,129,0.18), rgba(6,182,212,0.18))", border: "1px solid rgba(0,0,0,0.06)" }}>
            <p className="text-sm font-semibold uppercase tracking-wider" style={{ color: "var(--primary)" }}>Class bot rankings</p>
            <h1 className="mt-2 text-3xl font-extrabold sm:text-4xl">🤖 Eco Bot Leaderboard</h1>
            <p className="mt-2" style={{ color: "var(--muted)" }}>Student accounts appear as BOT usernames. Only bots in your class are listed.</p>
          </section>

          <section className="mt-6 flex flex-wrap justify-center gap-3 rounded-3xl p-5" style={{ background: "var(--panel)", border: "1px solid rgba(0,0,0,0.06)" }}>
            {periods.map((option) => (
              <button
                key={option.value}
                type="button"
                aria-pressed={period === option.value}
                onClick={() => setPeriod(option.value)}
                className={`rounded-2xl px-6 py-3 font-semibold transition-all ${period === option.value ? "text-white shadow-lg" : "hover:shadow-md"}`}
                style={period === option.value
                  ? { background: "linear-gradient(135deg, var(--primary), var(--secondary))" }
                  : { background: "rgba(0,0,0,0.03)", color: "var(--text)" }}
              >
                {option.label}
              </button>
            ))}
          </section>

          {error && (
            <div role="alert" className="mt-6 rounded-2xl bg-red-50 p-4 text-red-700">
              <p>{error}</p>
              <button type="button" className="mt-2 font-semibold underline" onClick={loadLeaderboard}>Try again</button>
            </div>
          )}

          {loading ? (
            <div role="status" className="mt-6 rounded-3xl p-12 text-center" style={{ background: "var(--panel)" }}>
              <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-t-2" style={{ borderColor: "var(--primary)" }} />
              <p className="mt-4" style={{ color: "var(--muted)" }}>Loading class bots…</p>
            </div>
          ) : !error && rankedBots.length === 0 ? (
            <div className="mt-6 rounded-3xl p-10 text-center" style={{ background: "var(--panel)", border: "1px solid rgba(0,0,0,0.06)" }}>
              <div className="text-5xl">🤖</div>
              <h2 className="mt-4 text-xl font-bold">No class bots yet</h2>
              <p className="mt-2" style={{ color: "var(--muted)" }}>Student accounts in your class will appear here after they sign up.</p>
            </div>
          ) : !error && (
            <>
              <section className="mt-6 rounded-3xl p-6 sm:p-8" style={{ background: "var(--panel)", border: "1px solid rgba(0,0,0,0.06)", boxShadow: "0 8px 24px rgba(22,163,74,0.06)" }}>
                <h2 className="mb-8 text-center text-2xl font-bold">🏆 Top Bots</h2>
                <div className="flex flex-wrap items-end justify-center gap-8">
                  {podiumOrder.map((bot) => (
                    <div key={bot.id} className="flex flex-col items-center">
                      <div className="relative flex h-20 w-20 items-center justify-center rounded-full text-4xl" style={{ background: "rgba(22,163,74,0.1)" }}>
                        🤖
                        <span className="absolute -bottom-2 -right-2 flex h-8 w-8 items-center justify-center rounded-full border-2 border-white text-sm font-bold text-white" style={{ background: bot.rank === 1 ? "#fbbf24" : bot.rank === 2 ? "#9ca3af" : "#fb923c" }}>{bot.rank}</span>
                      </div>
                      <h3 className="mt-3 font-semibold">{bot.name}</h3>
                      <p className="font-bold" style={{ color: "var(--primary)" }}>{bot.ecoPoints} pts</p>
                    </div>
                  ))}
                </div>
              </section>

              <section className="mt-6 overflow-hidden rounded-3xl" style={{ background: "var(--panel)", border: "1px solid rgba(0,0,0,0.06)", boxShadow: "0 8px 24px rgba(22,163,74,0.06)" }}>
                <div className="p-6">
                  <h2 className="text-xl font-bold">Complete Bot Rankings</h2>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-left">
                    <thead style={{ background: "rgba(22,163,74,0.05)" }}>
                      <tr>
                        {["Rank", "Bot", "Eco Points", "Missions"].map((heading) => (
                          <th key={heading} className="px-6 py-4 text-sm font-semibold uppercase tracking-wider" style={{ color: "var(--muted)" }}>{heading}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y" style={{ divideColor: "rgba(0,0,0,0.06)" }}>
                      {rankedBots.map((bot) => (
                        <tr key={bot.id} style={bot.isCurrentUser ? { background: "rgba(22,163,74,0.1)" } : undefined}>
                          <td className="px-6 py-4"><span className="inline-flex h-8 w-8 items-center justify-center rounded-full font-bold" style={{ color: "var(--text)" }}>{bot.rank}</span></td>
                          <td className="px-6 py-4 font-medium">🤖 {bot.name}{bot.isCurrentUser && <span className="ml-2 rounded-full px-2 py-1 text-xs text-white" style={{ background: "var(--primary)" }}>You</span>}</td>
                          <td className="px-6 py-4 font-bold" style={{ color: "var(--primary)" }}>{bot.ecoPoints}</td>
                          <td className="px-6 py-4">{bot.missionsCompleted}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
