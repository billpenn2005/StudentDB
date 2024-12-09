// src/components/ProtectedRoute.js

import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { Spin } from 'antd';

const ProtectedRoute = ({ children }) => {
    const { isAuthenticated, loading } = useContext(AuthContext);

    if (loading) return <div style={styles.loading}><Spin tip="加载中..." size="large" /></div>;

    return isAuthenticated ? children : <Navigate to="/login" />;
};

const styles = {
    loading: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
    },
};

export default ProtectedRoute;
