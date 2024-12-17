// src/contexts/AuthContext.js

import React, { createContext, useState, useEffect, useRef } from 'react';
import axiosInstance from '../axiosInstance';
import { toast } from 'react-toastify';
import { useNavigate, useLocation } from 'react-router-dom';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('access_token'));
    const [user, setUser] = useState(null);
    const [selectedCourses, setSelectedCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const location = useLocation(); // 获取当前路径
    const hasNavigated = useRef(false); // Ref to track navigation

    const fetchUser = async () => {
        try {
            const response = await axiosInstance.get('user/current/');
            setUser(response.data);
            setIsAuthenticated(true);
            console.log('Fetched User:', response.data); // Debug log
            return response.data;
        } catch (err) {
            console.error(err);
            setIsAuthenticated(false);
            setUser(null);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            toast.error('用户信息获取失败，请重新登录');
            return null;
        }
    };

    const fetchSelectedCourses = async () => {
        try {
            const response = await axiosInstance.get('course-instances/list_selected_courses/');
            setSelectedCourses(response.data);
            console.log('Fetched Selected Courses:', response.data); // Debug log
        } catch (error) {
            console.error('Failed to fetch selected courses:', error);
            setSelectedCourses([]);
        }
    };

    // 初始化
    useEffect(() => {
        const initialize = async () => {
            if (isAuthenticated) {
                const fetchedUser = await fetchUser();
                if (fetchedUser) {
                    await fetchSelectedCourses();
                }
            }
            setLoading(false);
        };
        initialize();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // 监听用户变化，刷新已选课程
    useEffect(() => {
        if (user) {
            fetchSelectedCourses();
        }
    }, [user]);

    const login = async (accessToken, refreshToken) => {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        setIsAuthenticated(true);
        const fetchedUser = await fetchUser();
        if (fetchedUser) {
            await fetchSelectedCourses();
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setIsAuthenticated(false);
        setUser(null);
        setSelectedCourses([]); // 清空已选课程
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
        <AuthContext.Provider value={{ isAuthenticated, user, login, logout, loading, setUser, selectedCourses, fetchSelectedCourses }}>
            {children}
        </AuthContext.Provider>
    );
};
