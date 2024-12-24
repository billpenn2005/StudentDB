// src/components/Login.js

import React, { useState, useContext } from 'react';
import { Form, Input, Button, Typography, Alert, Card, Row, Col, Checkbox } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';
import { toast } from 'react-toastify';

const { Title } = Typography;

const Login = () => {
    const { login } = useContext(AuthContext);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [username, setUsername] = useState('');

    const onFinish = async (values) => {
        const { username, password, remember } = values;
        setLoading(true);
        try {
            const response = await axiosInstance.post('token/', { username, password });
            await login(response.data.access, response.data.refresh);
            setUsername(username);
            toast.success('登录成功');
            // 导航由 AuthContext 处理
        } catch (err) {
            console.error(err);
            setError('登录失败，请检查用户名和密码');
            toast.error('登录失败，请检查用户名和密码');
        } finally {
            setLoading(false);
        }
    };

    const onFinishFailed = (errorInfo) => {
        console.log('Failed:', errorInfo);
    };

    return (
        <div style={styles.container}>
            <Row justify="center" align="middle" style={{ width: '100%', height: '100%' }}>
                <Col xs={22} sm={16} md={12} lg={8} xl={6}>
                    <Card style={styles.card} bordered={false}>
                        <div style={styles.logoContainer}>
                            {/* 替换为您的品牌 logo */}
                            <img src="/logo192.png" alt="Logo" style={styles.logo} />
                            <Title level={3}>学生管理系统</Title>
                        </div>
                        {error && <Alert message={error} type="error" showIcon style={{ marginBottom: '20px' }} />}
                        <Form
                            name="login"
                            initialValues={{ remember: true }}
                            onFinish={onFinish}
                            onFinishFailed={onFinishFailed}
                            layout="vertical"
                        >
                            <Form.Item
                                name="username"
                                label="用户名"
                                rules={[
                                    { required: true, message: '请输入您的用户名!' },
                                    { min: 4, message: '用户名至少4个字符!' },
                                ]}
                            >
                                <Input prefix={<UserOutlined />} placeholder="用户名" autoFocus />
                            </Form.Item>

                            <Form.Item
                                name="password"
                                label="密码"
                                rules={[
                                    { required: true, message: '请输入您的密码!' },
                                    { min: 6, message: '密码至少6个字符!' },
                                ]}
                            >
                                <Input.Password prefix={<LockOutlined />} placeholder="密码" />
                            </Form.Item>

                            <Form.Item name="remember" valuePropName="checked">
                                <Checkbox>记住我</Checkbox>
                            </Form.Item>

                            <Form.Item>
                                <Button type="primary" htmlType="submit" block loading={loading}>
                                    登录
                                </Button>
                            </Form.Item>

                            <Form.Item>
                                <Row justify="space-between">
                                    <Col>
                                        <a href="/forgot-password">忘记密码</a>
                                    </Col>
                                    <Col>
                                        <a href="/register">没有账号？注册</a>
                                    </Col>
                                </Row>
                            </Form.Item>
                        </Form>
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

const styles = {
    container: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #71b7e6, #9b59b6)',
    },
    card: {
        padding: '30px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    },
    logoContainer: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        marginBottom: '20px',
    },
    logo: {
        width: '80px',
        marginBottom: '10px',
    },
};

export default Login;
