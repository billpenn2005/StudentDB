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
    const [currentSemester, setCurrentSemester] = useState(null); // 新增状态
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const location = useLocation(); // 获取当前路径
    const hasNavigated = useRef(false); // Ref to track navigation

    const fetchUser = useCallback(async () => {
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
    }, []);

    const fetchSelectedCourses = useCallback(async () => {
        try {
            const response = await axiosInstance.get('course-instances/list_selected_courses/');
            setSelectedCourses(response.data);
            console.log('Fetched Selected Courses:', response.data); // Debug log
        } catch (error) {
            console.error('Failed to fetch selected courses:', error);
            setSelectedCourses([]);
        }
    }, []);

    const fetchCurrentSemester = useCallback(async () => {
        try {
            const response = await axiosInstance.get('semesters/current/');
            setCurrentSemester(response.data);
            console.log('Fetched Current Semester:', response.data); // Debug log
        } catch (error) {
            console.error('Fetch Current Semester Error:', error);
            toast.error('获取当前学期信息失败');
        }
    }, []);

    // 初始化
    useEffect(() => {
        const initialize = async () => {
            if (isAuthenticated) {
                const fetchedUser = await fetchUser();
                if (fetchedUser) {
                    await fetchSelectedCourses();
                    await fetchCurrentSemester(); // 获取当前学期
                }
            }
            setLoading(false);
        };
        initialize();
    }, [isAuthenticated, fetchUser, fetchSelectedCourses, fetchCurrentSemester]);

    // 监听用户变化，刷新已选课程和当前学期
    useEffect(() => {
        if (user) {
            fetchSelectedCourses();
            fetchCurrentSemester();
        }
    }, [user, fetchSelectedCourses, fetchCurrentSemester]);

    const login = async (accessToken, refreshToken) => {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        setIsAuthenticated(true);
        const fetchedUser = await fetchUser();
        if (fetchedUser) {
            await fetchSelectedCourses();
            await fetchCurrentSemester();
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setIsAuthenticated(false);
        setUser(null);
        setSelectedCourses([]); // 清空已选课程
        setCurrentSemester(null); // 清空当前学期
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
        <AuthContext.Provider value={{
            isAuthenticated,
            user,
            login,
            logout,
            loading,
            setUser,
            selectedCourses,
            fetchSelectedCourses,
            fetchUser, // 添加 fetchUser 到 context
            currentSemester, // 提供当前学期信息
            fetchCurrentSemester, // 添加 fetchCurrentSemester 到 context
        }}>
            {children}
        </AuthContext.Provider>
    );
};
