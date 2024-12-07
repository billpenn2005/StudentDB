import React, { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import axios from 'axios';// eslint-disable-next-lin

const Login = ({ onLogin }) => {
    const [loading, setLoading] = useState(false);

    const handleLogin = async (values) => {
        /*setLoading(true);
        if (values.username === 'admin' && values.password === 'admin') {
            onLogin(values.username, 'admin');
        } else if (values.username === 'student' && values.password === 'student') {
            onLogin(values.username, 'student');
        } else if (values.username === 'teacher' && values.password === 'teacher') {
            onLogin(values.username, 'teacher');
        }
        else {
            message.error('登录失败，请检查用户名和密码');
        }*/
        try {
          const response = await axios.post('你的后端登录API端点', {
            username: values.username,
            password: values.password,
          });
          
          const { userrole } = response.data;
          
          if (userrole) {
            onLogin(values.username, userrole);
          } else {
            message.error('获取用户角色失败');
          }
        } catch (error) {
          message.error('登录失败，请检查用户名和密码');
        } finally {
          setLoading(false);
        }
    };

    return (
        <div style={{ padding: '50px' }}>
            <h2>学生选课系统登录</h2>
            <Form onFinish={handleLogin}>
                <Form.Item
                    name="username"
                    rules={[{ required: true, message: '请输入用户名!' }]}
                >
                    <Input placeholder="用户名" />
                </Form.Item>
                <Form.Item
                    name="password"
                    rules={[{ required: true, message: '请输入密码!' }]}
                >
                    <Input.Password placeholder="密码" />
                </Form.Item>
                <Button type="primary" htmlType="submit" loading={loading}>
                    登录
                </Button>
            </Form>
        </div>
    );
};

export default Login;