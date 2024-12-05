import React from 'react';
import { Menu } from 'antd';
import { Link } from 'react-router-dom';

const Sidebar = () => {
  return (
    <Menu
      mode="inline"
      defaultSelectedKeys={['1']}
      style={{ height: '100%', borderRight: 0 }}
    >
      <Menu.Item key="1">
        <Link to="/course-selection">选课页面</Link>
      </Menu.Item>
      <Menu.Item key="2">
        <Link to="/student-info">学生信息页面</Link>
      </Menu.Item>
    </Menu>
  );
};

export default Sidebar;
