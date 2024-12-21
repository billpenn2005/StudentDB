// src/components/StudentProfile.js

import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { Form, Input, Button, Spin, message, Typography } from 'antd';
import axiosInstance from '../axiosInstance';

const { Title, Text } = Typography;

const StudentProfile = () => {
    const { user, loading } = useContext(AuthContext);
    const [form] = Form.useForm();
    const [submitting, setSubmitting] = useState(false);
    const [studentData, setStudentData] = useState(null);

    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                // 获取当前用户信息
                const userRes = await axiosInstance.get('user/current/');
                // 获取当前学生的详细信息
                const studentRes = await axiosInstance.get('old_students/current/');

                // 如果响应在 results 中，提取第一个元素
                const userData = userRes.data.results ? userRes.data.results[0] : userRes.data;
                const studentData = studentRes.data.results ? studentRes.data.results[0] : studentRes.data;

                const combinedData = {
                    ...studentData,
                    ...userData
                };
                setStudentData(combinedData);
                // 设置表单初始值
                form.setFieldsValue({
                    email: userData.email,
                });
            } catch (error) {
                console.error('Failed to fetch profile data:', error);
                message.error('获取个人资料失败');
            }
        };
        if (user) {
            fetchInitialData();
        }
    }, [user, form]);

    const onFinish = async (values) => {
        setSubmitting(true);
        try {
            // 更新用户邮箱
            await axiosInstance.patch('user/current/', {
                email: values.email,
            });
            message.success('邮箱更新成功');
            // 更新本地状态
            setStudentData(prevData => ({
                ...prevData,
                email: values.email
            }));
        } catch (error) {
            console.error('Failed to update email:', error);
            message.error('邮箱更新失败');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading || !studentData) {
        return <Spin tip="加载中..." />;
    }

    return (
        <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
            <Title level={2}>学生资料</Title>
            <Form
                form={form}
                layout="vertical"
                onFinish={onFinish}
                initialValues={{
                    email: studentData.email,
                }}
            >
                <Form.Item label="姓名">
                    <Text>{`${studentData.user.first_name} ${studentData.user.last_name}`}</Text>
                </Form.Item>
                <Form.Item label="邮箱" name="email" rules={[
                    { required: true, message: '请输入邮箱', type: 'email' }
                ]}>
                    <Input />
                </Form.Item>
                <Form.Item label="部门">
                    <Text>{studentData.department ? studentData.department.name : 'N/A'}</Text>
                </Form.Item>
                <Form.Item label="班级">
                    <Text>{studentData.student_class ? studentData.student_class.name : 'N/A'}</Text>
                </Form.Item>
                <Form.Item label="年级">
                    <Text>{studentData.grade ? studentData.grade.name : 'N/A'}</Text>
                </Form.Item>
                <Form.Item label="年龄">
                    <Text>{studentData.age}</Text>
                </Form.Item>
                <Form.Item label="性别">
                    <Text>
                        {studentData.gender === 'M' ? '男' :
                        studentData.gender === 'F' ? '女' : '其他'}
                    </Text>
                </Form.Item>
                <Form.Item label="身份证号码">
                    <Text>{studentData.id_number}</Text>
                </Form.Item>
                <Form.Item>
                    <Button type="primary" htmlType="submit" loading={submitting}>
                        更新邮箱
                    </Button>
                </Form.Item>
            </Form>
        </div>
    );
};

export default StudentProfile;
