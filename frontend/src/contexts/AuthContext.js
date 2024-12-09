// src/contexts/AuthContext.js

import React, { createContext, useState, useEffect } from 'react';
import axiosInstance from '../axiosInstance';
import { toast } from 'react-toastify';
import { useNavigate, useLocation } from 'react-router-dom';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('access_token'));
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const location = useLocation(); // 获取当前路径

    const fetchUser = async () => {
        try {
            const response = await axiosInstance.get('user/');
            setUser(response.data);
            setIsAuthenticated(true);
            console.log('Fetched User:', response.data); // 调试日志
        } catch (err) {
            console.error(err);
            setIsAuthenticated(false);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            toast.error('用户信息获取失败，请重新登录');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (isAuthenticated) {
            fetchUser();
        } else {
            setLoading(false);
        }
    }, [isAuthenticated]);

    const login = (accessToken, refreshToken) => {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        setIsAuthenticated(true);
        fetchUser();
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setIsAuthenticated(false);
        setUser(null);
        toast.info('已注销');
        navigate('/'); // 重定向到首页
    };

    // 监听用户数据变化以进行跳转
    useEffect(() => {
        if (user) {
            const userGroups = user.groups.map(group => group.name);
            console.log('User Groups:', userGroups); // 调试日志

            // 仅当用户当前在首页时，进行自动导航
            if (userGroups.includes('Student') && location.pathname === '/') {
                navigate('/student-dashboard');
            } else if (userGroups.includes('Teacher') && location.pathname === '/') {
                navigate('/teacher-dashboard');
            }
            // 否则，允许用户访问其他路由
        }
    }, [user, navigate, location.pathname]);

    return (
        <AuthContext.Provider value={{ isAuthenticated, user, setUser, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};
