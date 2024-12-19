import React, { useEffect, useState, useContext } from 'react';
import { Table, Spin, Typography } from 'antd';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';
import { toast } from 'react-toastify';

const { Title } = Typography;

const StudentGradesAndRanking = () => {
  const { user } = useContext(AuthContext);
  const [loading, setLoading] = useState(true);
  const [rankings, setRankings] = useState([]);

  useEffect(() => {
    const fetchRankings = async () => {
      try {
        // 调用 my_rankings API
        const res = await axiosInstance.get('s-grades/my_rankings/');
        const rank = res.data.results || res.data;
        setRankings(rank);
        console.log('Rankings:', rank);
      } catch (error) {
        console.error('Error fetching rankings:', error);
        toast.error('获取成绩和排名失败');
      } finally {
        setLoading(false);
      }
    };
    fetchRankings();
  }, []);

  const columns = [
    {
      title: '课程名称 - 学期',
      dataIndex: 'course_instance',
      key: 'course_instance',
      render: (text) => text || 'N/A',
    },
    {
      title: '平时分',
      dataIndex: 'daily_score',
      key: 'daily_score',
      render: (score) => score !== null ? score : '未发布',
    },
    {
      title: '期末分',
      dataIndex: 'final_score',
      key: 'final_score',
      render: (score) => score !== null ? score : '未发布',
    },
    {
      title: '总分',
      dataIndex: 'total_score',
      key: 'total_score',
      render: (score) => score !== null ? score : '未发布',
    },
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      render: (rank) => rank !== null ? rank : '未发布',
    }
  ];

  if (loading) {
    return <Spin tip="加载中..." style={{ display: 'block', margin: '100px auto' }} />;
  }

  return (
    <div>
      <Title level={2}>我的成绩和排名</Title>
      <Table
        dataSource={rankings}
        columns={columns}
        rowKey={(record, index) => `${record.course_instance}-${index}`}
        pagination={false}
      />
    </div>
  );
};

export default StudentGradesAndRanking;