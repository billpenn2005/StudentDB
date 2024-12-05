// src/pages/Dashboard.js
import React, { useState } from 'react';
import { Layout, Menu, Tabs } from 'antd';
import Header from '../components/Header';
import CourseSelection from './CourseSelection';  // 选课页面组件
import StudentInfo from './StudentInfo';  // 学生信息页面组件
import TeacherDashboard from './TeacherDashboard';  // 老师页面组件

const { Content, Sider } = Layout;

const Dashboard = ({ username, userRole, onLogout }) => {
  const [activeTab, setActiveTab] = useState("1");  // 当前tab
  const [sidebarKey, setSidebarKey] = useState("1");  // 当前侧边栏选项
  const studentId = "12345"; // 假设学生ID

  // 处理侧边栏点击
  const handleSidebarClick = (key) => {
    setSidebarKey(key);
    setActiveTab(key);  // 侧边栏点击时切换 Tab
  };

  // 渲染学生或老师的菜单项
  const renderMenuItems = () => {
    if (userRole === "student") {
      return (
        <>
          <Menu.Item key="1">选课页面</Menu.Item>
          <Menu.Item key="2">学生信息页面</Menu.Item>
        </>
      );
    } else if (userRole === "teacher") {
      return (
        <>
          <Menu.Item key="3">学生信息管理</Menu.Item>
          <Menu.Item key="4">成绩查看</Menu.Item>
          <Menu.Item key="5">选课管理</Menu.Item>
        </>
      );
    }
    return null;
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header username={username} onLogout={onLogout} />

      <Layout>
        {/* Sider 侧边栏 */}
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[sidebarKey]}  // 根据当前选中的 sidebarKey 高亮侧边栏
            style={{ height: '100%', borderRight: 0 }}
            onClick={({ key }) => handleSidebarClick(key)}  // 侧边栏点击切换
          >
            {renderMenuItems()}  {/* 渲染菜单项 */}
          </Menu>
        </Sider>

        {/* Content 内容区域 */}
        <Layout style={{ padding: '0 24px 24px' }}>
          <Content style={{ padding: 24, margin: 0, minHeight: 280 }}>
            {/* Tabs 用于切换页面 */}
            <Tabs activeKey={activeTab} onChange={setActiveTab}>
              {userRole === "student" && (
                <>
                  <Tabs.TabPane tab="选课页面" key="1">
                    {sidebarKey === '1' && <CourseSelection />}
                  </Tabs.TabPane>
                  <Tabs.TabPane tab="学生信息页面" key="2">
                    {sidebarKey === '2' && <StudentInfo studentId={studentId} />}
                  </Tabs.TabPane>
                </>
              )}

              {userRole === "teacher" && (
                <>
                  <Tabs.TabPane tab="学生信息管理" key="3">
                    {sidebarKey === '3' && <TeacherDashboard />}
                  </Tabs.TabPane>
                  <Tabs.TabPane tab="成绩查看" key="4">
                    {sidebarKey === '4' && <TeacherDashboard />}
                  </Tabs.TabPane>
                  <Tabs.TabPane tab="选课管理" key="5">
                    {sidebarKey === '5' && <TeacherDashboard />}
                  </Tabs.TabPane>
                </>
              )}
            </Tabs>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default Dashboard;
