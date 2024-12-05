import React, { useState, useEffect } from 'react';
import { Table, Button, Tabs } from 'antd';

const CourseSelection = () => {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
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
    <Tabs defaultActiveKey="1">
      <Tabs.TabPane tab="选课页面" key="1">
        <Table columns={columns} dataSource={courses} />
      </Tabs.TabPane>
    </Tabs>
  );
};

export default CourseSelection;