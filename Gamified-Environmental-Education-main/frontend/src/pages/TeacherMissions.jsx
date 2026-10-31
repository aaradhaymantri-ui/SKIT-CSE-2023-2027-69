import React, { useCallback, useEffect, useState } from "react";
import { API_URL, authFetch } from "../auth/api";

function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem("currentUser") || "null");
  } catch (error) {
    console.error("Could not read the signed-in user.", error);
    return null;
  }
}

const initialForm = { title: "", description: "", frequency: "daily", points: 25 };

export default function TeacherMissions() {
  const [user] = useState(getCurrentUser);
  const [missions, setMissions] = useState([]);
  const [students, setStudents] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadMissions = useCallback(async () => {
    if (!user?.email) {
      setLoading(false);
      return;
    }
    setError("");
    try {
      const response = await authFetch(`${API_URL}/teacher/missions`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Could not load class progress.");
      setMissions(data.missions);
      setStudents(data.students);
    } catch (loadError) {
      console.error("Could not load teacher mission data.", loadError);
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }, [user?.email]);

  useEffect(() => {
    loadMissions();
  }, [loadMissions]);

  async function createMission(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    setSaving(true);
    try {
      const response = await authFetch(`${API_URL}/missions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ ...form, points: Number(form.points) })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Could not assign this mission.");
      setForm(initialForm);
      setNotice(`“${data.mission.title}” was assigned to class ${data.mission.className}.`);
      await loadMissions();
    } catch (saveError) {
      console.error("Could not create eco mission.", saveError);
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="space-y-6">
      <div className="rounded-xl border border-eco-primary bg-white p-6 shadow-lg">
        <h2 className="text-xl font-bold text-eco-primary">🌿 Assign an Eco Action Mission</h2>
        <p className="mt-1 text-sm text-gray-600">Assignments go to students in your class ({user?.class_name || "class not set"}). Daily missions can be repeated each day; weekly missions each week.</p>
        {error && <p role="alert" className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
        {notice && <p role="status" className="mt-4 rounded-lg bg-green-50 p-3 text-sm text-green-700">{notice}</p>}
        {!user?.email && <p role="alert" className="mt-4 text-red-700">Sign in as a teacher to manage missions.</p>}
        <form onSubmit={createMission} className="mt-5 grid gap-4 md:grid-cols-2">
          <label className="text-sm font-medium">Mission title
            <input className="mt-1 w-full rounded-lg border border-gray-300 p-3" required maxLength="120" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
          </label>
          <label className="text-sm font-medium">Points (5–500)
            <input className="mt-1 w-full rounded-lg border border-gray-300 p-3" type="number" min="5" max="500" step="1" required value={form.points} onChange={(event) => setForm({ ...form, points: event.target.value })} />
          </label>
          <label className="text-sm font-medium">How often?
            <select className="mt-1 w-full rounded-lg border border-gray-300 p-3" value={form.frequency} onChange={(event) => setForm({ ...form, frequency: event.target.value })}>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </label>
          <label className="text-sm font-medium md:col-span-2">What should students do?
            <textarea className="mt-1 w-full rounded-lg border border-gray-300 p-3" rows="3" required maxLength="1000" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} placeholder="Describe a safe, practical eco-friendly action…" />
          </label>
          <button type="submit" disabled={saving || !user?.email} className="rounded-lg bg-eco-primary px-5 py-3 font-semibold text-white disabled:opacity-50 md:col-span-2">
            {saving ? "Assigning…" : "Assign to my class"}
          </button>
        </form>
      </div>

      <div className="rounded-xl border border-eco-primary bg-white p-6 shadow-lg">
        <h2 className="text-xl font-bold text-eco-primary">📈 Class mission progress</h2>
        {loading && <p className="mt-4 text-gray-600">Loading class progress…</p>}
        {!loading && missions.length === 0 && !error && <p className="mt-4 text-gray-600">No missions assigned yet.</p>}
        <div className="mt-4 space-y-4">
          {missions.map((mission) => (
            <article key={mission.id} className="rounded-xl border border-gray-200 p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h3 className="font-bold">{mission.title}</h3>
                  <p className="mt-1 text-sm text-gray-600">{mission.description}</p>
                </div>
                <span className="rounded-full bg-green-50 px-3 py-1 text-sm font-semibold text-green-800">{mission.frequency} · +{mission.points} EP</span>
              </div>
              <p className="mt-3 text-sm font-semibold">{mission.completedCount} of {mission.studentCount} students completed this {mission.frequency === "daily" ? "day" : "week"}</p>
              {mission.submissions.length > 0 && (
                <ul className="mt-3 divide-y divide-gray-100">
                  {mission.submissions.map((submission, index) => (
                    <li key={`${mission.id}-${submission.studentName}-${index}`} className="py-3 text-sm">
                      <span className="font-semibold">{submission.studentName}</span>
                      <p className="mt-1 text-gray-600">{submission.reflection}</p>
                      <time className="mt-1 block text-xs text-gray-400">{new Date(submission.completedAt).toLocaleString()}</time>
                    </li>
                  ))}
                </ul>
              )}
            </article>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-eco-primary bg-white p-6 shadow-lg">
        <h2 className="text-xl font-bold text-eco-primary">👩‍🎓 Student eco progress</h2>
        {students.length === 0 ? <p className="mt-3 text-sm text-gray-600">No students are registered in this class yet.</p> : (
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-left text-sm">
              <thead><tr><th className="px-3 py-2">Student</th><th className="px-3 py-2">Missions done</th><th className="px-3 py-2">Eco-points</th><th className="px-3 py-2">Day streak</th></tr></thead>
              <tbody className="divide-y divide-gray-100">
                {students.map((student) => (
                  <tr key={student.id}>
                    <td className="px-3 py-3 font-medium">{student.name}</td>
                    <td className="px-3 py-3">{student.completedCount}</td>
                    <td className="px-3 py-3">{student.points}</td>
                    <td className="px-3 py-3">{student.streak} 🔥</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
