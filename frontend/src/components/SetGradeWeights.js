import React, { useState, useEffect, useContext } from 'react';
import { Form, InputNumber, Button, Select, message } from 'antd';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';

const { Option } = Select;

const SetGradeWeights = () => {
    const [form] = Form.useForm();
    const [courses, setCourses] = useState([]);
    const { user } = useContext(AuthContext);

    useEffect(() => {
        const fetchCourses = async () => {
            try {
                const response = await axiosInstance.get('course-instances/');
                // 过滤出教师负责的课程实例
                const teacherCourses = response.data.filter(course => 
                    course.department.id === user.teacher_profile.departments[0].id // 假设教师至少关联一个部门
                );
                setCourses(teacherCourses);
            } catch (error) {
                console.error('Failed to fetch courses:', error);
                message.error('获取课程失败');
            }
        };
        fetchCourses();
    }, [user]);

    const onFinish = async (values) => {
        const { course_instance, daily_weight, final_weight } = values;
        if (daily_weight + final_weight !== 100) {
            message.error('平时分和期末分的总和必须为100%');
            return;
        }
        try {
            await axiosInstance.patch(`course-instances/${course_instance}/set_grade_weights/`, {
                daily_weight,
                final_weight,
            });
            message.success('分数占比设置成功');
            form.resetFields();
        } catch (error) {
            console.error('Failed to set grade weights:', error);
            message.error('设置分数占比失败');
        }
    };

    return (
        <div>
            <h2>设置成绩分数占比</h2>
            <Form form={form} layout="vertical" onFinish={onFinish}>
                <Form.Item
                    name="course_instance"
                    label="选择课程实例"
                    rules={[{ required: true, message: '请选择课程实例' }]}
                >
                    <Select placeholder="选择课程实例">
                        {courses.map(course => (
                            <Option key={course.id} value={course.id}>
                                {course.course_prototype.name} - {course.semester}
                            </Option>
                        ))}
                    </Select>
                </Form.Item>
                <Form.Item
                    name="daily_weight"
                    label="平时分占比 (%)"
                    rules={[{ required: true, message: '请输入平时分占比' }]}
                >
                    <InputNumber min={0} max={100} />
                </Form.Item>
                <Form.Item
                    name="final_weight"
                    label="期末分占比 (%)"
                    rules={[{ required: true, message: '请输入期末分占比' }]}
                >
                    <InputNumber min={0} max={100} />
                </Form.Item>
                <Form.Item>
                    <Button type="primary" htmlType="submit">
                        设置占比
                    </Button>
                </Form.Item>
            </Form>
        </div>
    );
};

export default SetGradeWeights;
