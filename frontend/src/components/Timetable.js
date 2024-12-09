// src/components/Timetable.js

import React, { useEffect, useState, useContext } from 'react';
import { Table, Spin, message } from 'antd';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';

const Timetable = () => {
    const { user, loading: authLoading } = useContext(AuthContext);
    const [selectedCourses, setSelectedCourses] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user) {
            fetchSelectedCourses();
        }
    }, [user]);

    const fetchSelectedCourses = async () => {
        setLoading(true);
        try {
            const response = await axiosInstance.get('selected-courses/');
            setSelectedCourses(response.data);
        } catch (error) {
            console.error(error);
            message.error('获取已选课程失败');
        } finally {
            setLoading(false);
        }
    };

    const columns = [
        {
            title: '课程名称',
            dataIndex: ['class_instance', 'course', 'name'],
            key: 'course_name',
        },
        {
            title: '班级',
            dataIndex: ['class_instance', 'group'],
            key: 'group',
        },
        {
            title: '教师',
            dataIndex: ['class_instance', 'teacher'],
            key: 'teacher',
        },
        {
            title: '时间',
            dataIndex: ['class_instance', 'time_slot', 'period'],
            key: 'time',
            render: (period) => `第${period}节`,
        },
        {
            title: '选课时间',
            dataIndex: ['selected_at'],
            key: 'selected_at',
            render: (date) => new Date(date).toLocaleString(),
        },
    ];

    if (authLoading || loading) {
        return (
            <div style={{ textAlign: 'center', paddingTop: '50px' }}>
                <Spin tip="加载中..." size="large" />
            </div>
        );
    }

    return (
        <div>
            <h2>我的课表</h2>
            <Table
                dataSource={selectedCourses}
                columns={columns}
                rowKey="id"
                pagination={false}
            />
        </div>
    );
};

export default Timetable;
