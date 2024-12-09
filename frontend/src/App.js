// src/App.js

import React from 'react';
import { Route, Routes, Navigate, Link } from 'react-router-dom';
import Home from './components/Home';
import StudentDashboard from './components/StudentDashboard';
import TeacherDashboard from './components/TeacherDashboard';
import StudentProfile from './components/StudentProfile';
import MyCourses from './components/MyCourses';
import RoleProtectedRoute from './components/RoleProtectedRoute';
import Logout from './components/Logout';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { Layout, Menu, Spin } from 'antd';
import { UserOutlined, HomeOutlined, LogoutOutlined, ProfileOutlined, BookOutlined } from '@ant-design/icons';
import { useContext } from 'react';
import { AuthContext } from './contexts/AuthContext';

const { Header, Content, Footer, Sider } = Layout;

const App = () => {
    const { isAuthenticated, user, loading } = useContext(AuthContext);

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
                <Spin tip="加载中..." size="large" />
            </div>
        );
    }

    return (
        <Layout style={{ minHeight: '100vh' }}>
            {isAuthenticated && (
                <Sider collapsible>
                    <div className="logo" style={{ height: '32px', margin: '16px', background: 'rgba(255, 255, 255, 0.3)' }} />
                    <Menu theme="dark" mode="inline" defaultSelectedKeys={['1']}>
                        <Menu.Item key="1" icon={<HomeOutlined />}>
                            <Link to="/">首页</Link>
                        </Menu.Item>
                        {user && user.groups.some(group => group.name === 'Student') && ( // 大写 "Student"
                            <>
                                <Menu.Item key="2" icon={<UserOutlined />}>
                                    <Link to="/student-dashboard">学生仪表盘</Link>
                                </Menu.Item>
                                <Menu.Item key="3" icon={<ProfileOutlined />}>
                                    <Link to="/student-profile">学生资料</Link>
                                </Menu.Item>
                                <Menu.Item key="4" icon={<BookOutlined />}>
                                    <Link to="/my-courses">我的课程</Link>
                                </Menu.Item>
                            </>
                        )}
                        {user && user.groups.some(group => group.name === 'Teacher') && ( // 大写 "Teacher"
                            <>
                                <Menu.Item key="5" icon={<UserOutlined />}>
                                    <Link to="/teacher-dashboard">老师仪表盘</Link>
                                </Menu.Item>
                                {/* 老师的其他菜单项 */}
                            </>
                        )}
                        <Menu.Item key="6" icon={<LogoutOutlined />}>
                            <Logout />
                        </Menu.Item>
                    </Menu>
                </Sider>
            )}
            <Layout>
                {isAuthenticated && (
                    <Header style={{ background: '#fff', padding: 0, textAlign: 'right', paddingRight: '20px' }}>
                        {user && <span>欢迎, {user.first_name}</span>}
                    </Header>
                )}
                <Content style={{ margin: '16px' }}>
                    {/* 显示用户组信息（调试用，完成后可移除） */}
                    {user && (
                        <div style={{ marginBottom: '20px', textAlign: 'left' }}>
                            <strong>用户组:</strong> {user.groups.map(group => group.name).join(', ')}
                        </div>
                    )}
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/student-dashboard" element={
                            <RoleProtectedRoute roles={['Student']}>
                                <StudentDashboard />
                            </RoleProtectedRoute>
                        } />
                        <Route path="/student-profile" element={
                            <RoleProtectedRoute roles={['Student']}>
                                <StudentProfile />
                            </RoleProtectedRoute>
                        } />
                        <Route path="/my-courses" element={
                            <RoleProtectedRoute roles={['Student']}>
                                <MyCourses />
                            </RoleProtectedRoute>
                        } />
                        <Route path="/teacher-dashboard" element={
                            <RoleProtectedRoute roles={['Teacher']}>
                                <TeacherDashboard />
                            </RoleProtectedRoute>
                        } />
                        {/* 其他路由 */}
                        <Route path="*" element={<Navigate to="/" />} />
                    </Routes>
                </Content>
                <Footer style={{ textAlign: 'center' }}>学生管理系统 ©2024 Created by Your Name</Footer>
            </Layout>
            <ToastContainer />
        </Layout>
    );

};

export default App;
