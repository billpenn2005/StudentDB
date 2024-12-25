// src/contexts/AuthContext.js

import React, { createContext, useState, useEffect, useRef, useCallback } from 'react';
import axiosInstance from '../axiosInstance';
import { toast } from 'react-toastify';
import { useNavigate, useLocation } from 'react-router-dom';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('access_token'));
    const [user, setUser] = useState(null);
    const [selectedCourses, setSelectedCourses] = useState([]);
    const [currentSemester, setCurrentSemester] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const location = useLocation();
    const hasNavigated = useRef(false);

    const fetchUser = useCallback(async () => {
        try {
            const response = await axiosInstance.get('user/current/');
            setUser(response.data);
            setIsAuthenticated(true);
            return response.data;
        } catch (err) {
            console.error('Failed to fetch user:', err);
            setIsAuthenticated(false);
            setUser(null);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            toast.error('用户信息获取失败，请重新登录');
            return null;
        }
    }, []);

    const fetchBatchBasedSelectedCourses = useCallback(async (selectedBatchId) => {
        if (!selectedBatchId) {
            console.error('未提供选课批次ID');
            return [];
        }

        try {
            const response = await axiosInstance.get(`selection-batches/${selectedBatchId}/selected_courses/`);
            console.log('Selected Courses:', response.data.selected_courses);
            const courses = response.data.selected_courses || [];
            setSelectedCourses(courses);
            return courses;
        } catch (error) {
            console.error('Failed to fetch selected courses:', error);
            setSelectedCourses([]);
            return [];
        }
    }, []);

    const fetchSelectedCourses = useCallback(async () => {
        try {
            const response = await axiosInstance.get('selection-batches/current/selected_courses/');
            console.log('Selected Courses:', response.data.selected_courses);
            setSelectedCourses(response.data.selected_courses || []);
        } catch (error) {
            console.error('Failed to fetch selected courses:', error);
            setSelectedCourses([]);
        }
    }, []);

    const fetchCurrentSemester = useCallback(async () => {
        try {
            const response = await axiosInstance.get('semesters/current/');
            setCurrentSemester(response.data);
        } catch (error) {
            console.error('Fetch Current Semester Error:', error);
        }
    }, []);

    // 主初始化函数
    useEffect(() => {
        const initializeData = async () => {
            if (isAuthenticated) {
                try {
                    setLoading(true);
                    const fetchedUser = await fetchUser();
                    if (fetchedUser) {
                        await Promise.all([
                            fetchSelectedCourses(),
                            fetchCurrentSemester()
                        ]);
                    }
                } catch (error) {
                    console.error('初始化数据失败:', error);
                } finally {
                    setLoading(false);
                }
            } else {
                setLoading(false);
            }
        };

        initializeData();
    }, [isAuthenticated, fetchUser, fetchSelectedCourses, fetchCurrentSemester]);

    // 路由导航逻辑
    useEffect(() => {
        if (user && !hasNavigated.current && location.pathname === '/') {
            const userGroups = user.groups || [];
            if (userGroups.includes('Student')) {
                navigate('/');
            } else if (userGroups.includes('Teacher')) {
                navigate('/teacher-dashboard');
            } else {
                navigate('/dashboard');
            }
            hasNavigated.current = true;
        }
    }, [user, navigate, location.pathname]);

    async function login(accessToken, refreshToken) {
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

        try {
            setLoading(true);
            // 切换用户前先重置状态引用
            hasNavigated.current = false;
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('refresh_token', refreshToken);
            setIsAuthenticated(true);
        
            const fetchedUser = await fetchUser(); // 确保真正拿到新用户
            console.log('Fetched User:', fetchedUser);
            if (fetchedUser) {
                const userGroups = fetchedUser.groups || [];
                if (userGroups.includes('Student')) {
                    navigate('/student-dashboard');
                } else if (userGroups.includes('Teacher')) {
                    navigate('/teacher-dashboard');
                } else {
                    navigate('/dashboard');
                }
                return true;
            }
            return false;
        } catch (error) {
            console.error('登录失败:', error);
            // 处理错误与清理逻辑
            return false;
        } finally {
            setLoading(false);
        }
    }

    const logout = () => {
        // 重置相关状态
        hasNavigated.current = false;
        delete axiosInstance.defaults.headers.common['Authorization'];

        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setIsAuthenticated(false);
        setUser(null);
        setSelectedCourses([]);
        setCurrentSemester(null);
        toast.info('已注销');
        navigate('/');
    };

    return (
        <AuthContext.Provider value={{
            isAuthenticated,
            user,
            login,
            logout,
            loading,
            setUser,
            selectedCourses,
            fetchSelectedCourses,
            fetchBatchBasedSelectedCourses,
            fetchUser,
            currentSemester,
            fetchCurrentSemester
        }}>
            {children}
        </AuthContext.Provider>
    );
};