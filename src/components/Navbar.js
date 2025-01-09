import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import PropTypes from "prop-types";

function Navbar({ username, onLogout }) {
  const [menuVisible, setMenuVisible] = useState(false);
  const location = useLocation();

  // Close the dropdown menu when clicking outside
  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (!event.target.closest(".profile-menu")) {
        setMenuVisible(false);
      }
    };

    document.addEventListener("click", handleOutsideClick);
    return () => {
      document.removeEventListener("click", handleOutsideClick);
    };
  }, []);

  return (
    <nav className="navbar">
      <ul className="nav-list">
        <li className={`nav-item ${location.pathname === "/active-triggers" ? "active" : ""}`}>
          <Link to="/active-triggers" className="nav-link">
            Active Triggers
          </Link>
        </li>
        <li className={`nav-item ${location.pathname === "/inactive-triggers" ? "active" : ""}`}>
          <Link to="/inactive-triggers" className="nav-link">
            Inactive Triggers
          </Link>
        </li>
        <li className={`nav-item ${location.pathname === "/previous-triggers" ? "active" : ""}`}>
          <Link to="/previous-triggers" className="nav-link">
            Alerts Table
          </Link>
        </li>
        <li className={`nav-item ${location.pathname === "/hni-details" ? "active" : ""}`}>
          <Link to="/hni-details" className="nav-link">
            HNI Details
          </Link>
        </li>
      </ul>
      <div className="profile-menu">
        <button
          className="menu-button"
          onClick={() => setMenuVisible((prev) => !prev)}
          aria-label="Toggle profile menu"
        >
          ☰
        </button>
        {menuVisible && (
          <div className="dropdown-menu" role="menu">
            <p className="greeting">Hi, {username}</p>
            <button className="logout-button" onClick={onLogout} role="menuitem">
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}

Navbar.propTypes = {
  username: PropTypes.string.isRequired,
  onLogout: PropTypes.func.isRequired,
};

export default Navbar;
