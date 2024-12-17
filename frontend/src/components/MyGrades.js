// src/components/MyGrades.js

import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { Table, Spin, message } from 'antd';
import axiosInstance from '../axiosInstance';

const MyGrades = () => {
    const { user } = useContext(AuthContext);
    const [grades, setGrades] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchGrades = async () => {
        try {
            const response = await axiosInstance.get('/s-grades/');
            // 根据后端是否启用分页选择正确的数据
            const data = response.data.results || response.data;
            console.log('Grades API Response:', data); // 调试日志

            if (!Array.isArray(data)) {
                throw new TypeError('Expected grades data to be an array');
            }
            setGrades(data);
        } catch (error) {
            console.error('Failed to fetch grades:', error);
            message.error('获取成绩失败');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchGrades();
    }, []);

    const columns = [
        {
            title: '课程名称',
            dataIndex: 'course_instance',
            key: 'course_name',
        },
        {
            title: '学期',
            dataIndex: 'course_instance',
            key: 'semester',
        },
        
        {
            title: '平时分',
            dataIndex: 'daily_score',
            key: 'daily_score',
        },
        {
            title: '期末分',
            dataIndex: 'final_score',
            key: 'final_score',
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
            <h1>我的成绩</h1>
            <Table
                dataSource={grades}
                columns={columns}
                rowKey="id"
                pagination={{
                    pageSize: 10,
                }}
            />
        </div>
    );
};

export default MyGrades;
