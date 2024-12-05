import React from 'react';
import { Avatar, Button, Dropdown, Menu } from 'antd';
import { UserOutlined, LogoutOutlined, SettingOutlined } from '@ant-design/icons';

const Header = ({ username, onLogout }) => {
  const menu = (
    <Menu>
      <Menu.Item key="settings">
        <Button icon={<SettingOutlined />}>账号设置</Button>
      </Menu.Item>
      <Menu.Item key="logout" onClick={onLogout}>
        <Button icon={<LogoutOutlined />}>登出</Button>
      </Menu.Item>
    </Menu>
  );

  return (
    <div style={{ float: 'right' }}>
      <Avatar icon={<UserOutlined />} />
      <span style={{ marginLeft: 10 }}>{username}</span>
      <Dropdown overlay={menu}>
        <Button style={{ marginLeft: 10 }}>个人账号</Button>
      </Dropdown>
    </div>
  );
};

export default Header;
