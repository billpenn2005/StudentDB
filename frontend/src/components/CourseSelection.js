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
    Select,
} from 'antd';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';

const { Option } = Select;

const CourseSelection = () => {
    const { user, selectedCourses, fetchUser, fetchSelectedCourses, loading: authLoading } = useContext(AuthContext);
    const [selectionBatches, setSelectionBatches] = useState([]);
    const [selectedBatchId, setSelectedBatchId] = useState(null);
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
        fetchSelectionBatches();
    }, []);

    useEffect(() => {
        if (selectedBatchId) {
            fetchCourses(selectedBatchId);
        } else {
            setCourses([]);
            setLoading(false);
        }
    }, [selectedBatchId]);

    useEffect(() => {
        console.log('selectedCourses changed:', selectedCourses);
        if (!authLoading) {
            generateTimetable();
        }
    }, [selectedCourses, authLoading]);

    // 获取选课批次列表
    const fetchSelectionBatches = async () => {
        try {
            const response = await axiosInstance.get('selection-batches/');
            setSelectionBatches(response.data.results || response.data); // 确保处理不同格式的数据
            // 自动选择当前有效的批次（基于当前时间）
            const now = new Date();
            const currentBatch = response.data.find(batch => 
                new Date(batch.start_selection_date) <= now && now <= new Date(batch.end_selection_date)
            );
            if (currentBatch) {
                setSelectedBatchId(currentBatch.id);
            }
        } catch (error) {
            console.error('Fetch Selection Batches Error:', error);
            message.error('获取选课批次失败');
        }
    };

    // 获取可选课程列表，根据选中的批次
    const fetchCourses = async (batchId) => {
        setLoading(true);
        try {
            const response = await axiosInstance.get(`selection-batches/${batchId}/course_instances/`);
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
            console.error('Fetch Courses Error:', error);
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
            console.log('Course Details Response:', response); // Debug log
            setCourseDetails(response.data);
        } catch (error) {
            console.error('Fetch Course Details Error:', error);
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
            console.log('Enroll Response:', response.data); // Debug log
            message.success(response.data.detail || '选课成功');
            setModalVisible(false);
            await fetchUser(); // 重新获取用户信息，更新已选课程
            await fetchSelectedCourses(); // 重新获取已选课程
            await fetchCourses(selectedBatchId); // 更新可选课程列表，可能课程容量已变化
            // 不需要手动调用 generateTimetable，因为 useEffect 已监听 selectedCourses
        } catch (error) {
            console.error('Enroll Error:', error);
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
    const handleUnenroll = async (course) => { // 接受一个 course 参数
        if (!course) return;

        setSubmitting(true);
        try {
            const response = await axiosInstance.post(`course-instances/${course.id}/drop/`); // 确保端点正确
            console.log('Unenroll Response:', response.data); // Debug log
            message.success(response.data.detail || '退选成功');
            await fetchUser(); // 重新获取用户信息，更新已选课程
            await fetchSelectedCourses(); // 重新获取已选课程
            await fetchCourses(selectedBatchId); // 更新可选课程列表，可能课程容量已变化
        } catch (error) {
            console.error('Unenroll Error:', error);
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

    console.log('Selected Time Slots:', selectedTimeSlots); // Debug log

    // 计算已选课程的总学分
    const totalCredits = Array.isArray(selectedCourses)
        ? selectedCourses.reduce((sum, course) => sum + (course.course_prototype.credits || 0), 0)
        : 0;

    // 生成课表数据
    const generateTimetable = () => {
        console.log('Generating Timetable with Selected Courses:', selectedCourses); // Debug log
        if (!Array.isArray(selectedCourses)) {
            setTimetableData([]);
            return;
        }
    
        const data = periods.map(period => {
            const row = { key: period, period: `${period}节` };
            days.forEach(day => {
                const course = selectedCourses.find(sc => 
                    Array.isArray(sc.schedules) && sc.schedules.some(schedule => schedule.day === day && schedule.period === period)
                );
                row[day] = course ? {
                    id: course.id, // 确保包含课程ID
                    name: course.course_prototype.name,
                    group: course.group,
                    teacher: course.teacher?.user?.first_name ? `${course.teacher.user.first_name} ${course.teacher.user.last_name}` : '未知', // 使用可选链并提供默认值
                } : null;
            });
            return row;
        });
        setTimetableData(data);
        console.log('Timetable Data:', data); // Debug log
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
                        <div>教师: {courseData.teacher}</div> {/* 确保 teacher 是字符串 */}
                    </div>
                ) : null
            )
        }))
    ];

    // 处理批次选择变化
    const handleBatchChange = (value) => {
        setSelectedBatchId(value);
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
            <h2>选课系统</h2>
            
            {/* 选课批次选择 */}
            <div style={{ marginBottom: '20px' }}>
                <span style={{ marginRight: '10px' }}>选择选课批次:</span>
                <Select
                    style={{ width: 300 }}
                    placeholder="请选择选课批次"
                    value={selectedBatchId}
                    onChange={handleBatchChange}
                >
                    {selectionBatches.map(batch => (
                        <Option key={batch.id} value={batch.id}>
                            {batch.name} ({new Date(batch.start_selection_date).toLocaleString()} - {new Date(batch.end_selection_date).toLocaleString()})
                        </Option>
                    ))}
                </Select>
            </div>

            <Row gutter={[16, 16]}>
                {/* 课表部分 */}
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

                {/* 可选课程部分 */}
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
                                    <p><strong>教师：</strong> {course.teacher?.user?.first_name && course.teacher?.user?.last_name ? `${course.teacher.user.first_name} ${course.teacher.user.last_name}` : '未知'}</p> {/* 使用可选链并提供默认值 */}
                                    <p><strong>班级：</strong> {course.group}</p>
                                    <Button
                                        type="primary"
                                        onClick={() => handleViewDetails(course)}
                                        style={{ marginRight: '10px' }}
                                        size="small"
                                    >
                                        查看详情
                                    </Button>
                                    {/* 添加禁用选课按钮逻辑 */}
                                    <Button
                                        type="primary"
                                        onClick={() => handleEnroll()}
                                        size="small"
                                        disabled={course.is_finalized} // 禁用条件
                                    >
                                        选课
                                    </Button>
                                    {course.is_finalized && (
                                        <Badge status="warning" text="已截止选课" style={{ marginLeft: '10px' }} />
                                    )}
                                </Card>
                            </List.Item>
                        )}
                    />
                </Col>
            </Row>

            {/* 已选课程部分 */}
            <Row gutter={[16, 16]} style={{ marginTop: '40px' }}>
                <Col xs={24}>
                    <h3>已选课程</h3>
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
                                        <p><strong>教师：</strong> {course.teacher?.user?.first_name && course.teacher?.user?.last_name ? `${course.teacher.user.first_name} ${course.teacher.user.last_name}` : '未知'}</p> {/* 使用可选链并提供默认值 */}
                                        <p><strong>班级：</strong> {course.group}</p>
                                        <Button
                                            type="danger"
                                            onClick={() => handleUnenroll(course)}
                                            loading={submitting}
                                            size="small"
                                            disabled={course.is_finalized} // 禁用退选按钮
                                        >
                                            退选
                                        </Button>
                                        {course.is_finalized && (
                                            <Badge status="warning" text="已截止退选" style={{ marginLeft: '10px' }} />
                                        )}
                                    </Card>
                                </List.Item>
                            )}
                        />
                    )}
                </Col>
            </Row>

            {/* 课程详情模态框 */}
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
                            onClick={() => handleUnenroll(selectedCourse)}
                            loading={submitting}
                            size="small"
                            disabled={courseDetails?.is_finalized} // 禁用退选按钮
                        >
                            退选
                        </Button>
                    ) : (
                        <Button
                            key="enroll"
                            type="primary"
                            onClick={() => handleEnroll()}
                            disabled={
                                // 检查是否有时间冲突或课程已满或选课截止日期已过或课程已最终化
                                courseDetails?.schedules?.some(cls =>
                                    selectedTimeSlots.some(slot => slot.day === cls.day && slot.period === cls.period)
                                ) ||
                                courseDetails?.selected_students.length >= courseDetails?.capacity ||
                                new Date(courseDetails?.selection_deadline) < new Date() ||
                                courseDetails?.is_finalized // 添加最终化检查
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
                        <p><strong>教师：</strong>{courseDetails.teacher?.user?.first_name && courseDetails.teacher?.user?.last_name ? `${courseDetails.teacher.user.first_name} ${courseDetails.teacher.user.last_name}` : '未知'}</p> {/* 使用可选链并提供默认值 */}
                        <h4>上课时间</h4>
                        <List
                            dataSource={courseDetails.schedules || []}
                            renderItem={schedule => {
                                const isConflict = selectedTimeSlots.some(slot => slot.day === schedule.day && slot.period === schedule.period);
                                const isFull = courseDetails.selected_students.length >= courseDetails.capacity;
                                const remaining = courseDetails.capacity - courseDetails.selected_students.length;

                                console.log(`Schedule: ${schedule.day} 第${schedule.period}节, Conflict: ${isConflict}, Full: ${isFull}`); // Debug log

                                return (
                                    <List.Item key={`${schedule.day}-${schedule.period}`}>
                                        <Card
                                            title={`时间: ${schedule.day} 第${schedule.period}节`}
                                            bordered={false}
                                            style={{ width: '100%' }}
                                            size="small"
                                        >
                                            <p><strong>教师：</strong>{courseDetails.teacher?.user?.first_name && courseDetails.teacher?.user?.last_name ? `${courseDetails.teacher.user.first_name} ${courseDetails.teacher.user.last_name}` : '未知'}</p> {/* 使用可选链并提供默认值 */}
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
