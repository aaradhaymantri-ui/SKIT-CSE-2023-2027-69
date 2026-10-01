import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const StudHeader = ({ user = { name: "", ecoPoints: 0 }, activeTab }) => {
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [signedInUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("currentUser") || "null");
    } catch (error) {
      console.error("Could not read the signed-in user.", error);
      return null;
    }
  });
  const navigate = useNavigate();
  const displayUser = {
    ...user,
    name: signedInUser?.name || (localStorage.getItem("authToken") ? user.name : "Guest"),
    role: signedInUser?.role || "student",
    ecoPoints: user.ecoPoints || 0,
    badges: user.badges || 0,
  };

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("currentUser");
    localStorage.removeItem("userName");
    navigate('/');
  };

  return (
    <header className="rounded-3xl shadow-sm mt-4" style={{ background: 'var(--panel)', border: '1px solid rgba(0,0,0,0.06)' }}>
      <div className="max-w-6xl mx-auto px-10 py-4 flex justify-between items-center">
        <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity duration-200 cursor-pointer">
          <div className="text-3xl animate-pulse">🌍</div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-green-600 via-emerald-500 to-teal-500 bg-clip-text text-transparent">
            Eco Champs
          </h1>
          <div className="text-2xl">🏆</div>
        </Link>

        <div className="flex items-center gap-4">
          <div className="text-sm font-semibold px-4 py-2 rounded-xl flex items-center gap-2" style={{ background: 'rgba(245,158,11,0.15)', color: '#92400e' }}>
            <span>{displayUser.ecoPoints} Eco-Points</span>
          </div>
          
          {/* Profile Dropdown */}
          <div className="relative">
            <div 
              className="w-10 h-10 rounded-full text-white flex items-center justify-center font-bold text-lg cursor-pointer hover:scale-105 transition-transform duration-200" 
              style={{ background: 'var(--primary)' }}
              onMouseEnter={() => setShowProfileDropdown(true)}
              onMouseLeave={() => setShowProfileDropdown(false)}
            >
              {displayUser.name ? displayUser.name.charAt(0) : "?"}
            </div>

            {/* Dropdown Menu */}
            {showProfileDropdown && (
              <div 
                className="absolute right-0 top-12 w-64 rounded-2xl shadow-2xl border z-50 overflow-hidden"
                style={{ background: 'var(--panel)', borderColor: 'rgba(22,163,74,0.2)' }}
                onMouseEnter={() => setShowProfileDropdown(true)}
                onMouseLeave={() => setShowProfileDropdown(false)}
              >
                {/* Profile Header */}
                <div className="p-4" style={{ background: 'linear-gradient(135deg, rgba(16,185,129,0.1), rgba(6,182,212,0.1))' }}>
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full text-white flex items-center justify-center font-bold text-xl" style={{ background: 'var(--primary)' }}>
                      {displayUser.name ? displayUser.name.charAt(0) : "?"}
                    </div>
                    <div>
                      <h3 className="font-bold text-lg" style={{ color: 'var(--text)' }}>{displayUser.name || "Guest"}</h3>
                      <p className="text-sm capitalize" style={{ color: 'var(--muted)' }}>{displayUser.role} account 🌱</p>
                    </div>
                  </div>
                </div>

                {/* Stats */}
                <div className="p-4 border-b" style={{ borderColor: 'rgba(0,0,0,0.06)' }}>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="text-center p-2 rounded-xl" style={{ background: 'rgba(22,163,74,0.08)' }}>
                      <div className="font-bold text-lg" style={{ color: 'var(--primary)' }}>{displayUser.ecoPoints}</div>
                      <div className="text-xs" style={{ color: 'var(--muted)' }}>Eco-Points</div>
                    </div>
                    <div className="text-center p-2 rounded-xl" style={{ background: 'rgba(245,158,11,0.1)' }}>
                      <div className="font-bold text-lg" style={{ color: '#ca8a04' }}>{displayUser.badges}</div>
                      <div className="text-xs" style={{ color: 'var(--muted)' }}>Badges</div>
                    </div>
                  </div>
                </div>

                {/* Menu Items */}
                <div className="p-2">
                  <Link 
                    to="/profile" 
                    className="flex items-center gap-3 p-3 rounded-xl hover:bg-opacity-80 transition-all duration-200"
                    style={{ background: 'rgba(22,163,74,0.05)' }}
                  >
                    <span className="text-lg">👤</span>
                    <span className="font-medium" style={{ color: 'var(--text)' }}>View Profile</span>
                  </Link>
                  
                  <button 
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-opacity-80 transition-all duration-200 mt-1"
                    style={{ background: 'rgba(239,68,68,0.08)', color: '#dc2626' }}
                  >
                    <span className="text-lg">🚪</span>
                    <span className="font-medium">Logout</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default StudHeader;   // ✅ required
