// src/pages/CourseSelection.js
import React, { useState, useEffect } from 'react';
import { Table, Button } from 'antd';

const CourseSelection = () => {
  const [courses, setCourses] = useState([]);
  
  useEffect(() => {
    // 这里模拟获取课程数据，可以从后端 API 获取
    const fetchCourses = async () => {
      const data = [
        { key: '1', courseName: '数学', courseCode: 'MATH101', instructor: '张老师' },
        { key: '2', courseName: '英语', courseCode: 'ENG102', instructor: '李老师' },
        { key: '3', courseName: '计算机科学', courseCode: 'CS103', instructor: '王老师' },
      ];
      setCourses(data);
    };

    fetchCourses();
  }, []);

  const handleCourseSelect = (course) => {
    // 处理选课逻辑，通常是调用 API 向服务器提交选课请求
    alert(`已选择课程: ${course.courseName}`);
  };

  const columns = [
    { title: '课程名称', dataIndex: 'courseName' },
    { title: '课程代码', dataIndex: 'courseCode' },
    { title: '授课教师', dataIndex: 'instructor' },
    {
      title: '操作',
      render: (_, record) => (
        <Button type="primary" onClick={() => handleCourseSelect(record)}>
          选课
        </Button>
      ),
    },
  ];

  return (
    <div>
      <h2>选课页面</h2>
      <Table columns={columns} dataSource={courses} />
    </div>
  );
};

export default CourseSelection;
