// src/components/MyRankings.js

import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { Table, Spin, message } from 'antd';
import axiosInstance from '../axiosInstance';

const MyRankings = () => {
    const { user } = useContext(AuthContext);
    const [rankings, setRankings] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchRankings = async () => {
        try {
            const response = await axiosInstance.get('/s-grades/my_rankings/');
            setRankings(response.data);
        } catch (error) {
            console.error('Failed to fetch rankings:', error);
            message.error('获取排名失败');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRankings();
    }, []);

    const columns = [
        {
            title: '课程名称',
            dataIndex: 'course_instance',
            key: 'course_instance',
        },
        {
            title: '总分',
            dataIndex: 'total_score',
            key: 'total_score',
        },
        {
            title: '排名',
            dataIndex: 'rank',
            key: 'rank',
        },
    ];

    if (loading) {
        return <Spin tip="加载中..." />;
    }

    return (
        <div>
            <h1>我的排名</h1>
            <Table
                dataSource={rankings}
                columns={columns}
                rowKey="course_instance"
                pagination={false}
            />
        </div>
    );
};

export default MyRankings;
