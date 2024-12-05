// src/pages/StudentInfo.js
import React, { useState, useEffect } from 'react';
import { Card, Descriptions, Button } from 'antd';

const StudentInfo = ({ studentId }) => {
  const [studentInfo, setStudentInfo] = useState(null);

  useEffect(() => {
    // 模拟从后端 API 获取学生信息
    const fetchStudentInfo = async () => {
      const data = await fetch(`/api/student/${studentId}`).then((res) => res.json());
      setStudentInfo(data);
    };

    fetchStudentInfo();
  }, [studentId]);

  return (
    <div>
      <h2>学生信息页面</h2>
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
    </div>
  );
};

export default StudentInfo;
