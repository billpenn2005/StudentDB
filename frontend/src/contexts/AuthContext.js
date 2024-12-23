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
            if (JSON.stringify(response.data) !== JSON.stringify(user)) {
                setUser(response.data);
            }
            setIsAuthenticated(true);
            console.log('Fetched User:', response.data);
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
    }, [user]);

    const fetchSelectedCourses = useCallback(async () => {
        if (!user || !user.student) {
            console.warn('User or student information is missing.');
            setSelectedCourses([]);
            return;
        }

        try {
            const response = await axiosInstance.get('selection-batches/current/selected_courses/');
            setSelectedCourses(response.data.selected_courses || []);
            console.log('Fetched Selected Courses:', response.data.selected_courses);
        } catch (error) {
            console.error('Failed to fetch selected courses:', error);
            setSelectedCourses([]);
            toast.error('获取已选课程失败');
        }
    }, [user]);

    const fetchCurrentSemester = useCallback(async () => {
        try {
            const response = await axiosInstance.get('semesters/current/');
            setCurrentSemester(response.data);
            console.log('Fetched Current Semester:', response.data);
        } catch (error) {
            console.error('Fetch Current Semester Error:', error);
            toast.error('获取当前学期信息失败');
        }
    }, []);

    useEffect(() => {
        let isMounted = true;

        const initialize = async () => {
            if (isAuthenticated && isMounted) {
                const fetchedUser = await fetchUser();
                if (fetchedUser && isMounted) {
                    await fetchSelectedCourses();
                    await fetchCurrentSemester();
                }
            }
            if (isMounted) setLoading(false);
        };
        initialize();

        return () => {
            isMounted = false;
        };
    }, [isAuthenticated, fetchUser, fetchSelectedCourses, fetchCurrentSemester]);

    useEffect(() => {
        if (user) {
            fetchSelectedCourses();
            fetchCurrentSemester();
        }
    }, [user, fetchSelectedCourses, fetchCurrentSemester]);

    const login = async (accessToken, refreshToken) => {
        try {
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('refresh_token', refreshToken);
            setIsAuthenticated(true);
            const fetchedUser = await fetchUser();
            if (fetchedUser) {
                navigate('/dashboard');
            }
        } catch (error) {
            console.error('登录失败:', error);
            toast.error('登录失败，请检查用户名和密码');
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setIsAuthenticated(false);
        setUser(null);
        setSelectedCourses([]);
        setCurrentSemester(null);
        toast.info('已注销');
        navigate('/');
    };

    useEffect(() => {
        if (user && !hasNavigated.current) {
            const userGroups = Array.isArray(user.groups) ? user.groups : [];
            console.log('User Groups:', userGroups);

            if (location.pathname === '/') {
                if (userGroups.includes('Student')) {
                    navigate('/student-dashboard');
                } else if (userGroups.includes('Teacher')) {
                    navigate('/teacher-dashboard');
                }
                hasNavigated.current = true;
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
            fetchUser,
            currentSemester,
            fetchCurrentSemester,
        }}>
            {children}
        </AuthContext.Provider>
    );
};