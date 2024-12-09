// src/contexts/AuthContext.js

import React, { createContext, useState, useEffect, useRef } from 'react';
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
    const hasNavigated = useRef(false); // Ref to track navigation

    const fetchUser = async () => {
        try {
            const response = await axiosInstance.get('user/current');
            if (JSON.stringify(response.data) !== JSON.stringify(user)) {
                setUser(response.data);
            }
            setIsAuthenticated(true);
            console.log('Fetched User:', response.data); // Debug log
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
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isAuthenticated]); // Ensure dependencies are correctly set

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
        if (user && !hasNavigated.current) {
            const userGroups = user.groups;
            console.log('User Groups:', userGroups); // Debug log

            // 仅当用户当前在首页时，进行自动导航
            if (location.pathname === '/') {
                if (userGroups.includes('Student')) {
                    navigate('/student-dashboard');
                } else if (userGroups.includes('Teacher')) {
                    navigate('/teacher-dashboard');
                }
                hasNavigated.current = true; // Prevent future navigations
            }
        }
    }, [user, navigate, location.pathname]);

    return (
        <AuthContext.Provider value={{ isAuthenticated, user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};
