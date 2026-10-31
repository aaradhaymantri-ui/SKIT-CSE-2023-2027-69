import React, { useState } from 'react';
import "../styles/Signup.css";
import { Link } from "react-router-dom";
import AnimatedBackground from "../components/AnimatedBackground.jsx";
import { API_URL } from "../auth/api";

const usernamePattern = /^[A-Za-z0-9_-]+$/;
const emailPattern = new RegExp(
  "^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\\.)+[A-Za-z](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$",
  "u"
);

const Signup = () => {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [nameWarning, setNameWarning] = useState("");
  const [usernameWarning, setUsernameWarning] = useState("");
  const [emailWarning, setEmailWarning] = useState("");
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
    if (e.target.name === "name") {
      const normalizedName = e.target.value.trim().replace(/\s+/g, " ");
      const validName =
        !normalizedName || /^[\p{L}]+(?:[ '\u2019.-][\p{L}]+)*$/u.test(normalizedName);
      setNameWarning(
        normalizedName && !validName
          ? "Name must use letters only (spaces, apostrophes, periods, and hyphens are okay)."
          : ""
      );
      e.target.setCustomValidity(
        validName
          ? ""
          : "Enter a name using letters, spaces, apostrophes, periods, or hyphens"
      );
    } else if (e.target.name === "username") {
      const normalizedUsername = e.target.value.trim();
      const validUsername =
        !normalizedUsername || usernamePattern.test(normalizedUsername);
      setUsernameWarning(
        normalizedUsername && !validUsername
          ? "Use only English letters, numbers, underscores, or hyphens."
          : ""
      );
      e.target.setCustomValidity(
        validUsername ? "" : "Use only letters, numbers, underscores, or hyphens"
      );
    } else if (e.target.name === "email") {
      const normalizedEmail = e.target.value.trim();
      const validEmail = !normalizedEmail || emailPattern.test(normalizedEmail);
      setEmailWarning(
        normalizedEmail && !validEmail ? "Enter an email in the format name@example.com." : ""
      );
      e.target.setCustomValidity(
        validEmail ? "" : "Enter a valid email address"
      );
    } else if (["rollNumber", "school", "className"].includes(e.target.name)) {
      const isRequired = e.target.required;
      e.target.setCustomValidity(
        isRequired && !e.target.value.trim() ? "This field cannot be blank." : ""
      );
    }
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

const handleSubmit = async (e) => {
  e.preventDefault();
  setMessage("");
  setError("");
  if (formData.password !== formData.confirmPassword) {
    setError("Passwords do not match.");
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
    if (!response.ok) {
      setError(result.error || "Unable to create your account.");
      return;
    }
    setMessage(result.message);
  } catch (err) {
    console.error(err);
    setError("Unable to contact the signup service. Please try again.");
  }
};

  return (
    <div className="signup-container">
      <AnimatedBackground />
      <form className="signup-form" onSubmit={handleSubmit}>
        <h2>Sign Up</h2>
        {message && <p className="signup-feedback" role="status">{message}</p>}
        {error && <p className="signup-feedback signup-feedback-error" role="alert">{error}</p>}
        <input type="text" name="name" placeholder="Full Name" value={formData.name} onChange={handleChange} title="Enter a name using letters, spaces, apostrophes, periods, or hyphens" maxLength="100" aria-invalid={Boolean(nameWarning)} aria-describedby={nameWarning ? "signup-name-warning" : undefined} required />
        {nameWarning && <p className="signup-field-warning" id="signup-name-warning" role="alert">{nameWarning}</p>}
        <input type="text" name="username" placeholder="Username (shown as BOT username)" value={formData.username} onChange={handleChange} minLength="3" maxLength="30" title="Use 3–30 English letters, numbers, underscores, or hyphens" aria-invalid={Boolean(usernameWarning)} aria-describedby={usernameWarning ? "signup-username-warning" : undefined} required />
        {usernameWarning && <p className="signup-field-warning" id="signup-username-warning" role="alert">{usernameWarning}</p>}
        <input type="tel" name="phone" placeholder="10-digit Phone Number" value={formData.phone} onChange={handleChange} inputMode="numeric" pattern="[0-9]{10}" maxLength="10" title="Enter exactly 10 digits" required />
        <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleChange} maxLength="100" title="Enter a valid email address" aria-invalid={Boolean(emailWarning)} aria-describedby={emailWarning ? "signup-email-warning" : undefined} required />
        {emailWarning && <p className="signup-field-warning" id="signup-email-warning" role="alert">{emailWarning}</p>}
        <input type="text" name="rollNumber" placeholder="Roll Number (students)" value={formData.rollNumber} onChange={handleChange} maxLength="50" required={formData.role === 'student'} />
        <input type="text" name="school" placeholder="School" value={formData.school} onChange={handleChange} maxLength="100" required />
        <input type="text" name="className" placeholder="Class" value={formData.className} onChange={handleChange} maxLength="50" required />
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
