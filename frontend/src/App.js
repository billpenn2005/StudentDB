// src/App.js

import React, { useContext } from 'react';
import { Route, Routes, Navigate, Link } from 'react-router-dom';
import { Layout, Menu, Spin } from 'antd';
import {
    UserOutlined,
    HomeOutlined,
    LogoutOutlined,
    ProfileOutlined,
    BookOutlined,
    CalendarOutlined
} from '@ant-design/icons';

import Home from './components/Home';
import StudentDashboard from './components/StudentDashboard';
import TeacherDashboard from './components/TeacherDashboard';
import StudentProfile from './components/StudentProfile';
import MyCourses from './components/MyCourses';
import CourseSelection from './components/CourseSelection';
import Timetable from './components/Timetable';
import RoleProtectedRoute from './components/RoleProtectedRoute';
import Logout from './components/Logout';
import SetGradeWeights from './components/SetGradeWeights';
import EnterGrades from './components/EnterGrades';
import MyGrades from './components/MyGrades';
import MyRankings from './components/MyRankings';
import ManageGrades from './components/ManageGrades';
import { AuthContext } from './contexts/AuthContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ChangePassword from './components/ChangePassword';
import PunishmentRecords from './components/PunishmentRecords';
import MyPunishments from './components/MyPunishments';
import Login from './components/Login'; // 确保导入 Login 组件
import ManageGradesList from './components/ManageGradesList';
import MyRewards from './components/MyRewards';
import RewardsRecords from './components/RewardsRecords';
const { Header, Content, Footer, Sider } = Layout;
const { SubMenu } = Menu;

const App = () => {
    const { isAuthenticated, user, loading } = useContext(AuthContext);
    const isAdmin = user?.is_staff === true;

    // 加载中状态
    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
                <Spin tip="加载中..." size="large" />
            </div>
        );
    }

    // 用户组判断逻辑
    const userGroups = user?.groups?.map(g => g.trim().toLowerCase()) || [];
    const isStudent = userGroups.includes('student');
    const isTeacher = userGroups.includes('teacher');

    return (
        <Layout style={{ minHeight: '100vh' }}>
            {isAuthenticated && (
                <Sider collapsible>
                    <div className="logo" style={{ height: '32px', margin: '16px', background: 'rgba(255, 255, 255, 0.3)' }} />
                    <Menu theme="dark" mode="inline" defaultSelectedKeys={['1']}>

                        <Menu.Item key="1" icon={<HomeOutlined />}>
                            <Link to="/">首页</Link>
                        </Menu.Item>

                        {isStudent && (
                            <>
                                <Menu.Item key="3" icon={<ProfileOutlined />}>
                                    <Link to="/student-profile">学生资料</Link>
                                </Menu.Item>
                                <Menu.Item key="11" icon={<ProfileOutlined />}>
                                    <Link to="/my-grades">我的成绩</Link>
                                </Menu.Item>
                                <Menu.Item key="12" icon={<CalendarOutlined />}>
                                    <Link to="/my-rankings">我的排名</Link>
                                </Menu.Item>
                                <Menu.Item key="16" icon={<ProfileOutlined />}>
                                    <Link to="/my-punishments">我的惩罚记录</Link>
                                </Menu.Item>
                                <Menu.Item key="17" icon={<ProfileOutlined />}>
                                    <Link to="/my-rewards">我的奖励记录</Link>
                                </Menu.Item>
                                <SubMenu key="sub1" icon={<BookOutlined />} title="我的选课">
                                    <Menu.Item key="4">
                                        <Link to="/my-courses">已选课程</Link>
                                    </Menu.Item>
                                    <Menu.Item key="5">
                                        <Link to="/course-selection">选课</Link>
                                    </Menu.Item>
                                </SubMenu>
                                <Menu.Item key="6">
                                    <Link to="/timetable">课表</Link>
                                </Menu.Item>
                            </>
                        )}
                        {(isTeacher || isAdmin) && (
                            <Menu.Item key="22">
                                <Link to="/punishments">奖惩管理</Link>
                            </Menu.Item>
                        )}
                        {isTeacher && (
                            <>
                                <Menu.Item key="7" icon={<UserOutlined />}>
                                    <Link to="/teacher-dashboard">教师仪表盘</Link>
                                </Menu.Item>

                                <Menu.Item key="13">
                                    <Link to="/manage-grades-list">管理成绩</Link>
                                </Menu.Item>

                                {/* 新增奖惩管理入口 */}
                                <Menu.Item key="99">
                                    <Link to="/punishments">处分管理</Link>
                                </Menu.Item>        
                                <Menu.Item key="100">
                                    <Link to="/rewards">奖励管理</Link>
                                </Menu.Item>
                                <Menu.Item key="8">
                                    <Link to="/timetable">课表</Link>
                                </Menu.Item>
                            </>
                        )}
                        <Menu.Item key="15" icon={<ProfileOutlined />}>
                            <Link to="/change-password">修改密码</Link>
                        </Menu.Item>

                        <Menu.Item key="14" icon={<LogoutOutlined />}> 
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
                    <Routes>

                        <Route path="/" element={<Home />} />
                        
                        {/* 登录路由 */}
                        <Route path="/login" element={<Login />} />

                        {/* 学生端路由 */}
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
                        <Route path="/course-selection" element={
                            <RoleProtectedRoute roles={['Student']}>
                                <CourseSelection />
                            </RoleProtectedRoute>
                        } />

                        <Route path="/my-grades" element={
                            <RoleProtectedRoute roles={['Student']}>
                                <MyGrades />
                            </RoleProtectedRoute>
                        } />
                        <Route path="/my-rankings" element={
                            <RoleProtectedRoute roles={['Student']}>
                                <MyRankings />
                            </RoleProtectedRoute>
                        } />
                        <Route path="/my-punishments" element={
                            <RoleProtectedRoute roles={['Student']}>
                                <MyPunishments />
                            </RoleProtectedRoute>
                        } />
                        <Route path="/my-rewards" element={
                            <RoleProtectedRoute roles={['Student']}>
                                <MyRewards />
                            </RoleProtectedRoute>
                        } />

                        {/* 教师端路由 */}
                        <Route path="/teacher-dashboard" element={
                            <RoleProtectedRoute roles={['Teacher']}>
                                <TeacherDashboard />
                            </RoleProtectedRoute>
                        } />
                        <Route path="/set-grade-weights" element={
                            <RoleProtectedRoute roles={['Teacher']}>
                                <SetGradeWeights />
                            </RoleProtectedRoute>
                        } />
                        <Route path="/enter-grades" element={
                            <RoleProtectedRoute roles={['Teacher']}>
                                <EnterGrades />
                            </RoleProtectedRoute>
                        } />
                        <Route path="/manage-grades-list" element={
                            <RoleProtectedRoute roles={['Teacher']}>
                                <ManageGradesList />
                            </RoleProtectedRoute>
                        } />
                        <Route path="/manage-grades/:courseInstanceId" element={
                            <RoleProtectedRoute roles={['Teacher']}>
                                <ManageGrades />
                            </RoleProtectedRoute>
                        } />
                        <Route 
                        path="/punishments"
                        element={
                            <RoleProtectedRoute roles={['Teacher', 'Admin']}>
                                <PunishmentRecords />
                            </RoleProtectedRoute>
                        }   />
                        <Route
                        path="/rewards"
                        element={
                            <RoleProtectedRoute roles={['Teacher', 'Admin']}>
                                <RewardsRecords />
                            </RoleProtectedRoute>
                        }
                        />
                        {/* 公共路由 */}
                        <Route path="/timetable" element={
                            <RoleProtectedRoute roles={['Student', 'Teacher', 'Admin']}>
                                <Timetable />
                            </RoleProtectedRoute>
                        } />
                        <Route path="/change-password" element={
                            <RoleProtectedRoute roles={['Student', 'Teacher', 'Admin']}>
                                <ChangePassword />
                            </RoleProtectedRoute>
                        } />
                        {/* 未匹配的路由 */}
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