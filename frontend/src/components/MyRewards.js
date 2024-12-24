// src/components/MyPunishments.js

import React, { useEffect, useState, useContext } from 'react';
import { Table, Spin } from 'antd';
import { AuthContext } from '../contexts/AuthContext';
import axiosInstance from '../axiosInstance';
import { toast } from 'react-toastify';

const MyPunishments = () => {
    const { user } = useContext(AuthContext);
    const [punishments, setPunishments] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPunishments = async () => {
            try {
                const response = await axiosInstance.get('reward-record/');
                setPunishments(response.data.results);
                //console.log(response.data);
            } catch (error) {
                console.error(error);
                toast.error('获取奖励记录失败');
            } finally {
                setLoading(false);
            }
        };
        fetchPunishments();
    }, []);

    const columns = [
        {
            title: '日期',
            dataIndex: 'date',
            key: 'date',
        },
        {
            title: '类型',
            dataIndex: 'type',
            key: 'type',
            render: (text) => {
                const typeMap = {
                    'EXCELLENCE': '国家奖学金',
                    'OTHER': '其他',
                };
                return typeMap[text] || text;
            },
        },
        {
            title: '描述',
            dataIndex: 'description',
            key: 'description',
        },
    ];

    if (loading) {
        return <Spin tip="加载中..." />;
    }

    return (
        <div>
            <h2>我的奖励记录</h2>
            <Table dataSource={punishments} columns={columns} rowKey="id" />
        </div>
    );
};

export default MyPunishments;
