// src/components/MyCourses.js

import React, { useEffect, useContext, useState } from 'react';
import { List, Card, Button, Spin, Modal, message } from 'antd';
import { AuthContext } from '../contexts/AuthContext';
import axiosInstance from '../axiosInstance';

const SelectedCourses = () => {
    const { selectedCourses, fetchSelectedCourses, fetchUser, loading: authLoading } = useContext(AuthContext);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        const loadSelectedCourses = async () => {
            setLoading(true);
            await fetchSelectedCourses();
            setLoading(false);
        };
        loadSelectedCourses();
    }, [fetchSelectedCourses]);

    const handleUnenroll = (course) => {
        console.log('Unenrolling from course:', course.teacher?.user?.first_name);

        Modal.confirm({
            title: '确认退选',
            content: `您确定要退选课程 "${course.course_prototype.name}" 吗？`,
            okText: '确认',
            cancelText: '取消',
            onOk: async () => {
                setSubmitting(true);
                try {
                    await axiosInstance.post(`course-instances/${course.id}/drop/`);
                    message.success('退选成功');
                    await fetchUser();
                    await fetchSelectedCourses();
                } catch (error) {
                    console.error(error);
                    message.error('退选失败');
                } finally {
                    setSubmitting(false);
                }
            },
        });
    };

    if (loading || authLoading) {
        return (
            <div style={{ textAlign: 'center', paddingTop: '50px' }}>
                <Spin tip="加载中..." size="large" />
            </div>
        );
    }

    return (
        <div style={{ padding: '20px' }}>
            <h2>已选课程</h2>
            {selectedCourses.length === 0 ? (
                <p>您当前没有选中的课程。</p>
            ) : (
                <List
                    grid={{ gutter: 16, column: 1 }}
                    dataSource={selectedCourses}
                    renderItem={course => (
                        <List.Item key={course.id}>
                            <Card
                                title={`${course.course_prototype.name} (${course.course_prototype.credits} 学分)`}
                                bordered
                                size="small"
                            >
                                <p><strong>描述：</strong> {course.description}</p>
                                <p>
                                    <strong>教师：</strong> 
                                    {course.teacher && course.teacher.user 
                                        ? `${course.teacher.user.first_name} ${course.teacher.user.last_name}` 
                                        : '未知'}
                                </p>
                                <p><strong>班级：</strong> {course.group}</p>
                                <Button
                                    type="danger"
                                    onClick={() => handleUnenroll(course)}
                                    loading={submitting}
                                    size="small"
                                >
                                    退选
                                </Button>
                            </Card>
                        </List.Item>
                    )}
                />
            )}
        </div>
    );
};

export default SelectedCourses;