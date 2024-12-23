// src/axiosInstance.js

import axios from 'axios';
import { toast } from 'react-toastify';

const axiosInstance = axios.create({
    baseURL: process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000/api/',
    timeout: 5000,
    headers: {
        'Content-Type': 'application/json',
    },
});

axiosInstance.interceptors.response.use(
    response => {
        return response;
    },
    async error => {
        const originalRequest = error.config;

        // 定义需要排除的请求路径数组
        const excludedPaths = [
            '/api/token/', // 登录请求路径
            '/api/token/refresh/', // 刷新令牌路径
            '/api/auth/login/', // 假设的登录请求路径，如有不同请调整
        ];

        const isExcluded = excludedPaths.some(path => originalRequest.url.includes(path));

        if (error.response && error.response.status === 401 && !originalRequest._retry && !isExcluded) {
            originalRequest._retry = true;
            const refreshToken = localStorage.getItem('refresh_token');

            if (refreshToken) {
                try {
                    const response = await axios.post(`${axiosInstance.defaults.baseURL}token/refresh/`, {
                        refresh: refreshToken,
                    });
                    const newAccessToken = response.data.access;
                    localStorage.setItem('access_token', newAccessToken);
                    axiosInstance.defaults.headers['Authorization'] = `Bearer ${newAccessToken}`;
                    originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
                    return axiosInstance(originalRequest);
                } catch (err) {
                    toast.error('刷新令牌失败，请重新登录');
                    // 清除令牌并重定向到登录页
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    window.location.href = '/login'; // 确保重定向到登录页
                    return Promise.reject(err);
                }
            } else {
                toast.error('没有刷新令牌，请重新登录');
                window.location.href = '/login'; // 确保重定向到登录页
            }
        }

        return Promise.reject(error);
    }
);

export default axiosInstance;