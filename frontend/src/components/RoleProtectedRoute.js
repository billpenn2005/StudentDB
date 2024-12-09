// src/components/RoleProtectedRoute.js

import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { Spin } from 'antd';

const RoleProtectedRoute = ({ children, roles }) => {
    const { isAuthenticated, user, loading } = useContext(AuthContext);
    console.log(roles);
    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
                <Spin tip="加载中..." size="large" />
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/" />;
    }

    const userGroups = roles;
    const hasRole = roles.some(role => userGroups.includes(role));

    if (!hasRole) {
        return <Navigate to="/" />;
    }

    return children;
};

export default RoleProtectedRoute;
