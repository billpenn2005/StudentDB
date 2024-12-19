// src/components/CourseSelection.js

import React, { useEffect, useState, useContext } from 'react';
import {
    List,
    Card,
    Button,
    Spin,
    Modal,
    message,
    Badge,
    Progress,
    Table,
    Row,
    Col,
} from 'antd';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';

const CourseSelection = () => {
    const { user, selectedCourses, fetchUser, fetchSelectedCourses, loading: authLoading } = useContext(AuthContext);
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [modalVisible, setModalVisible] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [courseDetails, setCourseDetails] = useState(null);
    const [detailsLoading, setDetailsLoading] = useState(false);
    const [timetableData, setTimetableData] = useState([]);

    // 定义课表的天数和节数
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const periods = [1, 2, 3, 4, 5]; // 根据模型修改为5节

    useEffect(() => {
        fetchCourses();
    }, []);

    useEffect(() => {
        if (!authLoading) {
            generateTimetable();
        }
    }, [selectedCourses, authLoading]);

    // 获取可选课程列表
    const fetchCourses = async () => {
        setLoading(true);
        try {
            const response = await axiosInstance.get('course-instances/list_available_courses/');
            console.log('Courses Response:', response.data); // Debug log
            if (Array.isArray(response.data)) {
                setCourses(response.data);
            } else if (response.data.results && Array.isArray(response.data.results)) {
                setCourses(response.data.results);
            } else {
                console.error('Unexpected courses data format:', response.data);
                message.error('获取课程列表失败，数据格式错误');
            }
        } catch (error) {
            console.error(error);
            message.error('获取课程列表失败');
        } finally {
            setLoading(false);
        }
    };

    // 查看课程详情
    const handleViewDetails = async (course) => {
        setSelectedCourse(course);
        setModalVisible(true);
        setDetailsLoading(true);
        try {
            const response = await axiosInstance.get(`course-instances/${course.id}/retrieve_course_details/`);
            setCourseDetails(response.data);
        } catch (error) {
            console.error(error);
            message.error('获取课程详情失败');
            setModalVisible(false);
        } finally {
            setDetailsLoading(false);
        }
    };

    // 选课功能
    const handleEnroll = async () => {
        if (!selectedCourse) return;

        setSubmitting(true);
        try {
            const response = await axiosInstance.post(`course-instances/${selectedCourse.id}/enroll/`);
            message.success(response.data.detail || '选课成功');
            setModalVisible(false);
            await fetchUser(); // 重新获取用户信息，更新已选课程
            await fetchSelectedCourses(); // 重新获取已选课程
            fetchCourses(); // 更新可选课程列表，可能课程容量已变化
            // 不需要手动调用 generateTimetable，因为 useEffect 已监听 selectedCourses
        } catch (error) {
            console.error(error);
            if (error.response && error.response.data) {
                // 处理多种错误信息
                const errors = Object.values(error.response.data).flat();
                message.error(errors.join(', ') || '选课失败');
            } else {
                message.error('选课失败');
            }
        } finally {
            setSubmitting(false);
        }
    };

    // 退选功能
    const handleUnenroll = async () => {
        if (!selectedCourse) return;

        setSubmitting(true);
        try {
            const response = await axiosInstance.post(`course-instances/${selectedCourse.id}/drop/`);
            message.success(response.data.detail || '退选成功');
            setModalVisible(false);
            await fetchUser(); // 重新获取用户信息，更新已选课程
            await fetchSelectedCourses(); // 重新获取已选课程
            fetchCourses(); // 更新可选课程列表，可能课程容量已变化
            // 不需要手动调用 generateTimetable，因为 useEffect 已监听 selectedCourses
        } catch (error) {
            console.error(error);
            if (error.response && error.response.data) {
                // 处理多种错误信息
                const errors = Object.values(error.response.data).flat();
                message.error(errors.join(', ') || '退选失败');
            } else {
                message.error('退选失败');
            }
        } finally {
            setSubmitting(false);
        }
    };

    // 获取已选课程的时间槽ID，用于冲突检测
    const selectedTimeSlots = Array.isArray(selectedCourses)
        ? selectedCourses.flatMap(sc => Array.isArray(sc.schedules) ? sc.schedules.map(schedule => ({
            day: schedule.day,
            period: schedule.period,
        })) : [])
        : [];

    // 计算已选课程的总学分
    const totalCredits = Array.isArray(selectedCourses)
        ? selectedCourses.reduce((sum, course) => sum + (course.course_prototype.credits || 0), 0)
        : 0;

    // 生成课表数据
    const generateTimetable = () => {
        console.log('Selected Courses:', selectedCourses); // 调试日志
        if (!Array.isArray(selectedCourses)) {
            setTimetableData([]);
            return;
        }
    
        const data = periods.map(period => {
            const row = { key: period, period: `${period}节` };
            days.forEach(day => {
                // 查找在该天和节次上有课程的课程实例
                const course = selectedCourses.find(sc => 
                    Array.isArray(sc.schedules) && sc.schedules.some(schedule => schedule.day === day && schedule.period === period)
                );
                row[day] = course ? {
                    id: course.id, // 添加课程ID以便点击时使用
                    name: course.course_prototype.name,
                    group: course.group,
                    teacher: course.teacher,
                } : null;
            });
            return row;
        });
        setTimetableData(data);
        console.log('Timetable Data:', data); // 调试日志
    };

    // 定义课表的列
    const timetableColumns = [
        {
            title: '节数',
            dataIndex: 'period',
            key: 'period',
            fixed: 'left',
            width: 80,
            align: 'center',
        },
        ...days.map(day => ({
            title: day,
            dataIndex: day,
            key: day,
            align: 'center',
            width: 200,
            render: (courseData) => (
                courseData ? (
                    <div onClick={() => handleViewDetails(courseData)} style={{ cursor: 'pointer' }}>
                        <strong>{courseData.name}</strong>
                        <div>班级: {courseData.group}</div>
                        <div>教师: {courseData.teacher}</div>
                    </div>
                ) : null
            )
        }))
    ];

    if (loading || authLoading) {
        return (
            <div style={{ textAlign: 'center', paddingTop: '50px' }}>
                <Spin tip="加载中..." size="large" />
            </div>
        );
    }

    return (
        <div style={{ padding: '20px' }}>
            <h2>选课系统</h2>
            <Row gutter={[16, 16]}>
                <Col xs={24} md={16}>
                    <h3>课表</h3>
                    <Table
                        columns={timetableColumns}
                        dataSource={timetableData}
                        pagination={false}
                        bordered
                        size="small"
                        style={{ marginBottom: '20px' }}
                        onRow={(record, rowIndex) => {
                            return {
                                onClick: (event) => {
                                    // 点击行时，如果有课程，则显示详情
                                    const clickedCourse = days.reduce((acc, day) => acc || record[day], null);
                                    if (clickedCourse) {
                                        handleViewDetails(clickedCourse);
                                    }
                                },
                            };
                        }}
                    />
                    <div style={{ textAlign: 'right', fontWeight: 'bold' }}>
                        总学分: {totalCredits}
                    </div>
                </Col>
                <Col xs={24} md={8}>
                    <h3>可选课程</h3>
                    <List
                        grid={{ gutter: 16, column: 1 }}
                        dataSource={courses}
                        renderItem={course => (
                            <List.Item key={course.id}>
                                <Card
                                    title={`${course.course_prototype.name} (${course.course_prototype.credits} 学分)`}
                                    bordered={false}
                                    style={{ width: '100%' }}
                                    size="small"
                                >
                                    <p>{course.description}</p>
                                    <Button
                                        type="primary"
                                        onClick={() => handleViewDetails(course)}
                                        style={{ marginRight: '10px' }}
                                        size="small"
                                    >
                                        查看详情
                                    </Button>
                                    {/* 根据您的需求，可以选择是否保留直接选课按钮 */}
                                    {/* <Button type="primary" onClick={() => handleEnroll(course)} size="small">
                                        选课
                                    </Button> */}
                                </Card>
                            </List.Item>
                        )}
                    />
                </Col>
            </Row>

            <Modal
                title={courseDetails ? `课程详情 - ${courseDetails.course_prototype.name}` : '课程详情'}
                visible={modalVisible}
                onCancel={() => setModalVisible(false)}
                footer={[
                    <Button key="cancel" onClick={() => setModalVisible(false)} size="small">
                        取消
                    </Button>,
                    selectedCourses && selectedCourses.find(sc => sc.id === selectedCourse?.id) ? (
                        <Button
                            key="unenroll"
                            type="danger"
                            onClick={() => handleUnenroll()}
                            loading={submitting}
                            size="small"
                        >
                            退选
                        </Button>
                    ) : (
                        <Button
                            key="enroll"
                            type="primary"
                            onClick={() => handleEnroll()}
                            disabled={
                                // 检查是否有时间冲突
                                courseDetails?.schedules?.some(cls =>
                                    selectedTimeSlots.some(slot => slot.day === cls.day && slot.period === cls.period)
                                ) || false
                            }
                            loading={submitting}
                            size="small"
                        >
                            选课
                        </Button>
                    )
                ]}
            >
                {detailsLoading ? (
                    <Spin tip="加载中..." />
                ) : courseDetails ? (
                    <div>
                        <p><strong>描述：</strong>{courseDetails.description}</p>
                        <p><strong>选择截止日期：</strong>{new Date(courseDetails.selection_deadline).toLocaleString()}</p>
                        <p><strong>是否最终化：</strong>{courseDetails.is_finalized ? '是' : '否'}</p>
                        <p><strong>教师：</strong>{courseDetails.teacher}</p> {/* 确保显示教师 */}
                        <h4>上课时间</h4>
                        <List
                            dataSource={courseDetails.schedules || []}
                            renderItem={schedule => {
                                const isConflict = selectedTimeSlots.some(slot => slot.day === schedule.day && slot.period === schedule.period);
                                const isFull = courseDetails.selected_students.length >= courseDetails.capacity;
                                const remaining = courseDetails.capacity - courseDetails.selected_students.length;

                                return (
                                    <List.Item key={`${schedule.day}-${schedule.period}`}>
                                        <Card
                                            title={`时间: ${schedule.day} 第${schedule.period}节`}
                                            bordered={false}
                                            style={{ width: '100%' }}
                                            size="small"
                                        >
                                            <p><strong>教师：</strong>{courseDetails.teacher}</p>
                                            <p><strong>容量：</strong>{courseDetails.selected_students.length} / {courseDetails.capacity} ({remaining}剩余)</p>
                                            <Progress
                                                percent={Math.round((courseDetails.selected_students.length / courseDetails.capacity) * 100)}
                                                status={isFull ? 'exception' : 'active'}
                                                showInfo={false}
                                                size="small"
                                            />
                                            {isFull && <Badge status="error" text="该班级已满" />}
                                            {isConflict && <Badge status="warning" text="时间冲突" />}
                                            {/* 移除每个时间段的选课按钮 */}
                                        </Card>
                                    </List.Item>
                                );
                            }}
                        />
                        <h4>学分信息</h4>
                        <p><strong>课程学分：</strong>{courseDetails.course_prototype.credits} 学分</p>
                    </div>
                ) : (
                    <p>没有课程详情可显示。</p>
                )}
            </Modal>
        </div>
    );

};

export default CourseSelection;
