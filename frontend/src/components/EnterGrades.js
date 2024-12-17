// src/components/EnterGrades.js

import React, { useState, useEffect } from 'react';
import { Table, InputNumber, Button, message, Spin } from 'antd';
import axiosInstance from '../axiosInstance';

const EnterGrades = () => {
    const [grades, setGrades] = useState([]);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    const fetchGradesToEnter = async () => {
        try {
            const response = await axiosInstance.get('/s-grades/');
            console.log('EnterGrades API Response:', response.data); // 调试日志
            const data = response.data.results || response.data;
            if (!Array.isArray(data)) {
                throw new TypeError('Expected grades data to be an array');
            }
            setGrades(data);
        } catch (error) {
            console.error('Failed to fetch grades:', error);
            message.error('获取成绩信息失败');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchGradesToEnter();
    }, []);

    const handleChange = (id, field, value) => {
        setGrades(prevGrades =>
            prevGrades.map(grade =>
                grade.id === id ? { ...grade, [field]: value } : grade
            )
        );
    };

    const handleSubmit = async () => {
        setSubmitting(true);
        try {
            const updatePromises = grades.map(grade =>
                axiosInstance.patch(`/s-grades/${grade.id}/`, {
                    daily_score: grade.daily_score,
                    final_score: grade.final_score,
                })
            );
            await Promise.all(updatePromises);
            message.success('成绩更新成功');
            fetchGradesToEnter();
        } catch (error) {
            console.error('Failed to update grades:', error);
            message.error(error.response?.data?.detail || '成绩更新失败');
        } finally {
            setSubmitting(false);
        }
    };

    const columns = [
        {
            title: '学生姓名',
            dataIndex: 'student',
            key: 'student_name',
            render: (student) => `${student.user.first_name} ${student.user.last_name}`,
        },
        {
            title: '课程名称',
            dataIndex: 'course_instance',
            key: 'course_name',
            render: (courseInstance) => courseInstance.course_prototype.name,
        },
        {
            title: '平时分',
            dataIndex: 'daily_score',
            key: 'daily_score',
            render: (text, record) => (
                <InputNumber
                    min={0}
                    max={100}
                    value={record.daily_score}
                    onChange={(value) => handleChange(record.id, 'daily_score', value)}
                />
            ),
        },
        {
            title: '期末分',
            dataIndex: 'final_score',
            key: 'final_score',
            render: (text, record) => (
                <InputNumber
                    min={0}
                    max={100}
                    value={record.final_score}
                    onChange={(value) => handleChange(record.id, 'final_score', value)}
                />
            ),
        },
        {
            title: '总分',
            dataIndex: 'total_score',
            key: 'total_score',
        },
    ];

    if (loading) {
        return <Spin tip="加载中..." />;
    }

    return (
        <div>
            <h1>录入成绩</h1>
            <Table
                dataSource={grades}
                columns={columns}
                rowKey="id"
                pagination={{
                    pageSize: 10,
                }}
            />
            <Button type="primary" onClick={handleSubmit} loading={submitting} style={{ marginTop: '20px' }}>
                提交成绩
            </Button>
        </div>
    );
};

export default EnterGrades;
