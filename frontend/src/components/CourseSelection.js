// src/components/CourseSelection.js

import React, { useEffect, useState, useContext } from 'react';
import { List, Card, Button, Spin, Modal, message, Badge, Progress } from 'antd';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';

const CourseSelection = () => {
    const { user, fetchUser } = useContext(AuthContext);
    const [courses, setCourses] = useState([]);
    const [classes, setClasses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [courseClasses, setCourseClasses] = useState([]);
    const [modalVisible, setModalVisible] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchCourses();
    }, []);

    const fetchCourses = async () => {
        setLoading(true);
        try {
            const response = await axiosInstance.get('courses/');
            setCourses(response.data);
        } catch (error) {
            console.error(error);
            message.error('获取课程列表失败');
        } finally {
            setLoading(false);
        }
    };

    const fetchClasses = async (courseId) => {
        setLoading(true);
        try {
            // 使用新的 API 路径获取特定课程的班级实例
            const response = await axiosInstance.get(`classes/by_course/?course_id=${courseId}`);
            setCourseClasses(response.data);
        } catch (error) {
            console.error(error);
            message.error('获取班级信息失败');
        } finally {
            setLoading(false);
        }
    };
    const handleViewDetails = (course) => {
        setSelectedCourse(course);
        fetchClasses(course.id);
        setModalVisible(true);
    };

    const handleSelectClass = async (classInstance) => {
        setSubmitting(true);
        try {
            await axiosInstance.post('course-selections/', { class_instance_id: classInstance.id });
            message.success('选课成功');
            setModalVisible(false);
            await fetchUser(); // 重新获取用户信息，更新已选课程
        } catch (error) {
            console.error(error);
            if (error.response && error.response.data) {
                message.error(Object.values(error.response.data).join(', ') || '选课失败');
            } else {
                message.error('选课失败');
            }
        } finally {
            setSubmitting(false);
        }
    };

    // 获取已选课程的时间槽ID，用于冲突检测
    const selectedTimeSlots = user && user.selected_courses
        ? user.selected_courses.map(sc => sc.class_instance.time_slot.id)
        : [];

    if (loading) {
        return (
            <div style={{ textAlign: 'center', paddingTop: '50px' }}>
                <Spin tip="加载中..." size="large" />
            </div>
        );
    }

    return (
        <div>
            <h2>选课</h2>
            <List
                grid={{ gutter: 16, column: 4 }}
                dataSource={courses}
                renderItem={course => (
                    <List.Item>
                        <Card title={course.name} bordered={false}>
                            <p>{course.description}</p>
                            <Button type="primary" onClick={() => handleViewDetails(course)}>
                                查看详情
                            </Button>
                        </Card>
                    </List.Item>
                )}
            />

            <Modal
                title={selectedCourse ? `选择班级 - ${selectedCourse.name}` : '选择班级'}
                visible={modalVisible}
                onCancel={() => setModalVisible(false)}
                footer={null}
            >
                <List
                    dataSource={courseClasses}
                    renderItem={cls => {
                        const isConflict = selectedTimeSlots.includes(cls.time_slot.id);
                        const isAlreadySelected = user && user.selected_courses.some(
                            sc => sc.class_instance.id === cls.id
                        );
                        const isFull = cls.enrolled_count >= cls.capacity; // 判断班级是否已满
                        const remaining = cls.capacity - cls.enrolled_count;

                        return (
                            <List.Item>
                                <Card title={`班级: ${cls.group}`} bordered={false}>
                                    <p>教师: {cls.teacher}</p>
                                    <p>时间: 第{cls.time_slot.period}节</p>
                                    <p>容量: {cls.enrolled_count} / {cls.capacity} ({remaining}剩余)</p>
                                    <Progress percent={(cls.enrolled_count / cls.capacity) * 100} status={isFull ? 'exception' : 'active'} />
                                    <Button
                                        type="primary"
                                        onClick={() => handleSelectClass(cls)}
                                        disabled={isConflict || isAlreadySelected || isFull}
                                        style={{ marginTop: '10px' }}
                                        loading={submitting}
                                    >
                                        {isFull ? '已满' : isConflict ? '时间冲突' : isAlreadySelected ? '已选' : '选课'}
                                    </Button>
                                    {isFull && <Badge status="error" text="该班级已满" />}
                                </Card>
                            </List.Item>
                        );
                    }}
                />
            </Modal>
        </div>
    );
};

export default CourseSelection;
