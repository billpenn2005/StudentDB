// src/components/RoleProtectedRoute.js

import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { Spin } from 'antd';

const RoleProtectedRoute = ({ children, roles }) => {
    const { isAuthenticated, user, loading } = useContext(AuthContext);

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
                <Spin tip="加载中..." size="large" />
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/" replace />;
    }

    if (!user || !user.groups) {
        // 如果用户信息不完整，重定向到首页或错误页面
        return <Navigate to="/" replace />;
    }

    // 提取用户所属的组名称，并转换为小写以进行不区分大小写的比较
    const userGroups = user.groups.map(group => group.toLowerCase());

    // 转换允许的角色为小写
    const allowedRoles = roles.map(role => role.toLowerCase());

    // 检查用户是否拥有任何一个允许的角色
    const hasRole = allowedRoles.some(role => userGroups.includes(role));

    if (!hasRole) {
        return <Navigate to="/" replace />;
    }

    return children;
};

export default RoleProtectedRoute;
