// src/components/CourseSelection.js

import React, { useEffect, useState, useContext, useMemo, useCallback } from 'react';
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
    const [courses, setCourses] = useState([]); // Available courses
    const [loading, setLoading] = useState(true);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [modalVisible, setModalVisible] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [courseDetails, setCourseDetails] = useState(null);
    const [detailsLoading, setDetailsLoading] = useState(false);
    const [timetableData, setTimetableData] = useState([]);
    const [selectedWeek, setSelectedWeek] = useState(1); // Selected week number
    const [totalWeeks, setTotalWeeks] = useState(16); // Assuming a 16-week semester

    // Define timetable days and periods
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const periods = [1, 2, 3, 4, 5]; // Adjust based on your schedule

    /**
     * Calculate the current week number based on the semester start date.
     * @param {Date} currentDate - The current date.
     * @param {Date} startDate - The semester start date.
     * @returns {number} - The current week number.
     */
    const getWeekNumber = (currentDate, startDate) => {
        const oneWeek = 1000 * 60 * 60 * 24 * 7;
        const diffInTime = currentDate.getTime() - startDate.getTime();
        const diffInWeeks = Math.floor(diffInTime / oneWeek) + 1; // +1 because the first week is 1
        return diffInWeeks;
    };

    /**
     * Determine if a course is scheduled in a particular week.
     * @param {Object} schedule - The schedule object.
     * @param {number} week - The selected week number.
     * @returns {boolean} - True if scheduled, else false.
     */
    const isCourseScheduledInWeek = (schedule, week) => {
        const { frequency, exceptions, start_week, end_week } = schedule;

        // Exclude if the week is in exceptions
        if (exceptions && exceptions.includes(week)) {
            return false;
        }

        // Ensure the week is within start and end weeks
        if (typeof start_week === 'number' && typeof end_week === 'number') {
            if (week < start_week || week > end_week) {
                return false;
            }
        }

        // Check frequency
        if (frequency > 0 && week % frequency === 0) {
            return true;
        }

        return false; // Default to not scheduled
    };

    /**
     * Fetch selection batches from the API.
     */
    const fetchSelectionBatches = useCallback(async () => {
        try {
            const response = await axiosInstance.get('selection-batches/');
            const batches = response.data.results || response.data; // Handle pagination
            setSelectionBatches(batches);

            // Auto-select the current active batch based on dates
            const now = new Date();
            const currentBatch = batches.find(batch =>
                new Date(batch.start_selection_date) <= now && now <= new Date(batch.end_selection_date)
            );
            if (currentBatch) {
                setSelectedBatchId(currentBatch.id);
                // Calculate the current week number
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
        } finally {
            setLoading(false);
        }
    }, [currentSemester, totalWeeks]);

    /**
     * Fetch available courses based on the selected batch.
     * @param {number} batchId - The selected batch ID.
     */
    const fetchAvailableCourses = useCallback(async (batchId) => {
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
    }, []);

    /**
     * View course details by fetching them from the API.
     * @param {Object} course - The course object.
     */
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

    /**
     * Enroll in a specific course.
     * @param {Object} course - The course object to enroll in.
     */
    const handleEnroll = async (course) => {
        if (!course) return;

        setSubmitting(true);
        try {
            const response = await axiosInstance.post(`course-instances/${course.id}/enroll/`);
            console.log('Enroll Response:', response.data); // Debug log
            message.success(response.data.detail || '选课成功');
            setModalVisible(false);
            await fetchUser(); // Re-fetch user info
            await fetchSelectedCourses(selectedBatchId); // Re-fetch selected courses
            await fetchAvailableCourses(selectedBatchId); // Update available courses
        } catch (error) {
            console.error('Enroll Error:', error);
            if (error.response && error.response.data) {
                const errors = Object.values(error.response.data).flat();
                message.error(errors.join(', ') || '选课失败');
            } else {
                message.error('选课失败');
            }
        } finally {
            setSubmitting(false);
        }
    };

    /**
     * Unenroll from a specific course.
     * @param {Object} course - The course object to unenroll from.
     */
    const handleUnenroll = async (course) => {
        if (!course) return;

        setSubmitting(true);
        try {
            const response = await axiosInstance.post(`course-instances/${course.id}/drop/`);
            console.log('Unenroll Response:', response.data); // Debug log
            message.success(response.data.detail || '退选成功');
            await fetchUser(); // Re-fetch user info
            await fetchSelectedCourses(selectedBatchId); // Re-fetch selected courses
            await fetchAvailableCourses(selectedBatchId); // Update available courses
        } catch (error) {
            console.error('Unenroll Error:', error);
            if (error.response && error.response.data) {
                const errors = Object.values(error.response.data).flat();
                message.error(errors.join(', ') || '退选失败');
            } else {
                message.error('退选失败');
            }
        } finally {
            setSubmitting(false);
        }
    };

    /**
     * Generate the timetable based on selected courses and week.
     */
    const generateTimetable = useCallback(() => {
        if (!Array.isArray(selectedCourses) || !currentSemester) {
            setTimetableData([]);
            return;
        }
    
        const selectedWeekNumber = selectedWeek;
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
                row[day] = course ? {
                    id: course.id,
                    name: course.course_prototype.name,
                    group: course.group,
                    teacher: course.teacher?.user?.first_name ? 
                        `${course.teacher.user.first_name} ${course.teacher.user.last_name}` : '未知',
                    week: selectedWeekNumber,
                } : null;
            });
            return row;
        });
        setTimetableData(data);
    }, [selectedCourses, selectedWeek, periods, days, currentSemester]);
    

    /**
     * Generate options for the week selector.
     * @returns {Array} - Array of Option components.
     */
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

    // Fetch selection batches on component mount
    useEffect(() => {
        if (currentSemester) {
            fetchSelectionBatches();
        }
    }, [currentSemester]); // 只依赖currentSemester

    useEffect(() => {
        if (selectedBatchId) {
            Promise.all([
                fetchAvailableCourses(selectedBatchId),
            ]).finally(() => {
                setLoading(false);
            });
        } else {
            setCourses([]);
            setLoading(false);
        }
    }, [selectedBatchId, fetchAvailableCourses]); // 移除fetchSelectedCourses依赖

    // Generate timetable whenever selected courses, week, or semester changes
    useEffect(() => {
        if (!authLoading && currentSemester && selectedCourses.length > 0) {
            generateTimetable();
        }
    }, [authLoading, currentSemester, selectedWeek]); // 简化依赖
    // Compute selected time slots using useMemo for performance
    const selectedTimeSlots = useMemo(() => (
        Array.isArray(selectedCourses)
            ? selectedCourses.flatMap(sc => 
                Array.isArray(sc.schedules) 
                    ? sc.schedules.map(schedule => ({
                        day: schedule.day,
                        period: schedule.period,
                        frequency: schedule.frequency,
                        exceptions: schedule.exceptions || [],
                        start_week: schedule.start_week,
                        end_week: schedule.end_week,
                    })) 
                    : []
            )
            : []
    ), [selectedCourses]);

    //console.log('Selected Time Slots:', selectedTimeSlots); // Debug log

    // Calculate total credits
    const totalCredits = useMemo(() => {
        return Array.isArray(selectedCourses)
            ? selectedCourses.reduce((sum, course) => sum + (course.course_prototype.credits || 0), 0)
            : 0;
    }, [selectedCourses]);

    // Define timetable columns
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
                        <div>周数: 第{courseData.week}周</div>
                    </div>
                ) : null
            )
        }))
    ];

    /**
     * Handle changes in batch selection.
     * @param {number} value - The selected batch ID.
     */
    const handleBatchChange = (value) => {
        setSelectedBatchId(value);
    };

    /**
     * Handle changes in week selection.
     * @param {number} value - The selected week number.
     */
    const handleWeekChange = (value) => {
        setSelectedWeek(value);
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
            
            {/* Selection Batches and Week Selector */}
            <div style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', flexWrap: 'wrap' }}>
                <span style={{ marginRight: '10px' }}>选择选课批次:</span>
                <Select
                    style={{ width: 300, marginRight: '20px', minWidth: '200px' }}
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

                {/* Week Selector */}
                <span style={{ marginRight: '10px' }}>选择周数:</span>
                <Select
                    style={{ width: 150, minWidth: '100px' }}
                    placeholder="请选择周数"
                    value={selectedWeek}
                    onChange={handleWeekChange}
                >
                    {generateWeekOptions()}
                </Select>
            </div>

            <Row gutter={[16, 16]}>
                {/* Timetable Section */}
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
                                    // Click row to view course details if a course exists
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

                {/* Available Courses Section */}
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
                                    </p>
                                    <p><strong>班级：</strong> {course.group}</p>
                                    <Button
                                        type="primary"
                                        onClick={() => handleViewDetails(course)}
                                        style={{ marginRight: '10px' }}
                                        size="small"
                                    >
                                        查看详情
                                    </Button>
                                    <Button
                                        type="primary"
                                        onClick={() => handleEnroll(course)} // Pass the specific course
                                        size="small"
                                        disabled={course.is_finalized} // Disable if enrollment is finalized
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

            {/* Selected Courses Section */}
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
                                        </p>
                                        <p><strong>班级：</strong> {course.group}</p>
                                        <p><strong>选课批次：</strong> {course.selection_batch ? course.selection_batch.name : '未分配'}</p>
                                        <Button
                                            type="danger"
                                            onClick={() => handleUnenroll(course)}
                                            loading={submitting}
                                            size="small"
                                            disabled={course.is_finalized} // Disable if unenrollment is finalized
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

            {/* Course Details Modal */}
            <Modal
                title={courseDetails ? `课程详情 - ${courseDetails.course_prototype.name}` : '课程详情'}
                visible={modalVisible}
                onCancel={() => setModalVisible(false)}
                footer={[
                    <Button key="cancel" onClick={() => setModalVisible(false)} size="small">
                        取消
                    </Button>,
                    selectedCourse && selectedCourses.find(sc => sc.id === selectedCourse.id) ? (
                        <Button
                            key="unenroll"
                            type="danger"
                            onClick={() => handleUnenroll(selectedCourse)}
                            loading={submitting}
                            size="small"
                            disabled={courseDetails?.is_finalized} // Disable if unenrollment is finalized
                        >
                            退选
                        </Button>
                    ) : (
                        <Button
                            key="enroll"
                            type="primary"
                            onClick={() => handleEnroll(selectedCourse)}
                            disabled={
                                // Check for time conflicts, capacity, deadlines, or finalization
                                courseDetails?.schedules?.some(cls =>
                                    (
                                        isCourseScheduledInWeek(cls, selectedWeek)
                                    ) &&
                                    selectedTimeSlots.some(slot => slot.day === cls.day && slot.period === cls.period)
                                ) ||
                                courseDetails?.selected_students.length >= courseDetails?.capacity ||
                                new Date(courseDetails?.selection_deadline) < new Date() ||
                                courseDetails?.is_finalized // Check finalization
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
                        </p>
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
                                            </p>
                                            <p><strong>容量：</strong>{courseDetails.selected_students.length} / {courseDetails.capacity} ({remaining}剩余)</p>
                                            <Progress
                                                percent={Math.round((courseDetails.selected_students.length / courseDetails.capacity) * 100)}
                                                status={isFull ? 'exception' : 'active'}
                                                showInfo={false}
                                                size="small"
                                            />
                                            {isFull && <Badge status="error" text="该班级已满" />}
                                            {isConflict && <Badge status="warning" text="时间冲突" />}
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
