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
        // 1. 获取所有成绩
        const res = await axiosInstance.get('s-grades/my_all_grades/');
        // 注意：如果后端没做分页，res.data 可能就是数组；如果做了分页，可能是 {results: [...]}
        const allGrades = res.data.results || res.data;
        setGrades(allGrades);

        // 2. 获取排名
        const rankRes = await axiosInstance.get('s-grades/my_rankings/');
        const rankData = rankRes.data.results || rankRes.data;
        setRankings(rankData);

        // 3. 设定当前学期
        if (allGrades.length > 0) {
          // 你需要从后端得到更准确的学期信息，这里只是示范
          const semesters = [...new Set(allGrades.map(g => g.semester))];
          setCurrentSemester(semesters[0]); 
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
  const currentSemesterGrades = grades.filter(g => g.semester === currentSemester);
  const historicalSemesterGrades = grades.filter(g => g.semester !== currentSemester);

  // 在这里新增一列“考试轮次”
  const columns = [
    {
      title: '课程名称 - 学期',
      dataIndex: 'course_instance',
      key: 'course_instance',
      render: (text, record) => (
        // record.course_instance 可能是字符串或对象，视后端返回而定
        <span>
          {typeof record.course_instance === 'object' 
            ? record.course_instance.name 
            : record.course_instance}
          {' - '}
          {record.semester}
        </span>
      ),
    },
    {
      title: '考试轮次',
      dataIndex: 'attempt',
      key: 'attempt',
      render: (val) => {
        switch (val) {
          case 1: return '首考';
          case 2: return '补考';
          case 3: return '重修';
          default: return `其他(${val})`;
        }
      },
    },
    {
      title: '平时分',
      dataIndex: 'daily_score',
      key: 'daily_score',
      render: (score) => (score !== null ? score : '未发布'),
    },
    {
      title: '期末分',
      dataIndex: 'final_score',
      key: 'final_score',
      render: (score) => (score !== null ? score : '未发布'),
    },
    {
      title: '总分',
      dataIndex: 'total_score',
      key: 'total_score',
      render: (score) => (score !== null ? score : '未发布'),
    },
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      render: (rank) => (rank !== null ? rank : '未发布'),
    },
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
      <Button 
        type="primary" 
        onClick={handleExportMyTranscript} 
        style={{ marginBottom: '20px' }}
      >
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
              rowKey={(record, index) => `${record.id}-${index}`} 
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
              rowKey={(record, index) => `${record.id}-${index}`}
              pagination={{ pageSize: 10 }}
            />
          )}
        </TabPane>
      </Tabs>

      <Title level={3} style={{ marginTop: '40px' }}>我的综合排名</Title>
      <Table
        dataSource={rankings}
        columns={columns}
        rowKey={(record, index) => `${record.id}-${index}`}
        pagination={false}
      />
    </div>
  );
};

export default StudentGradesAndRanking;
