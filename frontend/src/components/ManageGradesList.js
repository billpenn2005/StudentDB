// src/components/ManageGradesList.js

import React, { useEffect, useState, useContext } from 'react';
import { Table, Button, Spin, Alert } from 'antd';
import { Link } from 'react-router-dom';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';

const ManageGradesList = () => {
    const { user } = useContext(AuthContext);
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchCourses = async () => {
        try {
            const response = await axiosInstance.get('/course-instances/', {
                params: {
                    teacher: user.teacher_id
                }
            });
            console.log('Courses:', response.data);
            setCourses(response.data);
        } catch (err) {
            setError('无法获取课程列表。');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCourses();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const columns = [
        {
            title: '课程名称',
            dataIndex: ['course_prototype', 'name'],
            key: 'name',
        },
        {
            title: '学期',
            dataIndex: 'semester',
            key: 'semester',
        },
        {
            title: '位置',
            dataIndex: 'location',
            key: 'location',
        },
        {
            title: '容量',
            dataIndex: 'capacity',
            key: 'capacity',
        },
        {
            title: '操作',
            key: 'action',
            render: (text, record) => (
                <Link to={`/manage-grades/${record.id}`}>
                    <Button type="primary">管理成绩</Button>
                </Link>
            ),
        },
    ];

    if (loading) {
        return <Spin tip="加载课程列表..." />;
    }

    if (error) {
        return <Alert message="错误" description={error} type="error" showIcon />;
    }

    return (
        <div>
            <h2>管理成绩</h2>
            <Table
                dataSource={courses}
                columns={columns}
                rowKey="id"
                pagination={{ pageSize: 10 }}
            />
        </div>
    );
};

export default ManageGradesList;
