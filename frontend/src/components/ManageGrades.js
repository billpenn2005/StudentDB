import React, { useEffect, useState, useContext } from 'react';
import { useParams } from 'react-router-dom';
import { Spin, Form, InputNumber, Button, Table, Typography } from 'antd';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';
import { toast } from 'react-toastify';

const { Title } = Typography;

const ManageGrades = () => {
    const { courseInstanceId } = useParams();
    const { user } = useContext(AuthContext);

    const [loading, setLoading] = useState(true);
    const [courseInstance, setCourseInstance] = useState(null);
    const [enrolledStudents, setEnrolledStudents] = useState([]);
    const [weightsForm] = Form.useForm();
    const [gradesData, setGradesData] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // 获取课程实例详情
                const courseRes = await axiosInstance.get(`course-instances/${courseInstanceId}/`);
                setCourseInstance(courseRes.data);

                // 获取已选学生列表
                const studentsRes = await axiosInstance.get(`course-instances/${courseInstanceId}/view_enrolled_students/`);
                const students = studentsRes.data || [];

                // 获取已有成绩数据
                const gradesRes = await axiosInstance.get(`s-grades/?course_instance=${courseInstanceId}`);
                const existingGrades = gradesRes.data.results || [];

                // 获取权重
                const dailyWeight = courseRes.data.daily_weight;
                const finalWeight = courseRes.data.final_weight;

                // 将学生列表与成绩数据关联，并计算加权总分
                const mergedData = students.map(stu => {
                    const gradeItem = existingGrades.find(g => g.student === stu.username);
                    const daily_score = gradeItem ? parseFloat(gradeItem.daily_score) : 0.00;
                    const final_score = gradeItem ? parseFloat(gradeItem.final_score) : 0.00;
                    const weightedTotal = (daily_score * (dailyWeight / 100)) + (final_score * (finalWeight / 100));
                    return {
                        student_id: stu.id,
                        username: stu.username,
                        first_name: stu.first_name,
                        last_name: stu.last_name,
                        daily_score,
                        final_score,
                        total_score: weightedTotal,
                    };
                });

                setEnrolledStudents(students);
                setGradesData(mergedData);

                // 设置表单初始值
                weightsForm.setFieldsValue({
                    daily_weight: dailyWeight,
                    final_weight: finalWeight,
                });
            } catch (error) {
                console.error('Error fetching course or student data:', error);
                toast.error('获取课程或学生信息失败');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [courseInstanceId, weightsForm]);

    const handleSetWeights = async (values) => {
        const { daily_weight, final_weight } = values;
        if (daily_weight + final_weight !== 100) {
            toast.error('平时分和期末分占比总和必须为100%');
            return;
        }

        try {
            await axiosInstance.patch(`course-instances/${courseInstanceId}/set_grade_weights/`, {
                daily_weight,
                final_weight
            });
            toast.success('成绩占比设置成功');
            
            // 更新本地状态中的权重
            setCourseInstance(prev => ({
                ...prev,
                daily_weight,
                final_weight
            }));

            // 重新计算所有学生的 total_score
            const updatedGradesData = gradesData.map(g => ({
                ...g,
                total_score: (g.daily_score * (daily_weight / 100)) + (g.final_score * (final_weight / 100))
            }));
            setGradesData(updatedGradesData);

            // 如果不想刷新页面，可以移除以下行
            // window.location.reload();
        } catch (error) {
            console.error('Error setting grade weights:', error);
            toast.error('设置成绩占比失败');
        }
    };

    const handleGradesChange = (record, field, value) => {
        const daily_weight = courseInstance.daily_weight;
        const final_weight = courseInstance.final_weight;

        const newData = gradesData.map(item => {
            if (item.student_id === record.student_id) {
                const daily_score = field === 'daily_score' ? value : item.daily_score;
                const final_score = field === 'final_score' ? value : item.final_score;
                const weightedTotal = (parseFloat(daily_score) * (daily_weight / 100)) + (parseFloat(final_score) * (final_weight / 100));
                return {
                    ...item,
                    [field]: value,
                    total_score: weightedTotal
                };
            }
            return item;
        });
        setGradesData(newData);
    };

    const handlePublishGrades = async () => {
        try {
            await axiosInstance.post(`course-instances/${courseInstanceId}/publish_grades/`);
            toast.success('成绩发布成功');
        } catch (error) {
            console.error('Error publishing grades:', error);
            toast.error(error.response?.data?.detail || '成绩发布失败');
        }
    };

    const handlewithdrawGrades = async () => {
        try {
            await axiosInstance.post(`course-instances/${courseInstanceId}/withdraw_grades/`);
            toast.success('成绩撤回成功');
        } catch (error) {
            console.error('Error withdrawing grades:', error);
            toast.error(error.response?.data?.detail || '成绩撤回失败');
        }
    };

    const handleSubmitGrades = async () => {
        // 构建批量更新的数据结构
        // 每条数据需要 student_id, daily_score, final_score
        const payload = gradesData.map(g => ({
            student_id: g.student_id,
            daily_score: g.daily_score,
            final_score: g.final_score
        }));

        try {
            await axiosInstance.post(`s-grades/bulk_update_grades/?course_instance_id=${courseInstanceId}`, payload);
            toast.success('成绩更新成功');
        } catch (error) {
            console.error('Error updating grades:', error);
            toast.error(error.response?.data?.detail || '成绩更新失败');
        }
    };

    const columns = [
        {
            title: '学生姓名',
            dataIndex: 'first_name',
            key: 'first_name',
            render: (text, record) => `${record.last_name}${record.first_name}`
        },
        {
            title: '用户名',
            dataIndex: 'username',
            key: 'username',
        },
        {
            title: '平时分',
            dataIndex: 'daily_score',
            key: 'daily_score',
            render: (text, record) => (
                <InputNumber
                    min={0} max={100}
                    value={record.daily_score}
                    onChange={(value) => handleGradesChange(record, 'daily_score', value)}
                />
            )
        },
        {
            title: '期末分',
            dataIndex: 'final_score',
            key: 'final_score',
            render: (text, record) => (
                <InputNumber
                    min={0} max={100}
                    value={record.final_score}
                    onChange={(value) => handleGradesChange(record, 'final_score', value)}
                />
            )
        },
        {
            title: '总分',
            dataIndex: 'total_score',
            key: 'total_score',
            render: (text, record) => record.total_score.toFixed(2)
        }
    ];

    if (loading) {
        return <Spin tip="加载中..." style={{ display: 'block', margin: '100px auto' }} />;
    }

    if (!courseInstance) {
        return <div>未找到该课程实例信息</div>;
    }

    return (
        <div>
            <Title level={2}>管理成绩 - {courseInstance.course_prototype.name} ({courseInstance.semester})</Title>

            <Title level={4}>设置成绩占比</Title>
            <Form
                form={weightsForm}
                layout="inline"
                onFinish={handleSetWeights}
            >
                <Form.Item
                    label="平时分占比"
                    name="daily_weight"
                    rules={[{ required: true, message: '请输入平时分占比' }]}
                >
                    <InputNumber min={0} max={100} />
                </Form.Item>
                <Form.Item
                    label="期末分占比"
                    name="final_weight"
                    rules={[{ required: true, message: '请输入期末分占比' }]}
                >
                    <InputNumber min={0} max={100} />
                </Form.Item>
                <Form.Item>
                    <Button type="primary" htmlType="submit">保存</Button>
                </Form.Item>
            </Form>

            <Title level={4} style={{ marginTop: '40px' }}>录入学生成绩</Title>
            <Table
                dataSource={gradesData}
                columns={columns}
                rowKey="student_id"
                pagination={false}
            />
            <div style={{ marginTop: '20px' }}>
                <Button type="primary" onClick={handleSubmitGrades}>提交成绩更新</Button>
                <span style={{ margin: '0 8px' }} />
                <Button type="primary" onClick={handlePublishGrades}>发布成绩</Button>
                <span style={{ margin: '0 8px' }} />
                <Button type="primary" onClick={handlewithdrawGrades}>撤回成绩</Button>
                <span style={{ margin: '0 8px' }} />
                <Button>导出成绩</Button>
            </div>
        </div>
    );
};

export default ManageGrades;
