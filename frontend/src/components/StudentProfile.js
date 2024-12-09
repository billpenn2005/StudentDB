// src/components/StudentProfile.js

import React, { useState, useEffect, useContext } from 'react';
import { Typography, Card, Form, Input, Button, message } from 'antd';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';

const { Title, Paragraph } = Typography;

const StudentProfile = () => {
    const { user, setUser } = useContext(AuthContext);
    const [form] = Form.useForm();
    const [editing, setEditing] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (user) {
            form.setFieldsValue({
                first_name: user.first_name,
                last_name: user.last_name,
                email: user.email,
            });
        }
    }, [user, form]);

    const onFinish = async (values) => {
        setLoading(true);
        try {
            const response = await axiosInstance.put('user/current', values);
            setUser(response.data); // 更新全局用户状态
            message.success('个人信息更新成功');
            setEditing(false);
        } catch (error) {
            console.error(error);
            message.error('更新失败，请稍后再试');
        } finally {
            setLoading(false);
        }
    };

    const onCancel = () => {
        form.resetFields();
        setEditing(false);
    };

    return (
        <div style={styles.container}>
            <Title level={2}>学生资料</Title>
            <Card title="个人信息" bordered={false} style={styles.card}>
                {!editing ? (
                    <div>
                        <Paragraph><strong>姓名:</strong> {user.first_name} {user.last_name}</Paragraph>
                        <Paragraph><strong>学号:</strong> {user.username}</Paragraph>
                        <Paragraph><strong>邮箱:</strong> {user.email}</Paragraph>
                        <Paragraph><strong>年龄:</strong> {user.age}</Paragraph>
                        <Paragraph><strong>学院:</strong>{user.department?.name || 'N/A'}</Paragraph>
                        <Paragraph><strong>专业:</strong>{user.major || 'N/A'}</Paragraph>
                        <Paragraph><strong>年级:</strong>{user.grade || 'N/A'}</Paragraph>
                        <Button type="primary" onClick={() => setEditing(true)}>
                            编辑
                        </Button>
                    </div>
                ) : (
                    <Form
                        form={form}
                        layout="vertical"
                        onFinish={onFinish}
                    >
                        <Form.Item
                            label="名字"
                            name="first_name"
                            rules={[{ required: true, message: '请输入名字' }]}
                        >
                            <Input />
                        </Form.Item>
                        <Form.Item
                            label="姓氏"
                            name="last_name"
                            rules={[{ required: true, message: '请输入姓氏' }]}
                        >
                            <Input />
                        </Form.Item>
                        <Form.Item
                            label="邮箱"
                            name="email"
                            rules={[
                                { required: true, message: '请输入邮箱' },
                                { type: 'email', message: '请输入有效的邮箱地址' },
                            ]}
                        >
                            <Input />
                        </Form.Item>
                        {/* 添加其他可编辑字段 */}
                        <Form.Item>
                            <Button type="primary" htmlType="submit" loading={loading}>
                                保存
                            </Button>
                            <Button style={{ marginLeft: '10px' }} onClick={onCancel}>
                                取消
                            </Button>
                        </Form.Item>
                    </Form>
                )}
            </Card>
            {/* 添加更多资料相关的内容 */}
        </div>
    );
};

const styles = {
    container: {
        textAlign: 'center',
        paddingTop: '50px',
    },
    card: {
        maxWidth: '600px',
        margin: 'auto',
    },
};

export default StudentProfile;
