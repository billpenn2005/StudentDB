import React, { useContext, useState } from 'react';
import { Form, Input, Button, message, Typography } from 'antd';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';

const { Title } = Typography;

const ChangePassword = () => {
    const { logout } = useContext(AuthContext);
    const [form] = Form.useForm();
    const [submitting, setSubmitting] = useState(false);

    const onFinish = async (values) => {
        const { old_password, new_password, confirm_password } = values;
        setSubmitting(true);
        try {
            const response = await axiosInstance.post('change-password/', {
                old_password,
                new_password,
                confirm_password
            });
            message.success(response.data.detail || '密码修改成功');
            form.resetFields();
            logout(); // 强制用户重新登录
        } catch (error) {
            console.error('Change Password Error:', error);
            if (error.response && error.response.data) {
                const errors = Object.values(error.response.data).flat();
                message.error(errors.join(', ') || '密码修改失败');
            } else {
                message.error('密码修改失败');
            }
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px' }}>
            <Title level={3}>修改密码</Title>
            <Form
                form={form}
                layout="vertical"
                onFinish={onFinish}
            >
                <Form.Item
                    label="旧密码"
                    name="old_password"
                    rules={[{ required: true, message: '请输入旧密码' }]}
                >
                    <Input.Password />
                </Form.Item>
                <Form.Item
                    label="新密码"
                    name="new_password"
                    rules={[
                        { required: true, message: '请输入新密码' },
                        { min: 8, message: '密码至少8位' },
                        // 其他密码规则
                    ]}
                >
                    <Input.Password />
                </Form.Item>
                <Form.Item
                    label="确认新密码"
                    name="confirm_password"
                    dependencies={['new_password']}
                    rules={[
                        { required: true, message: '请确认新密码' },
                        ({ getFieldValue }) => ({
                            validator(_, value) {
                                if (!value || getFieldValue('new_password') === value) {
                                    return Promise.resolve();
                                }
                                return Promise.reject(new Error('两次密码不一致'));
                            },
                        }),
                    ]}
                >
                    <Input.Password />
                </Form.Item>
                <Form.Item>
                    <Button type="primary" htmlType="submit" loading={submitting}>
                        修改密码
                    </Button>
                </Form.Item>
            </Form>
        </div>
    );
};

export default ChangePassword;
