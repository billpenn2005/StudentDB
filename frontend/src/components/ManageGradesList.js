// src/components/ManageGradesList.js

import React, { useEffect, useState, useContext } from 'react';
import { Table, Button, Spin, Alert } from 'antd';
import { Link } from 'react-router-dom';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Select } from 'antd';

const ManageGradesList = () => {
    const { user, currentSemester, fetchCurrentSemester } = useContext(AuthContext);
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedCourseId, setSelectedCourseId] = useState(null);
    const navigate = useNavigate();

    const fetchCourses = async () => {
        try {
            const response = await axiosInstance.get('/course-instances/', {
                params: {
                    teacher: user.teacher_id,
                    semester: currentSemester?.id // 只获取当前学期
                }
            });
            setCourses(response.data.results || []);
        } catch (err) {
            setError('无法获取课程列表。');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (!currentSemester) {
            fetchCurrentSemester();
        }
        if (currentSemester && user) {
            fetchCourses();
        }
    }, [currentSemester, user, fetchCurrentSemester]);

    if (loading) {
        return <Spin tip="加载中..." />;
    }

    if (error) {
        return <Alert message={error} type="error" />;
    }

    return (
        <div>
            <h2>成绩录入（当前学期）</h2>
            <div style={{ marginBottom: '16px' }}>
                <Select
                    placeholder="请选择要录入成绩的课程"
                    style={{ width: 300 }}
                    onChange={value => setSelectedCourseId(value)}
                    value={selectedCourseId}
                >
                    {courses.map(course => (
                        <Select.Option key={course.id} value={course.id}>
                            {course.course_prototype.name}
                        </Select.Option>
                    ))}
                </Select>
                <Button
                    type="primary"
                    disabled={!selectedCourseId}
                    style={{ marginLeft: '8px' }}
                    onClick={() => {
                        navigate(`/manage-grades/${selectedCourseId}`);
                    }}
                >
                    录入成绩
                </Button>
            </div>
            {/* 也可在此使用表格或其他展示方式 */}
        </div>
    );
};

export default ManageGradesList;
