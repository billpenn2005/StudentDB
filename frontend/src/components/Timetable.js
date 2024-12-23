import React, { useEffect, useState, useContext } from 'react';
import { Table, Spin, Select, Row, Col } from 'antd';
import { AuthContext } from '../contexts/AuthContext';
import axiosInstance from '../axiosInstance';

const Timetable = () => {
  const { user, currentSemester } = useContext(AuthContext);

  // 所有课程数据（一次性从后端获取）
  const [allCourses, setAllCourses] = useState([]);

  // 当前选中的周次，默认第 1 周
  const [selectedWeek, setSelectedWeek] = useState(1);

  // 前端组装好的课表对象 ( day -> [5节] )
  const [schedule, setSchedule] = useState({});

  // antd Table 数据源
  const [tableData, setTableData] = useState([]);

  const [loading, setLoading] = useState(true);

  /**
   * 组件挂载或 user 变化时，一次性获取课程数据
   */
  useEffect(() => {
    if (user) {
      fetchAllCourses();
    }
    // eslint-disable-next-line
  }, [user]);

  /**
   * 当 allCourses 或 selectedWeek 变化时，重新构建课表并更新 tableData
   */
  useEffect(() => {
    const newSchedule = buildSchedule(allCourses, selectedWeek);
    setSchedule(newSchedule);

    const newTableData = buildTableData(newSchedule);
    setTableData(newTableData);
  }, [allCourses, selectedWeek]);

  /**
   * 根据用户角色从后端获取课程数据
   * 老师 => GET /course-instances/?teacher={teacher_id}
   * 学生 => GET /course-instances/list_selected_courses/
   */
  const fetchAllCourses = async () => {
    try {
      setLoading(true);

      const userGroups = user.groups.map(g => g.trim().toLowerCase());
      let endpoint = '';

      if (userGroups.includes('teacher')) {
        endpoint = `/course-instances/?teacher=${user.teacher_id}&semester=${currentSemester.name}`;
      } else if (userGroups.includes('student')) {
        endpoint = `/course-instances/?student=${user.student_id}&semester=${currentSemester.name}`;
      } else {
        // 其他角色可自行处理
        endpoint = '/course-instances/';
      }

      const response = await axiosInstance.get(endpoint);
      const courses = response.data.results || response.data; // 若无分页可直接用 data

      setAllCourses(courses);
    } catch (error) {
      console.error('Failed to fetch timetable data:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 根据当前 selectedWeek，将课程数据转成 { Monday: [5节], Tuesday: [...], ... }
   */
  const buildSchedule = (courses, week) => {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

    // 初始化
    const scheduleObj = {};
    days.forEach(day => {
      scheduleObj[day] = [null, null, null, null, null];
    });

    // 遍历每门课程，基于它的 schedules 判断是否在本周上课
    courses.forEach(course => {
      if (course.schedules && Array.isArray(course.schedules)) {
        course.schedules.forEach(sch => {
          const { day, period } = sch;

          // 判断本周是否需要上课
          if (isActiveThisWeek(sch, week) && scheduleObj[day]) {
            // period 为 1~5，数组下标从 0 开始
            scheduleObj[day][period - 1] = course;
          }
        });
      }
    });

    return scheduleObj;
  };

  /**
   * 判断某个 schedule 是否在指定周次上课
   * - start_week <= week <= end_week
   * - (week - start_week) % frequency === 0 (如果 frequency > 1)
   * - 不在 exceptions 中
   */
  const isActiveThisWeek = (sch, week) => {
    const {
      start_week = 1,
      end_week = 16,      // 例如默认16周
      frequency = 1,      // 1 表示每周都有课，2 表示隔周一次
      exceptions,         // array
    } = sch;

    // 周次不在开始结束区间内
    if (week < start_week || week > end_week) {
      return false;
    }

    // 按 frequency 判断是否是上课周
    const diff = week - start_week + 1;
    if (frequency > 1 && diff % frequency !== 0) {
      return false;
    }

    // 判断是否在 exceptions(停课或特殊周)
    if (exceptions && Array.isArray(exceptions)) {
      // 如果 exceptions 中包含当前周
      if (exceptions.includes(week)) {
        return false;
      }
    }

    return true;
  };

  /**
   * 将 scheduleObj 转成 antd <Table> 需要的数据结构：
   * [
   *   { key: 1, period: '第1节', monday: ..., tuesday: ..., ... },
   *   ...
   * ]
   */
  const buildTableData = (scheduleObj) => {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const data = [];

    for (let i = 0; i < 5; i++) {
      data.push({
        key: i + 1,
        period: `第${i + 1}节`,
        monday: scheduleObj['Monday'][i],
        tuesday: scheduleObj['Tuesday'][i],
        wednesday: scheduleObj['Wednesday'][i],
        thursday: scheduleObj['Thursday'][i],
        friday: scheduleObj['Friday'][i],
      });
    }
    return data;
  };

  /**
   * 自定义渲染单元格：将课程信息渲染成显示课程名称、地点、老师等
   */
  const renderCourseCell = (courseInstance) => {
    if (!courseInstance) {
      return <span style={{ color: '#999' }}>无</span>;
    }

    return (
      <div style={{ lineHeight: '1.5' }}>
        <div style={{ fontWeight: 'bold' }}>
          {courseInstance.course_prototype?.name || '未命名课程'}
        </div>
        <div>地点：{courseInstance.location || '未知'}</div>
        <div>教师：{courseInstance.teacher?.user?.first_name || '未知'}</div>
      </div>
    );
  };

  // antd Table 的列定义
  const columns = [
    {
      title: '节次/星期',
      dataIndex: 'period',
      key: 'period',
      width: 110,
      align: 'center',
      fixed: 'left',
    },
    {
      title: '周一',
      dataIndex: 'monday',
      key: 'monday',
      align: 'center',
      render: renderCourseCell,
    },
    {
      title: '周二',
      dataIndex: 'tuesday',
      key: 'tuesday',
      align: 'center',
      render: renderCourseCell,
    },
    {
      title: '周三',
      dataIndex: 'wednesday',
      key: 'wednesday',
      align: 'center',
      render: renderCourseCell,
    },
    {
      title: '周四',
      dataIndex: 'thursday',
      key: 'thursday',
      align: 'center',
      render: renderCourseCell,
    },
    {
      title: '周五',
      dataIndex: 'friday',
      key: 'friday',
      align: 'center',
      render: renderCourseCell,
    },
  ];

  // 如果后端返回了 currentSemester.total_weeks，可用于生成周次下拉选项；否则默认为 16
  const totalWeeks = currentSemester?.total_weeks || 16;
  const weekOptions = Array.from({ length: totalWeeks }, (_, i) => ({
    label: `第 ${i + 1} 周`,
    value: i + 1,
  }));

  return (
    <div style={{ background: '#fff', padding: 16 }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <h2 style={{ marginBottom: 0 }}>课表</h2>
        </Col>
        <Col>
          {/* 周次选择器 */}
          <Select
            style={{ width: 140 }}
            options={weekOptions}
            value={selectedWeek}
            onChange={setSelectedWeek}
          />
        </Col>
      </Row>

      {loading ? (
        <div style={{ textAlign: 'center', marginTop: 50 }}>
          <Spin tip="课表加载中..." size="large" />
        </div>
      ) : (
        <Table
          columns={columns}
          dataSource={tableData}
          bordered
          pagination={false}
          scroll={{ x: 'max-content' }}
        />
      )}
    </div>
  );
};

export default Timetable;
