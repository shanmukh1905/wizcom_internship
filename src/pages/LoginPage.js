import React, { useState } from "react";
import axios from "axios";

function LoginPage({ setIsLoggedIn, setUsername }) {
  const [username, setLocalUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:5000/login", {
        username,
        password,
      });

      if (response.data.success) {
        localStorage.setItem("user_id", response.data.user_id);
        localStorage.setItem("username", username);
        setUsername(username);
        setIsLoggedIn(true);
      } else {
        setError("Invalid username or password");
      }
    } catch (err) {
      setError("Error logging in. Please try again.");
    }
  };

  return (
    <div id="login-page" className="page-container">
      <center>
      <h2 className="login-title">Login</h2>
      <form id="login-form" className="form-container1" onSubmit={handleLogin}>
        <div className="form-group1">
          <label htmlFor="username" className="form-label">
            Username
          </label>
          <input
            id="username"
            className="form-input1"
            type="text"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setLocalUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group1">
          <label htmlFor="password" className="form-label">
            Password
          </label>
          <input
            id="password"
            className="form-input1"
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div className="form-actions1">
          <button id="login-button" className="form-button" type="submit">
            Login
          </button>
        </div>
      </form>
      {error && (
        <p id="login-error" className="error-message">
          {error}
        </p>
      )}
      </center>
    </div>
  );
}

export default LoginPage;
