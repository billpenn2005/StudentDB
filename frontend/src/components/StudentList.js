// src/components/StudentList.js

import React, { useEffect, useState, useContext } from 'react';
import { Table, Typography, Spin, Alert } from 'antd';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';
import { toast } from 'react-toastify';

const { Title } = Typography;

const StudentList = () => {
    const { isAuthenticated } = useContext(AuthContext);
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchStudents = async () => {
        try {
            const response = await axiosInstance.get('students/');
            setStudents(response.data.results); // 根据分页结构调整
            setLoading(false);
        } catch (err) {
            console.error(err);
            setError('无法获取学生列表');
            setLoading(false);
            toast.error('无法获取学生列表');
        }
    };

    useEffect(() => {
        if (isAuthenticated) {
            fetchStudents();
        }
    }, [isAuthenticated]);

    const columns = [
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
            sorter: (a, b) => a.id - b.id,
        },
        {
            title: '姓名',
            key: 'name',
            render: (text, record) => `${record.user.first_name} ${record.user.last_name}`,
            sorter: (a, b) => a.user.first_name.localeCompare(b.user.first_name),
        },
        {
            title: '单位',
            dataIndex: ['department', 'name'],
            key: 'department',
            render: (text) => text || 'N/A',
            sorter: (a, b) => (a.department?.name || '').localeCompare(b.department?.name || ''),
        },
        {
            title: '年龄',
            dataIndex: 'age',
            key: 'age',
            sorter: (a, b) => a.age - b.age,
        },
        {
            title: '性别',
            dataIndex: 'gender',
            key: 'gender',
            render: (gender) => gender === 'M' ? '男' : '女',
            filters: [
                { text: '男', value: 'M' },
                { text: '女', value: 'F' },
            ],
            onFilter: (value, record) => record.gender === value,
        },
        {
            title: '身份证号码',
            dataIndex: 'id_number',
            key: 'id_number',
        },
    ];

    if (loading) return <div style={styles.loading}><Spin tip="加载中..." size="large" /></div>;
    if (error) return <Alert message={error} type="error" showIcon />;

    return (
        <div>
            <Title level={2}>学生列表</Title>
            <Table 
                dataSource={students} 
                columns={columns} 
                rowKey="id" 
                pagination={{ pageSize: 10 }} 
                bordered
            />
        </div>
    );
};

const styles = {
    loading: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
    },
};

export default StudentList;
