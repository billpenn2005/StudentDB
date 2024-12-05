import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [userRole, setUserole] = useState('');

  const handleLogin = (username, userrole) => {
    setUsername(username);
    setIsLoggedIn(true);
    setUserole(userrole);
  };

  const handleLogout = () => {
    setUsername('');
    setIsLoggedIn(false);
    setUserole('');
  };

  return (
    <Router>
      <div>
        <Routes>
          <Route path="/" element={isLoggedIn ? <Dashboard username={username} onLogout={handleLogout} userRole={userRole}  /> : <Login onLogin={handleLogin} />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
