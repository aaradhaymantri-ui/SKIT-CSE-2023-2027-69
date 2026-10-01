import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AnimatedBackground from "../components/AnimatedBackground.jsx";
import StudHeader from "../components/StudHeader";

const API_URL = "http://localhost:5000";
const emptyStats = { points: 0, completedCount: 0, streak: 0 };

function getAuthHeaders() {
  return { Authorization: `Bearer ${localStorage.getItem("authToken") || ""}` };
}

export default function Profile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(emptyStats);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadProfile() {
      try {
        const response = await fetch(`${API_URL}/profile`, {
          headers: getAuthHeaders()
        });
        const data = await response.json();
        if (response.status === 401) {
          localStorage.removeItem("authToken");
          localStorage.removeItem("currentUser");
          localStorage.removeItem("userName");
          navigate("/signin", { replace: true });
          return;
        }
        if (!response.ok) {
          throw new Error(data.error || "Could not load your profile.");
        }
        if (cancelled) return;
        setProfile(data.user);

        if (data.user.role === "student") {
          const missionResponse = await fetch(`${API_URL}/missions`, {
            headers: getAuthHeaders()
          });
          const missionData = await missionResponse.json();
          if (!missionResponse.ok) {
            throw new Error(missionData.error || "Could not load your eco progress.");
          }
          if (!cancelled) setStats(missionData.stats);
        }
      } catch (loadError) {
        console.error("Could not load signed-in profile.", loadError);
        if (!cancelled) setError(loadError.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadProfile();
    return () => { cancelled = true; };
  }, [navigate]);

  const headerUser = profile
    ? { name: profile.name, ecoPoints: stats.points, badges: 0 }
    : { name: "Your profile", ecoPoints: 0 };

  return (
    <div className="min-h-screen font-sans relative" style={{ background: "var(--bg)", color: "var(--text)" }}>
      <AnimatedBackground />
      <div className="relative z-10 mx-auto max-w-6xl px-4 pb-10">
        <StudHeader user={headerUser} activeTab="profile" />
        <nav className="mt-4 flex flex-wrap gap-6 rounded-2xl p-4 shadow-lg" style={{ background: "var(--panel)", border: "1px solid rgba(0,0,0,0.06)" }}>
          <Link to={profile?.role === "teacher" ? "/teacherdashboard" : "/studentdashboard"} className="nav-link">Dashboard</Link>
          {profile?.role === "student" && <Link to="/games" className="nav-link">Games</Link>}
          {profile?.role === "student" && <Link to="/learntopics" className="nav-link">Learn</Link>}
          <span className="nav-link active" aria-current="page">Profile</span>
        </nav>

        <main className="mt-6 space-y-6">
          <section className="rounded-3xl p-6 sm:p-8" style={{ background: "linear-gradient(135deg, rgba(16,185,129,0.18), rgba(6,182,212,0.18))", border: "1px solid rgba(0,0,0,0.06)" }}>
            <p className="text-sm font-semibold uppercase tracking-wider" style={{ color: "var(--primary)" }}>Personal account</p>
            <h1 className="mt-2 text-3xl font-extrabold">Your profile</h1>
            <p className="mt-2" style={{ color: "var(--muted)" }}>Only details for the account signed in on this browser are shown here.</p>
          </section>

          {loading && <p role="status" className="rounded-2xl p-6" style={{ background: "var(--panel)" }}>Loading your profile…</p>}
          {error && <p role="alert" className="rounded-2xl bg-red-50 p-4 text-red-700">{error}</p>}
          {!loading && !error && profile && (
            <>
              <section className="rounded-3xl p-6 sm:p-8" style={{ background: "var(--panel)", border: "1px solid rgba(0,0,0,0.06)", boxShadow: "0 8px 24px rgba(22,163,74,0.06)" }}>
                <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
                  <div className="flex h-20 w-20 items-center justify-center rounded-full text-3xl font-bold text-white" style={{ background: "var(--primary)" }}>
                    {profile.name?.charAt(0)?.toUpperCase() || "U"}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold">{profile.name}</h2>
                    <p style={{ color: "var(--muted)" }}>{profile.email}</p>
                    <span className="mt-2 inline-block rounded-full px-3 py-1 text-sm capitalize" style={{ background: "rgba(22,163,74,0.1)", color: "var(--primary)" }}>{profile.role} account</span>
                  </div>
                </div>
                <dl className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {[
                    ["Username", profile.username],
                    ["School", profile.school],
                    ["Class", profile.class_name],
                    ["Roll number", profile.roll_number],
                    ["Phone", profile.phone],
                    ["Email", profile.email],
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-2xl p-4" style={{ background: "rgba(0,0,0,0.03)" }}>
                      <dt className="text-sm" style={{ color: "var(--muted)" }}>{label}</dt>
                      <dd className="mt-1 break-words font-semibold">{value || "Not provided"}</dd>
                    </div>
                  ))}
                </dl>
              </section>

              {profile.role === "student" && (
                <section className="rounded-3xl p-6 sm:p-8" style={{ background: "var(--panel)", border: "1px solid rgba(0,0,0,0.06)" }}>
                  <h2 className="text-xl font-bold">Your eco progress</h2>
                  <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>These totals belong to your signed-in account.</p>
                  <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-3">
                    {[
                      ["Eco-points", stats.points, "🌱"],
                      ["Missions completed", stats.completedCount, "✅"],
                      ["Day streak", `${stats.streak} 🔥`, "📅"],
                    ].map(([label, value, icon]) => (
                      <div key={label} className="rounded-2xl p-5 text-center" style={{ background: "rgba(22,163,74,0.07)" }}>
                        <div className="text-2xl">{icon}</div>
                        <div className="mt-2 text-2xl font-bold" style={{ color: "var(--primary)" }}>{value}</div>
                        <div className="text-sm" style={{ color: "var(--muted)" }}>{label}</div>
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
