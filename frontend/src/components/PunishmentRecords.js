import React, { useEffect, useState, useContext } from 'react';
import { Table, Button, Modal, Form, Input, Select, DatePicker, message, Typography, Radio } from 'antd';
import axiosInstance from '../axiosInstance';
import { AuthContext } from '../contexts/AuthContext';

const { Option } = Select;
const { Title } = Typography;

const PunishmentRecords = () => {
    const { user } = useContext(AuthContext);
    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [form] = Form.useForm();
    const [submitting, setSubmitting] = useState(false);
    const [students, setStudents] = useState([]);

    useEffect(() => {
        const fetchStudents = async () => {
            try { 
                // 若后端已经做了限制，只返回教师部门的学生
                const res = await axiosInstance.get('students/'); 
                console.log('Students:', res.data.results);
                if (Array.isArray(res.data.results)) {
                    setStudents(res.data.results); // 看后端接口返回的结构决定
                } else {
                    console.error('Unexpected data format:', res.data.results);
                    message.error('获取学生列表失败');
                }
            } catch(err) {
                console.error(err);
                message.error('获取学生列表失败');
            }
        };
        fetchStudents();
    }, []);

    const fetchRecords = async () => {
        setLoading(true);
        try {
            const response = await axiosInstance.get('punishment-record/');
            if (Array.isArray(response.data.results)) {
                setRecords(response.data.results);
            } else if(response.results){
                setRecords(response.results);
            } 
            else {
                console.error('Unexpected data format:', response.data.results);
                message.error('获取奖惩记录失败');
            }
        } catch (error) {
            console.error('Fetch Punishments Error:', error);
            message.error('获取奖惩记录失败');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRecords();
    }, []);

    const showModal = () => {
        setIsModalVisible(true);
    };

    const handleCancel = () => {
        setIsModalVisible(false);
        form.resetFields();
    };

    const onFinish = async (values) => {
        setSubmitting(true);
        try {
            await axiosInstance.post('punishment-record/', {
                student: values.student_id,
                type: values.type,
                description: values.description,
            });
            message.success('添加奖惩记录成功');
            fetchRecords();
            handleCancel();
        } catch (error) {
            console.error('Add Punishment Error:', error);
            message.error('添加奖惩记录失败');
        } finally {
            setSubmitting(false);
        }
    };

    const columns = [
        {
            title: '学生姓名',
            dataIndex: ['student', 'user', 'first_name'],
            key: 'student_name',
            render: (text, record) => {
                const { student } = record;
                if (student && student.user) {
                    return `${student.user.first_name} ${student.user.last_name}`;
                }
                return '';
            },
        },
        {
            title: '类型',
            dataIndex: 'type',
            key: 'type',
            render: (text) => {
                const types = {
                    'DISCIPLINE': '纪律处分',
                    'ACADEMIC': '学术处分',
                    'OTHER': '其他',
                };
                return types[text] || text;
            }
        },
        {
            title: '日期',
            dataIndex: 'date',
            key: 'date',
        },
        {
            title: '描述',
            dataIndex: 'description',
            key: 'description',
        },
    ];

    // 新增生成报表的功能
    const [isReportModalVisible, setIsReportModalVisible] = useState(false);
    const [reportForm] = Form.useForm();
    const [generating, setGenerating] = useState(false);

    const showReportModal = () => {
        setIsReportModalVisible(true);
    };

    const handleReportCancel = () => {
        setIsReportModalVisible(false);
        reportForm.resetFields();
    };

    const onGenerateReport = async (values) => {
        setGenerating(true);
        try {
            let payload = { type: values.reportType };
            if (values.reportType === 'teacher_course') {
                payload.course_id = values.course_id;
            }
            const response = await axiosInstance.post('generate-report/', payload, {
                responseType: 'blob', // 重要
            });
            // 创建下载链接
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            // 从响应头中获取文件名
            const disposition = response.headers['content-disposition'];
            let filename = 'report.pdf';
            if (disposition && disposition.indexOf('attachment') !== -1) {
                const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                const matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) { 
                    filename = matches[1].replace(/['"]/g, '');
                }
            }
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            message.success('报表生成成功');
            handleReportCancel();
        } catch (error) {
            console.error('Generate Report Error:', error);
            message.error('生成报表失败');
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <Title level={3}>奖惩记录管理</Title>
            <Button type="primary" onClick={showModal} style={{ marginBottom: '20px', marginRight: '10px' }}>
                添加奖惩记录
            </Button>
            <Button type="default" onClick={showReportModal} style={{ marginBottom: '20px' }}>
                生成报表
            </Button>
            <Table
                dataSource={records}
                columns={columns}
                rowKey="id"
                loading={loading}
            />
            <Modal
                title="添加奖惩记录"
                visible={isModalVisible}
                onCancel={handleCancel}
                footer={null}
            >
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={onFinish}
                >
                    <Form.Item
                    label="学生"
                    name="student_id"
                    rules={[{ required: true, message: '请选择学生' }]}
                    >
                    <Select placeholder="选择学生">
                        {students.map(stu => (
                        <Option key={stu.id} value={stu.id}>
                            {stu.user.first_name + stu.user.last_name}
                        </Option>
                        ))}
                    </Select>
                    </Form.Item>
                    <Form.Item
                        label="类型"
                        name="type"
                        rules={[{ required: true, message: '请选择类型' }]}
                    >
                        <Select placeholder="选择类型">
                            <Option value="DISCIPLINE">纪律处分</Option>
                            <Option value="ACADEMIC">学术处分</Option>
                            <Option value="OTHER">其他</Option>
                        </Select>
                    </Form.Item>
                    <Form.Item
                        label="描述"
                        name="description"
                        rules={[{ required: true, message: '请输入描述' }]}
                    >
                        <Input.TextArea rows={4} />
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit" loading={submitting}>
                            提交
                        </Button>
                    </Form.Item>
                </Form>
            </Modal>
            {/* 报表生成模态框 */}
            <Modal
                title="生成报表"
                visible={isReportModalVisible}
                onCancel={handleReportCancel}
                footer={null}
            >
                <Form
                    form={reportForm}
                    layout="vertical"
                    onFinish={onGenerateReport}
                >
                    <Form.Item
                        label="报表类型"
                        name="reportType"
                        rules={[{ required: true, message: '请选择报表类型' }]}
                    >
                        <Radio.Group>
                            <Radio value="my_transcript">个人成绩单</Radio>
                            <Radio value="teacher_course">教师课程报表</Radio>
                            <Radio value="students">学生信息报表</Radio>
                            <Radio value="grades">成绩报表</Radio>
                            <Radio value="courses">课程报表</Radio>
                        </Radio.Group>
                    </Form.Item>
                    {/* 如果选择教师课程报表，需要选择课程 */}
                    <Form.Item noStyle shouldUpdate={(prevValues, currentValues) => prevValues.reportType !== currentValues.reportType}>
                        {({ getFieldValue }) => {
                            return getFieldValue('reportType') === 'teacher_course' ? (
                                <Form.Item
                                    label="课程"
                                    name="course_id"
                                    rules={[{ required: true, message: '请选择课程' }]}
                                >
                                    <Select placeholder="选择课程">
                                        {/* 假设有一个获取教师课程的API */}
                                        { /* 需要根据实际情况调整 */}
                                        {/* 这里可以添加一个useEffect来获取教师的课程列表 */}
                                        {/* 示例： */}
                                        {/* {teacherCourses.map(course => (
                                            <Option key={course.id} value={course.id}>
                                                {course.name}
                                            </Option>
                                        ))} */}
                                    </Select>
                                </Form.Item>
                            ) : null;
                        }}
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit" loading={generating}>
                            生成
                        </Button>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default PunishmentRecords;