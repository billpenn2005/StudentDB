import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import axios from 'axios';

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [userRole, setUserole] = useState('');

  // 使用 useEffect 在组件加载时读取 localStorage 中的状态
  useEffect(() => {
    const storedUsername = localStorage.getItem('username');
    const storedRole = localStorage.getItem('userRole');
    if (storedUsername && storedRole) {
      setIsLoggedIn(true);
      setUsername(storedUsername);
      setUserole(storedRole);
    }
  }, []);

  const handleLogin = (username, userrole) => {
    // 登录时保存状态到 localStorage
    localStorage.setItem('username', username);
    localStorage.setItem('userRole', userrole);
    
    setUsername(username);
    setIsLoggedIn(true);
    setUserole(userrole);
  };

  const handleLogout = () => {
    // 注销时清除 localStorage
    localStorage.removeItem('username');
    localStorage.removeItem('userRole');
    
    setUsername('');
    setIsLoggedIn(false);
    setUserole('');
  };

  return (
    <Router>
      <div>
        <Routes>
          <Route 
            path="/" 
            element={isLoggedIn ? <Dashboard username={username} onLogout={handleLogout} userRole={userRole} /> : <Login onLogin={handleLogin} />}
          />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
