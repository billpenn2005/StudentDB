import React, { useState, useEffect } from 'react';
import { Card, Descriptions, Button } from 'antd';
import axios from 'axios';
const StudentInfo = ({ username }) => {
  const [studentInfo, setStudentInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem('access_token');
  axios.defaults.headers['Authorization'] = `Bearer ${token}`;
  useEffect(() => {
    const fetchStudentInfo = async () => {
      try {
        username=localStorage.getItem('username');
        const response = await axios.get(`http://127.0.0.1:8000/api/students/${username}`);
        const data = response.data;
        console.log('Student data:', data);  // Debugging line
        setStudentInfo(data);
      } catch (error) {
        console.error('Error fetching student info:', error);
      } finally {
        setLoading(false);  // Ensure loading state is turned off after fetching
      }
    };

    fetchStudentInfo();
  }, [username]);

  if (loading) {
    return <p>加载中...</p>;
  }

  return (
    <Tabs defaultActiveKey="1">
      <Tabs.TabPane tab="学生信息页面" key="1">
        {studentInfo ? (
          <Card>
            <Descriptions title="学生信息" bordered>
              <Descriptions.Item label="姓名">{studentInfo.name}</Descriptions.Item>
              <Descriptions.Item label="学号">{studentInfo.id}</Descriptions.Item>
              <Descriptions.Item label="年龄">{studentInfo.age}</Descriptions.Item>
              <Descriptions.Item label="性别">{studentInfo.gender}</Descriptions.Item>
              <Descriptions.Item label="系别">{studentInfo.department}</Descriptions.Item>
              <Descriptions.Item label="专业">{studentInfo.major}</Descriptions.Item>
            </Descriptions>
            <Button type="primary">编辑信息</Button>
          </Card>
        ) : (
          <p>加载中...</p>
        )}
      </Tabs.TabPane>
    </Tabs>
  );
};

export default StudentInfo;