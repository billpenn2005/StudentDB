import React, { useContext, useEffect, useState } from 'react';
import { Table, Spin, Typography, Button } from 'antd';
import { Link } from 'react-router-dom';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';
import { toast } from 'react-toastify';

const { Title } = Typography;

const TeacherDashboard = () => {
  const { user } = useContext(AuthContext);
  const [loading, setLoading] = useState(true);
  const [courseInstances, setCourseInstances] = useState([]);

  useEffect(() => {
    const fetchCourses = async () => {
      if (!user || !user.teacher_id) {
        setLoading(false);
        return;
      }
      try {
        // 假设后端提供通过teacher字段过滤的API
        const res = await axiosInstance.get(`course-instances/?teacher=${user.teacher_id}`);

        // 如果res.data是一个分页对象（含有results字段）
        const courseData = Array.isArray(res.data.results) ? res.data.results : [];

        // 设置表格数据源为courseData
        setCourseInstances(courseData);
      } catch (error) {
        console.error('Error fetching teacher courses:', error);
        toast.error('获取教师课程信息失败');
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, [user]);

  const columns = [
    {
      title: '课程名称',
      dataIndex: ['course_prototype', 'name'],
      key: 'course_name',
    },
    {
      title: '学期',
      dataIndex: 'semester',
      key: 'semester',
    },
    {
      title: '已选人数',
      dataIndex: ['selected_students'],
      key: 'selected_students_count',
      render: (students) => students ? students.length : 0
    },
    {
      title: '操作',
      key: 'action',
      render: (text, record) => (
        <div style={{ display: 'flex', gap: '8px' }}>
          {/* 成绩管理链接 */}
          <Link to={`/manage-grades/${record.id}`}>
            <Button type="primary">管理成绩</Button>
          </Link>

          {/* 设置成绩占比页面 */}
          <Link to="/set-grade-weights">
            <Button>设置成绩占比</Button>
          </Link>

          {/* 录入成绩页面 */}
          <Link to="/enter-grades">
            <Button>录入成绩</Button>
          </Link>
        </div>
      )
    }
  ];

  if (loading) {
    return (
      <div style={{ marginTop: '100px', textAlign: 'center' }}>
        <Spin tip="加载中..." size="large" />
      </div>
    );
  }

  return (
    <div>
      <Title level={2}>教师仪表盘</Title>
      <p>欢迎，{user && user.first_name}！</p>
      <Title level={4}>我教授的课程</Title>
      {courseInstances.length === 0 ? (
        <p>暂无课程信息</p>
      ) : (
        <Table
          dataSource={courseInstances}
          columns={columns}
          rowKey="id"
          pagination={false}
        />
      )}
    </div>
  );
};

export default TeacherDashboard;
