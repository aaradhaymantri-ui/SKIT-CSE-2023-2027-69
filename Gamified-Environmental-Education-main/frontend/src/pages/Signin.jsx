import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles/Signin.css";
import AnimatedBackground from "../components/AnimatedBackground.jsx";
import { useAuth } from "../auth/AuthContext";

const Signin = () => {
  const navigate = useNavigate(); // hook to redirect
  const { signIn } = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const user = await signIn(formData.email, formData.password);
      navigate(user.role === "teacher" ? "/teacherdashboard" : "/studentdashboard");
    } catch (err) {
      console.error("Error during signin:", err);
      alert(err.message || "Something went wrong!");
    }
  };

  return (
    <div className="signin-container">
      <AnimatedBackground />
      <form className="signin-form" onSubmit={handleSubmit}>
        <h2>Sign In</h2>

        <label>Email</label>
        <input
          type="email"
          name="email"
          placeholder="Enter your email"
          value={formData.email}
          onChange={handleChange}
          required
        />

        <label>Password</label>
        <input
          type="password"
          name="password"
          placeholder="Enter your password"
          value={formData.password}
          onChange={handleChange}
          required
        />

        <button type="submit">Sign In</button>

        <p className="link-text">
          Don't have an account? <Link to="/signup">Sign Up</Link>
        </p>
      </form>
    </div>
  );
};

export default Signin;
