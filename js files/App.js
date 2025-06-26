import React, { useState, useEffect } from "react";
import SideNav from "./SideNav";
import getPageContent from "./SwitchPage";
import AuthPage from "./AuthPage";
import DarkMode from "./DarkMode.js"


function App() {
  const [page, setPage] = useState("authpage");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user information is stored in local storage to manage authentication state
    const user = JSON.parse(localStorage.getItem('user'));
    if (user && user.name) {
      setIsAuthenticated(true);
      setPage("start"); // Direct user to start page if already logged in
    }
  }, []);

  // Redirects user to start page upon successful login
  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
    setPage("start");
  };

  // Redirects user to authentiocation page upon logout
  const handleLogout = () => {
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setPage("authpage");
  };
  
  <DarkMode/>
  return (
    <div>
      {isAuthenticated ? (
        <>
          <SideNav setPage={setPage} onLogout={handleLogout} />
          {getPageContent(page)}
        </>
      ) : (
        <AuthPage onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App;
