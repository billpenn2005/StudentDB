import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { Form, Input, Button, Spin, message, Typography, Card, Row, Col, Divider } from 'antd';
import axiosInstance from '../axiosInstance';
import { EditOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const StudentProfile = () => {
    const { user, loading } = useContext(AuthContext);
    const [form] = Form.useForm();
    const [submitting, setSubmitting] = useState(false);
    const [studentData, setStudentData] = useState(null);
    const [editMode, setEditMode] = useState(false);

    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                // 获取当前用户及关联的学生信息
                const userRes = await axiosInstance.get('old_students/current/');
                console.log('Fetched student data:', userRes.data);
    
                // 解析 API 响应
                const userData = userRes.data;
                // const studentInfo = userData.student; // 移除此行
    
                // if (!studentInfo) {
                //     throw new Error('未找到对应的学生信息');
                // }
    
                const combinedData = {
                    ...userData,
                    // ...studentInfo // 移除此行
                };
                setStudentData(combinedData);
                
                // 设置表单初始值
                form.setFieldsValue({
                    email: userData.user.email, // 更新路径
                });
            } catch (error) {
                console.error('Failed to fetch profile data:', error);
                message.error('获取个人资料失败');
            }
        
        };
        if (user) {
            fetchInitialData();
        }
    }, [user, form]);

    const onFinish = async (values) => {
        setSubmitting(true);
        try {
            // 更新用户邮箱
            await axiosInstance.patch('user/current/', {
                email: values.email,
            });
            message.success('邮箱更新成功');
            // 更新本地状态
            setStudentData(prevData => ({
                ...prevData,
                email: values.email
            }));
            setEditMode(false);
        } catch (error) {
            console.error('Failed to update email:', error);
            message.error('邮箱更新失败');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading || !studentData) {
        return <Spin tip="加载中..." />;
    }

    return (
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
            <Title level={2} style={{ textAlign: 'center', marginBottom: '40px' }}>学生资料</Title>
            <Card bordered={false} style={{ marginBottom: '20px' }}>
                <Row justify="space-between" align="middle">
                    <Col>
                        <Title level={4}>基本信息</Title>
                    </Col>
                    <Col>
                        <Button
                            type="link"
                            icon={<EditOutlined />}
                            onClick={() => setEditMode(!editMode)}
                        >
                            {editMode ? '取消' : '编辑'}
                        </Button>
                    </Col>
                </Row>
                <Divider />
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={onFinish}
                >
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item label="姓名">
                                <Text strong>{`${studentData.first_name} ${studentData.last_name}`}</Text>
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="邮箱" name="email" rules={[
                                { required: true, message: '请输入邮箱', type: 'email' }
                            ]}>
                                <Input disabled={!editMode} />
                            </Form.Item>
                        </Col>
                    </Row>
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item label="部门">
                                <Text>{studentData.department ? studentData.department.name : 'N/A'}</Text>
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="班级">
                                <Text>{studentData.student_class ? studentData.student_class.name : 'N/A'}</Text>
                            </Form.Item>
                        </Col>
                    </Row>
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item label="年级">
                                <Text>{studentData.grade ? studentData.grade.name : 'N/A'}</Text>
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="年龄">
                                <Text>{studentData.age}</Text>
                            </Form.Item>
                        </Col>
                    </Row>
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item label="性别">
                                <Text>
                                    {studentData.gender === 'M' ? '男' :
                                    studentData.gender === 'F' ? '女' : '其他'}
                                </Text>
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="身份证号码">
                                <Text>{studentData.id_number}</Text>
                            </Form.Item>
                        </Col>
                    </Row>
                    {editMode && (
                        <Form.Item>
                            <Button type="primary" htmlType="submit" loading={submitting}>
                                保存
                            </Button>
                        </Form.Item>
                    )}
                </Form>
            </Card>
            {/* 可以添加更多Card组件展示其他信息 */}
        </div>
    );
};

export default StudentProfile;