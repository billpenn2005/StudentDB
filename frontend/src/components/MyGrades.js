// src/components/MyGrades.js

import React, { useEffect, useState, useContext } from 'react';
import { Table, Spin, Typography, Tabs, Button, message } from 'antd';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';
import { toast } from 'react-toastify';

const { Title } = Typography;
const { TabPane } = Tabs;

const handleExportMyTranscript = async () => {
  try {
    const res = await axiosInstance.post(
      'generate-report/',
      { type: 'my_transcript' },
      { responseType: 'blob' }
    );
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'my_transcript.pdf');
    document.body.appendChild(link);
    link.click();
    link.remove();
    message.success('导出成功');
  } catch (error) {
    console.error('Export Transcript Error:', error);
    message.error('导出失败');
  }
};

const StudentGradesAndRanking = () => {
  const { user } = useContext(AuthContext);
  const [loading, setLoading] = useState(true);
  const [grades, setGrades] = useState([]);
  const [currentSemester, setCurrentSemester] = useState('');
  const [rankings, setRankings] = useState([]);

  useEffect(() => {
    const fetchGradesAndRankings = async () => {
      setLoading(true);
      try {
        // 调用获取所有成绩的 API
        const res = await axiosInstance.get('s-grades/my_all_grades/');
        const allGrades = res.data.results || res.data;
        setGrades(allGrades);
        console.log('All Grades:', allGrades);

        // 调用获取排名的 API（假设排名也是基于所有成绩）
        const rankRes = await axiosInstance.get('s-grades/my_rankings/');
        const rankData = rankRes.data.results || rankRes.data;
        setRankings(rankData);
        console.log('Rankings:', rankData);

        // 假设 API 返回当前学期信息，或者从成绩中提取
        if (allGrades.length > 0) {
          const semesters = [...new Set(allGrades.map(grade => grade.semester))];
          // 假设最新的 semester 是当前学期
          const sortedSemesters = semesters.sort((a, b) => new Date(b.start_date) - new Date(a.start_date));
          setCurrentSemester(sortedSemesters[0]);
        }
      } catch (error) {
        console.error('Error fetching grades and rankings:', error);
        toast.error('获取成绩和排名失败');
      } finally {
        setLoading(false);
      }
    };
    fetchGradesAndRankings();
  }, []);

  // 过滤当前学期和历史学期的成绩
  const currentSemesterGrades = grades.filter(grade => grade.semester === currentSemester);
  const historicalSemesterGrades = grades.filter(grade => grade.semester !== currentSemester);

  const columns = [
    {
      title: '课程名称 - 学期',
      dataIndex: 'course_instance',
      key: 'course_instance',
      render: (text, record) => (
        <span>{record.course_instance.name} - {record.semester}</span>
      ),
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
    return (
      <div style={{ textAlign: 'center', paddingTop: '50px' }}>
        <Spin tip="加载中..." size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <Title level={2}>我的成绩和排名</Title>
      <Button type="primary" onClick={handleExportMyTranscript} style={{ marginBottom: '20px' }}>
        导出成绩单
      </Button>
      <Tabs defaultActiveKey="1">
        <TabPane tab="本学期成绩" key="1">
          {currentSemesterGrades.length === 0 ? (
            <p>本学期暂无成绩记录。</p>
          ) : (
            <Table
              dataSource={currentSemesterGrades}
              columns={columns}
              rowKey={(record, index) => `${record.course_instance.id}-${index}`}
              pagination={{ pageSize: 10 }}
            />
          )}
        </TabPane>
        <TabPane tab="历史学期成绩" key="2">
          {historicalSemesterGrades.length === 0 ? (
            <p>暂无历史学期的成绩记录。</p>
          ) : (
            <Table
              dataSource={historicalSemesterGrades}
              columns={columns}
              rowKey={(record, index) => `${record.course_instance.id}-${index}`}
              pagination={{ pageSize: 10 }}
            />
          )}
        </TabPane>
      </Tabs>
      {/* 如果需要显示综合排名，可以在这里添加 */}
      <Title level={3} style={{ marginTop: '40px' }}>我的综合排名</Title>
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