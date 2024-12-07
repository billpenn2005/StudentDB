import React, { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import axios from 'axios';// eslint-disable-next-lin

const Login = ({ onLogin }) => {
    const [loading, setLoading] = useState(false);

  const handleLogin = async (values) => {
    setLoading(true);
    try {
      // 向后端发送登录请求
      const response = await axios.post('http://localhost:8000/api/', {
        username: values.username,
        password: values.password,
      });
      const access = response.data.access_token;  // 后端返回的 access token
      const refresh = response.data.refresh_token;  // 后端返回的 refresh token
      const role= response.data.user.role;  // 后端返回的用户角色

      console.log(response);
      if (role) {
        // 登录成功后调用 onLogin 函数并传递用户名和角色
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        onLogin(values.username, role);
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
