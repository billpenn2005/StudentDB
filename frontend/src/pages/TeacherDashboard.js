// src/pages/TeacherDashboard.js
import React from 'react';
import { Card, List, Button } from 'antd';

const TeacherDashboard = () => {
  const students = [
    { key: '1', name: '张三', id: '2021001', grade: '90' },
    { key: '2', name: '李四', id: '2021002', grade: '85' },
    { key: '3', name: '王五', id: '2021003', grade: '88' },
  ];

  const handleViewGrades = (student) => {
    // 查看成绩的逻辑
    alert(`查看成绩: ${student.name}`);
  };

  return (
    <div>
      <h2>老师页面</h2>
      <Card title="学生信息管理">
        <List
          itemLayout="horizontal"
          dataSource={students}
          renderItem={(student) => (
            <List.Item
              actions={[
                <Button type="primary" onClick={() => handleViewGrades(student)}>
                  查看成绩
                </Button>,
              ]}
            >
              <List.Item.Meta
                title={student.name}
                description={`学号: ${student.id}, 成绩: ${student.grade}`}
              />
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default TeacherDashboard;
