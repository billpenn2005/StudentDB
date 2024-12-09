// src/axiosInstance.js

import axios from 'axios';
import { toast } from 'react-toastify';

const axiosInstance = axios.create({
    baseURL: process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000/api/', // 根据您的 Django API URL 进行调整
    timeout: 5000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// 请求拦截器：添加访问令牌到请求头
axiosInstance.interceptors.request.use(
    config => {
        const accessToken = localStorage.getItem('access_token');
        if (accessToken) {
            config.headers['Authorization'] = `Bearer ${accessToken}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// 响应拦截器：处理令牌过期并尝试刷新
axiosInstance.interceptors.response.use(
    response => {
        return response;
    },
    async error => {
        const originalRequest = error.config;

        if (error.response && error.response.status === 401 && !originalRequest._retry) {
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
                    window.location.href = '/';
                    return Promise.reject(err);
                }
            } else {
                toast.error('没有刷新令牌，请重新登录');
                window.location.href = '/';
            }
        }

        return Promise.reject(error);
    }
);

export default axiosInstance;
