import React, { useCallback, useEffect, useState } from "react";

const API_URL = "http://localhost:5000";

function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem("currentUser") || "null");
  } catch (error) {
    console.error("Could not read the signed-in user.", error);
    return null;
  }
}

export default function MissionBoard({ onStatsChange }) {
  const [user] = useState(getCurrentUser);
  const [missions, setMissions] = useState([]);
  const [stats, setStats] = useState({ points: 0, completedCount: 0, streak: 0 });
  const [reflections, setReflections] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submittingId, setSubmittingId] = useState(null);

  const loadMissions = useCallback(async () => {
    if (!user?.email) {
      setLoading(false);
      return;
    }

    setError("");
    try {
      const response = await fetch(
        `${API_URL}/missions`,
        { headers: { Authorization: `Bearer ${localStorage.getItem("authToken") || ""}` } }
      );
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Could not load missions.");
      }
      setMissions(data.missions);
      setStats(data.stats);
      onStatsChange?.(data.stats);
    } catch (loadError) {
      console.error("Could not load eco missions.", loadError);
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }, [onStatsChange, user?.email]);

  useEffect(() => {
    loadMissions();
  }, [loadMissions]);

  async function submitMission(missionId) {
    setError("");
    setSubmittingId(missionId);
    try {
      const response = await fetch(`${API_URL}/missions/${missionId}/complete`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken") || ""}`
        },
        body: JSON.stringify({
          reflection: reflections[missionId] || ""
        })
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Could not submit this mission.");
      }
      setStats(data.stats);
      setReflections((current) => ({ ...current, [missionId]: "" }));
      await loadMissions();
    } catch (submitError) {
      console.error("Could not submit eco mission.", submitError);
      setError(submitError.message);
    } finally {
      setSubmittingId(null);
    }
  }

  return (
    <section className="rounded-3xl p-6 sm:p-8" style={{ background: "var(--panel)", border: "1px solid rgba(0,0,0,0.06)" }}>
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wider" style={{ color: "var(--primary)" }}>Learn it, do it</p>
          <h2 className="text-2xl font-bold mt-1">Eco Action Missions 🌱</h2>
          <p className="mt-2" style={{ color: "var(--muted)" }}>Take a small real-world action, then share what you noticed.</p>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="rounded-xl px-3 py-2" style={{ background: "rgba(22,163,74,0.08)" }}>
            <strong className="block text-lg">{stats.points}</strong><span className="text-xs">Points</span>
          </div>
          <div className="rounded-xl px-3 py-2" style={{ background: "rgba(6,182,212,0.08)" }}>
            <strong className="block text-lg">{stats.completedCount}</strong><span className="text-xs">Done</span>
          </div>
          <div className="rounded-xl px-3 py-2" style={{ background: "rgba(245,158,11,0.12)" }}>
            <strong className="block text-lg">{stats.streak} 🔥</strong><span className="text-xs">Day streak</span>
          </div>
        </div>
      </div>

      {error && <p role="alert" className="mt-5 rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {!user?.email && <p className="mt-5 rounded-xl bg-amber-50 p-4 text-amber-800">Sign in to see missions assigned to your class.</p>}
      {loading && <p className="mt-5" style={{ color: "var(--muted)" }}>Loading class missions…</p>}
      {!loading && user?.email && missions.length === 0 && !error && (
        <p className="mt-5 rounded-xl p-4" style={{ background: "rgba(22,163,74,0.06)", color: "var(--muted)" }}>
          No missions have been assigned to your class yet. Check back soon!
        </p>
      )}

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        {missions.map((mission) => (
          <article key={mission.id} className="rounded-2xl p-5" style={{ border: "1px solid rgba(0,0,0,0.08)", background: mission.completed ? "rgba(22,163,74,0.05)" : "#fff" }}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wide" style={{ color: "var(--primary)" }}>{mission.frequency} mission</span>
                <h3 className="mt-1 text-lg font-bold">{mission.title}</h3>
              </div>
              <span className="shrink-0 rounded-full px-3 py-1 text-sm font-semibold" style={{ background: "rgba(245,158,11,0.14)", color: "#92400e" }}>+{mission.points} EP</span>
            </div>
            <p className="mt-3 text-sm" style={{ color: "var(--muted)" }}>{mission.description}</p>
            {mission.completed ? (
              <div className="mt-4 rounded-xl p-3 text-sm" style={{ background: "rgba(22,163,74,0.1)", color: "#166534" }}>
                Completed for this {mission.frequency === "daily" ? "day" : "week"} ✓
                {mission.reflection && <p className="mt-1 text-xs">Your reflection: {mission.reflection}</p>}
              </div>
            ) : (
              <div className="mt-4">
                <label className="block text-sm font-medium" htmlFor={`reflection-${mission.id}`}>What did you do or notice?</label>
                <textarea
                  id={`reflection-${mission.id}`}
                  className="mt-2 w-full rounded-xl border border-gray-200 p-3 text-sm"
                  rows="3"
                  maxLength="500"
                  minLength="10"
                  required
                  value={reflections[mission.id] || ""}
                  onChange={(event) => setReflections((current) => ({ ...current, [mission.id]: event.target.value }))}
                  placeholder="Write a short reflection (at least 10 characters)…"
                />
                <button
                  type="button"
                  disabled={submittingId === mission.id || (reflections[mission.id] || "").trim().length < 10}
                  onClick={() => submitMission(mission.id)}
                  className="mt-2 rounded-full px-5 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
                  style={{ background: "var(--primary)" }}
                >
                  {submittingId === mission.id ? "Submitting…" : "Mark mission complete"}
                </button>
              </div>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
