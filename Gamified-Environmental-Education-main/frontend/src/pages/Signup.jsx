import React, { useState } from 'react';
import "../styles/Signup.css";
import { Link } from "react-router-dom";
import AnimatedBackground from "../components/AnimatedBackground.jsx";
import { API_URL } from "../auth/api";


const Signup = () => {
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    phone: '',
    email: '',
    rollNumber: '', 
    school: '',
    className: '',
    role: 'student',
    teacherSignupCode: '',
    password: '',
    confirmPassword: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

const handleSubmit = async (e) => {
  e.preventDefault();
  if (formData.password !== formData.confirmPassword) {
    alert("Passwords do not match!");
    return;
  }

  try {
    const response = await fetch(`${API_URL}/signup`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });
    const result = await response.json();
    alert(result.message || result.error);
  } catch (err) {
    console.error(err);
    alert("Something went wrong");
  }
};


  return (
    <div className="signup-container">
      <AnimatedBackground />
      <form className="signup-form" onSubmit={handleSubmit}>
        <h2>Sign Up</h2>
        <input type="text" name="name" placeholder="Full Name" value={formData.name} onChange={handleChange} required />
        <input type="text" name="username" placeholder="Username (shown as BOT username)" value={formData.username} onChange={handleChange} minLength="3" maxLength="30" pattern="[A-Za-z0-9_-]+" title="Use 3–30 letters, numbers, underscores, or hyphens" required />
        <input type="text" name="phone" placeholder="Phone Number" value={formData.phone} onChange={handleChange} required />
        <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleChange} required />
        <input type="text" name="rollNumber" placeholder="Roll Number (students)" value={formData.rollNumber} onChange={handleChange} required={formData.role === 'student'} />
        <input type="text" name="school" placeholder="School" value={formData.school} onChange={handleChange} required />
        <input type="text" name="className" placeholder="Class" value={formData.className} onChange={handleChange} required />
        <select name="role" value={formData.role} onChange={handleChange} required>
          <option value="student">Student account</option>
          <option value="teacher">Teacher account</option>
        </select>
        {formData.role === 'teacher' && (
          <input
            type="password"
            name="teacherSignupCode"
            placeholder="Teacher invitation code"
            value={formData.teacherSignupCode}
            onChange={handleChange}
            required
          />
        )}
        <input type="password" name="password" placeholder="Password (8–128 characters)" value={formData.password} onChange={handleChange} minLength="8" maxLength="128" required />
        <input type="password" name="confirmPassword" placeholder="Confirm Password" value={formData.confirmPassword} onChange={handleChange} required />
        <button type="submit">Sign Up</button>
        <p>Already have an account? <Link to="/signin">Sign in</Link></p>
      </form>
    </div>
  );
};

export default Signup;
