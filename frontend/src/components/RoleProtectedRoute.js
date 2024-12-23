// src/components/RoleProtectedRoute.js

import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

const RoleProtectedRoute = ({ roles, children }) => {
    const { isAuthenticated, user, loading } = useContext(AuthContext);

    if (loading) {
        return null; // 或者显示一个加载指示器
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    const userGroups = user?.groups?.map(g => g.trim().toLowerCase()) || [];

    const hasRole = roles.some(role => userGroups.includes(role.toLowerCase()));

    if (!hasRole) {
        return <Navigate to="/" replace />; // 或者显示403页面
    }

    return children;
};

export default RoleProtectedRoute;
