// src/components/Logout.js

import React from 'react';
import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { Button } from 'antd';
import { LogoutOutlined } from '@ant-design/icons';

const Logout = () => {
    const { logout } = useContext(AuthContext);

    const handleLogout = () => {
        logout();
        window.location.reload();
    };

    return (
        <Button type="link" onClick={handleLogout} icon={<LogoutOutlined />}>
            注销
        </Button>
    );
};

export default Logout;
