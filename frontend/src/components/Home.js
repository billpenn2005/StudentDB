// src/components/Home.js

import React, { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { Typography, Button, Spin, Alert } from 'antd';
import Login from './Login';

const { Title, Paragraph } = Typography;

const Home = () => {
    const { isAuthenticated, user, loading } = useContext(AuthContext);

    if (loading) {
        // 显示加载指示器
        return (
            <div style={styles.loading}>
                <Spin tip="加载中..." size="large" />
            </div>
        );
    }


    if (!isAuthenticated) {
        // 未认证时显示登录界面
        return <Login />;
    }

    if (!user) {
        // 认证但未获取到用户数据时显示错误信息
        return (
            <div style={styles.errorContainer}>
                <Alert
                    message="错误"
                    description="无法获取用户信息，请重新登录。"
                    type="error"
                    showIcon
                />
            </div>
        );
    }
    console.log(user);

    // 已认证且获取到用户数据时显示欢迎信息和跳转按钮
    return (
        <div style={styles.container}>
            <Title level={2}>欢迎, {user.first_name} {user.last_name}!</Title>
            <Paragraph>
                您已经成功登录到学生管理系统。请选择您的仪表盘。
            </Paragraph>
            // ...existing code...
            {user.groups.some(group => group === 'student') && (
                <Button type="primary" href="/student-dashboard" style={{ marginRight: '10px' }}>
                    前往学生仪表盘
                </Button>
            )}
            {user.groups.some(group => group === 'teacher') && (
                <Button type="primary" href="/teacher-dashboard">
                    前往老师仪表盘
                </Button>
            )}
            // ...existing code...
        </div>
    );
};

const styles = {
    container: {
        textAlign: 'center',
        paddingTop: '50px',
    },
    loading: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
    },
    errorContainer: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        padding: '20px',
    },
};

export default Home;
