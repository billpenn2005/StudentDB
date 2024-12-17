// src/components/StudentProfile.js

import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { Form, Input, Button, Select, Spin, message } from 'antd';
import axiosInstance from '../axiosInstance';

const { Option } = Select;

const StudentProfile = () => {
    const { user, loading } = useContext(AuthContext);
    const [form] = Form.useForm();
    const [departments, setDepartments] = useState([]);
    const [classes, setClasses] = useState([]);
    const [grades, setGrades] = useState([]);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const [departmentsRes, classesRes, gradesRes] = await Promise.all([
                    axiosInstance.get('/departments/'),
                    axiosInstance.get('/classes/'),
                    axiosInstance.get('/grades/')
                ]);
                setDepartments(departmentsRes.data);
                setClasses(classesRes.data);
                setGrades(gradesRes.data);
                // 设置表单初始值
                form.setFieldsValue({
                    first_name: user.first_name,
                    last_name: user.last_name,
                    email: user.email,
                    department: user.department_id, // 假设 user 数据中包含 department_id
                    student_class: user.student_class_id, // 假设 user 数据中包含 student_class_id
                    grade: user.grade_id, // 假设 user 数据中包含 grade_id
                    age: user.age,
                    gender: user.gender,
                    id_number: user.id_number
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
            const response = await axiosInstance.put('/user/current/', {
                first_name: values.first_name,
                last_name: values.last_name,
                email: values.email,
                // 其他需要更新的字段
            });
            // 假设有专门的 API 更新学生信息
            await axiosInstance.put('/students/', {
                department: values.department,
                student_class: values.student_class,
                grade: values.grade,
                age: values.age,
                gender: values.gender,
                id_number: values.id_number
            });
            message.success('个人资料更新成功');
        } catch (error) {
            console.error('Failed to update profile:', error);
            message.error('个人资料更新失败');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return <Spin tip="加载中..." />;
    }

    return (
        <div>
            <h1>学生资料</h1>
            <Form
                form={form}
                layout="vertical"
                onFinish={onFinish}
                initialValues={{
                    first_name: user.first_name,
                    last_name: user.last_name,
                    email: user.email,
                    // 其他初始值
                }}
            >
                <Form.Item label="名" name="first_name" rules={[{ required: true, message: '请输入名' }]}>
                    <Input />
                </Form.Item>
                <Form.Item label="姓" name="last_name" rules={[{ required: true, message: '请输入姓' }]}>
                    <Input />
                </Form.Item>
                <Form.Item label="邮箱" name="email" rules={[{ required: true, message: '请输入邮箱', type: 'email' }]}>
                    <Input />
                </Form.Item>
                <Form.Item label="部门" name="department" rules={[{ required: true, message: '请选择部门' }]}>
                    <Select>
                        {departments.map(dept => (
                            <Option key={dept.id} value={dept.id}>{dept.name}</Option>
                        ))}
                    </Select>
                </Form.Item>
                <Form.Item label="班级" name="student_class" rules={[{ required: true, message: '请选择班级' }]}>
                    <Select>
                        {classes.map(cls => (
                            <Option key={cls.id} value={cls.id}>{cls.name}</Option>
                        ))}
                    </Select>
                </Form.Item>
                <Form.Item label="年级" name="grade" rules={[{ required: true, message: '请选择年级' }]}>
                    <Select>
                        {grades.map(grade => (
                            <Option key={grade.id} value={grade.id}>{grade.name}</Option>
                        ))}
                    </Select>
                </Form.Item>
                <Form.Item label="年龄" name="age" rules={[{ required: true, message: '请输入年龄' }]}>
                    <Input type="number" />
                </Form.Item>
                <Form.Item label="性别" name="gender" rules={[{ required: true, message: '请选择性别' }]}>
                    <Select>
                        <Option value="M">男</Option>
                        <Option value="F">女</Option>
                        <Option value="O">其他</Option>
                    </Select>
                </Form.Item>
                <Form.Item label="身份证号码" name="id_number" rules={[{ required: true, message: '请输入身份证号码' }]}>
                    <Input />
                </Form.Item>
                <Form.Item>
                    <Button type="primary" htmlType="submit" loading={submitting}>
                        更新资料
                    </Button>
                </Form.Item>
            </Form>
        </div>
    );
};

export default StudentProfile;
