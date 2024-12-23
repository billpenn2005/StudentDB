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
    const {
        user,
        selectedCourses,
        fetchUser,
        fetchSelectedCourses,
        loading: authLoading,
        currentSemester,
        fetchCurrentSemester,
    } = useContext(AuthContext);

    const [selectionBatches, setSelectionBatches] = useState([]);
    const [selectedBatchId, setSelectedBatchId] = useState(null);
    const [courses, setCourses] = useState([]); // 可选课程
    const [loading, setLoading] = useState(true);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [modalVisible, setModalVisible] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [courseDetails, setCourseDetails] = useState(null);
    const [detailsLoading, setDetailsLoading] = useState(false);
    const [timetableData, setTimetableData] = useState([]);
    const [selectedWeek, setSelectedWeek] = useState(1); // 存储选择的周数
    const [totalWeeks, setTotalWeeks] = useState(16); // 假设一个学期有16周，可以根据实际情况调整

    // 定义课表的天数和节数
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const periods = [1, 2, 3, 4, 5]; // 根据模型修改为5节

    useEffect(() => {
        fetchSelectionBatches();
        fetchCurrentSemester(); // 确保获取当前学期
    }, []);

    useEffect(() => {
        if (selectedBatchId) {
            fetchSelectedCourses(selectedBatchId); // 获取已选课程
            fetchAvailableCourses(selectedBatchId); // 获取可选课程
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
    }, [selectedCourses, authLoading, selectedWeek, currentSemester]); // 添加 currentSemester 依赖

    // 获取选课批次列表
    const fetchSelectionBatches = async () => {
        try {
            const response = await axiosInstance.get('selection-batches/');
            const batches = response.data.results || response.data; // 处理分页数据
            setSelectionBatches(batches);

            // 自动选择当前有效的批次（基于当前时间）
            const now = new Date();
            const currentBatch = batches.find(batch =>
                new Date(batch.start_selection_date) <= now && now <= new Date(batch.end_selection_date)
            );
            if (currentBatch) {
                setSelectedBatchId(currentBatch.id);
                // 计算当前周数
                if (currentSemester) {
                    const semesterStart = new Date(currentSemester.start_date);
                    const weekNumber = getWeekNumber(now, semesterStart);
                    const clampedWeekNumber = Math.min(Math.max(1, weekNumber), totalWeeks);
                    setSelectedWeek(clampedWeekNumber);
                } else {
                    message.warning('当前学期信息未获取，无法计算周数');
                }
            }
        } catch (error) {
            console.error('Fetch Selection Batches Error:', error);
            message.error('获取选课批次失败');
        }
    };

    // 获取可选课程列表，根据选中的批次
    // 修改为调用新的 available_courses API
    const fetchAvailableCourses = async (batchId) => {
        setLoading(true);
        try {
            const response = await axiosInstance.get(`selection-batches/${batchId}/available_courses/`);
            setCourses(response.data.available_courses);
        } catch (error) {
            console.error('Fetch Available Courses Error:', error);
            message.error('获取可选课程失败');
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
            await fetchSelectedCourses(selectedBatchId); // 重新获取已选课程
            await fetchAvailableCourses(selectedBatchId); // 更新可选课程列表，可能课程容量已变化
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
            await fetchSelectedCourses(selectedBatchId); // 重新获取已选课程
            await fetchAvailableCourses(selectedBatchId); // 更新可选课程列表，可能课程容量已变化
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
            frequency: schedule.frequency,
            exceptions: schedule.exceptions || [],
            start_week: schedule.start_week,
            end_week: schedule.end_week,
        })) : [])
        : [];

    console.log('Selected Time Slots:', selectedTimeSlots); // Debug log

    // 计算已选课程的总学分
    const totalCredits = Array.isArray(selectedCourses)
        ? selectedCourses.reduce((sum, course) => sum + (course.course_prototype.credits || 0), 0)
        : 0;

    // 判断课程是否在选定的周数安排
    const isCourseScheduledInWeek = (schedule, week) => {
        const { frequency, exceptions, start_week, end_week } = schedule;

        // 检查是否在例外周
        if (exceptions && exceptions.includes(week)) {
            return false;
        }

        // 检查是否在开始和结束周之间
        if (typeof start_week === 'number' && typeof end_week === 'number') {
            if (week < start_week || week > end_week) {
                return false;
            }
        }

        // 根据频率判断
        if((week) % frequency === 0) {
            return true;
        }
    };

    // 生成课表数据
    const generateTimetable = () => {
        console.log('Generating Timetable with Selected Courses:', selectedCourses); // Debug log
        console.log('Selected Week Number:', selectedWeek);
        if (!Array.isArray(selectedCourses) || !currentSemester) {
            setTimetableData([]);
            return;
        }

        const selectedWeekNumber = selectedWeek; // 使用选择的周数

        const data = periods.map(period => {
            const row = { key: period, period: `${period}节` };
            days.forEach(day => {
                const course = selectedCourses.find(sc =>
                    Array.isArray(sc.schedules) &&
                    sc.schedules.some(schedule =>
                        schedule.day === day &&
                        schedule.period === period &&
                        isCourseScheduledInWeek(schedule, selectedWeekNumber)
                    )
                );
                if (course) {
                    row[day] = {
                        id: course.id, // 确保包含课程ID
                        name: course.course_prototype.name,
                        group: course.group,
                        teacher: course.teacher?.user?.first_name ? `${course.teacher.user.first_name} ${course.teacher.user.last_name}` : '未知', // 使用可选链并提供默认值
                        week: selectedWeekNumber, // 使用选中的周数
                    };
                } else {
                    row[day] = null;
                }
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
                        <div>周数: 第{courseData.week}周</div> {/* 显示周数信息 */}
                    </div>
                ) : null
            )
        }))
    ];

    // 处理批次选择变化
    const handleBatchChange = (value) => {
        setSelectedBatchId(value);
    };

    // 处理周数选择变化
    const handleWeekChange = (value) => {
        setSelectedWeek(value);
    };

    // 计算当前周数
    const getWeekNumber = (currentDate, startDate) => {
        const oneWeek = 1000 * 60 * 60 * 24 * 7;
        const diffInTime = currentDate.getTime() - startDate.getTime();
        const diffInWeeks = Math.floor(diffInTime / oneWeek) + 1; // +1 因为第一周是1
        return diffInWeeks;
    };

    // 生成可选周数列表
    const generateWeekOptions = () => {
        const options = [];
        for (let i = 1; i <= totalWeeks; i++) {
            options.push(
                <Option key={i} value={i}>
                    第 {i} 周
                </Option>
            );
        }
        return options;
    };

    if (loading || authLoading || !currentSemester) {
        return (
            <div style={{ textAlign: 'center', paddingTop: '50px' }}>
                <Spin tip="加载中..." size="large" />
            </div>
        );
    }

    return (
        <div style={{ padding: '20px' }}>
            <h2>选课系统</h2>
            
            {/* 选课批次选择和周数选择 */}
            <div style={{ marginBottom: '20px', display: 'flex', alignItems: 'center' }}>
                <span style={{ marginRight: '10px' }}>选择选课批次:</span>
                <Select
                    style={{ width: 300, marginRight: '20px' }}
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

                {/* 添加周选择器 */}
                <span style={{ marginRight: '10px' }}>选择周数:</span>
                <Select
                    style={{ width: 150 }}
                    placeholder="请选择周数"
                    value={selectedWeek}
                    onChange={handleWeekChange}
                >
                    {generateWeekOptions()}
                </Select>
            </div>

            <Row gutter={[16, 16]}>
                {/* 课表部分 */}
                <Col xs={24} md={16}>
                    <h3>课表 - 第 {selectedWeek} 周</h3>
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
                                    <p>
                                        <strong>教师：</strong>
                                        {course.teacher?.user?.first_name && course.teacher?.user?.last_name
                                            ? `${course.teacher.user.first_name} ${course.teacher.user.last_name}`
                                            : '未知'}
                                    </p> {/* 使用可选链并提供默认值 */}
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
                                        <p>
                                            <strong>教师：</strong>
                                            {course.teacher?.user?.first_name && course.teacher?.user?.last_name
                                                ? `${course.teacher.user.first_name} ${course.teacher.user.last_name}`
                                                : '未知'}
                                        </p> {/* 使用可选链并提供默认值 */}
                                        <p><strong>班级：</strong> {course.group}</p>
                                        <p><strong>选课批次：</strong> {course.selection_batch ? course.selection_batch.name : '未分配'}</p>
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
                                    (
                                        isCourseScheduledInWeek(cls, selectedWeek)
                                    ) &&
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
                        <p>
                            <strong>教师：</strong>
                            {courseDetails.teacher?.user?.first_name && courseDetails.teacher?.user?.last_name
                                ? `${courseDetails.teacher.user.first_name} ${courseDetails.teacher.user.last_name}`
                                : '未知'}
                        </p> {/* 使用可选链并提供默认值 */}
                        <h4>上课时间</h4>
                        <List
                            dataSource={courseDetails.schedules || []}
                            renderItem={schedule => {
                                const isConflict = selectedTimeSlots.some(slot => 
                                    slot.day === schedule.day &&
                                    slot.period === schedule.period &&
                                    isCourseScheduledInWeek(schedule, selectedWeek)
                                );
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
                                            <p>
                                                <strong>教师：</strong>
                                                {courseDetails.teacher?.user?.first_name && courseDetails.teacher?.user?.last_name
                                                    ? `${courseDetails.teacher.user.first_name} ${courseDetails.teacher.user.last_name}`
                                                    : '未知'}
                                            </p> {/* 使用可选链并提供默认值 */}
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