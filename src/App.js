import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import ActiveTriggersPage from "./pages/ActiveTriggersPage";
import InactiveTriggersPage from "./pages/InactiveTriggersPage";
import PreviousTriggersPage from "./pages/PreviousTriggersPage";
import HNIDetailsPage from "./pages/HNIDetailsPage";
import Navbar from "./components/Navbar";
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");

  useEffect(() => {
    // Check if the user is logged in (user_id in localStorage)
    const userId = localStorage.getItem("user_id");
    const savedUsername = localStorage.getItem("username");
    if (userId) {
      setIsLoggedIn(true);
      setUsername(savedUsername || "");
    }
  }, []);

  const handleLogout = () => {
    localStorage.clear(); // Clear user data
    setIsLoggedIn(false);
  };

  const currentYear = new Date().getFullYear(); // Get the current year

  return (
    <Router>
      <div id="app-container">
        {isLoggedIn && (
          <header id="app-header" className="navbar-container">
            <Navbar username={username} onLogout={handleLogout} />
          </header>
        )}
        <main id="app-main" className="content-container">
          <Routes>
            <Route
              path="/"
              element={
                isLoggedIn ? (
                  <Navigate to="/active-triggers" replace />
                ) : (
                  <LoginPage setIsLoggedIn={setIsLoggedIn} setUsername={setUsername} />
                )
              }
            />
            <Route
              path="/active-triggers"
              element={isLoggedIn ? <ActiveTriggersPage /> : <Navigate to="/" replace />}
            />
            <Route
              path="/Inactive-triggers"
              element={isLoggedIn ? <InactiveTriggersPage /> : <Navigate to="/" replace />}
            />
            <Route
              path="/previous-triggers"
              element={isLoggedIn ? <PreviousTriggersPage /> : <Navigate to="/" replace />}
            />
            <Route
              path="/hni-details"
              element={isLoggedIn ? <HNIDetailsPage /> : <Navigate to="/" replace />}
            />
          </Routes>
        </main>
        <footer id="app-footer" className="footer-container">
          <p>&copy; {currentYear} Stock Alert App</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
