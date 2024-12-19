import React, { useEffect, useState, useContext } from 'react';
import { Form, InputNumber, Button, Card, Spin } from 'antd';
import axiosInstance from '../axiosInstance';
import { toast } from 'react-toastify';
import { AuthContext } from '../contexts/AuthContext';

const SetGradeWeights = ({ courseInstanceId }) => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const { fetchUser } = useContext(AuthContext);

    useEffect(() => {
        const fetchWeights = async () => {
            try {
                const response = await axiosInstance.get(`course-instances/${courseInstanceId}/`);
                form.setFieldsValue({
                    daily_weight: response.data.daily_weight,
                    final_weight: response.data.final_weight,
                });
            } catch (error) {
                console.error('Failed to fetch grade weights:', error);
                toast.error('获取成绩占比失败');
            } finally {
                setLoading(false);
            }
        };

        fetchWeights();
    }, [courseInstanceId, form]);

    const onFinish = async (values) => {
        setSubmitting(true);
        try {
            await axiosInstance.patch(`course-instances/${courseInstanceId}/set_grade_weights/`, values);
            toast.success('成绩占比设置成功');
            await fetchUser(); // 更新用户信息（如果需要）
        } catch (error) {
            console.error('Failed to set grade weights:', error);
            const message = error.response?.data?.detail || '设置成绩占比失败';
            toast.error(message);
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return <Spin tip="加载中..." />;
    }

    return (
        <Card title="设置成绩占比" style={{ marginBottom: '20px' }}>
            <Form
                form={form}
                layout="vertical"
                onFinish={onFinish}
                initialValues={{
                    daily_weight: 50,
                    final_weight: 50,
                }}
            >
                <Form.Item
                    label="平时分占比 (%)"
                    name="daily_weight"
                    rules={[
                        { required: true, message: '请输入平时分占比' },
                        { type: 'number', min: 0, max: 100, message: '必须在0到100之间' },
                    ]}
                >
                    <InputNumber min={0} max={100} />
                </Form.Item>
                <Form.Item
                    label="期末分占比 (%)"
                    name="final_weight"
                    rules={[
                        { required: true, message: '请输入期末分占比' },
                        { type: 'number', min: 0, max: 100, message: '必须在0到100之间' },
                        ({ getFieldValue }) => ({
                            validator(_, value) {
                                const daily = getFieldValue('daily_weight') || 0;
                                if (daily + value === 100) {
                                    return Promise.resolve();
                                }
                                return Promise.reject(new Error('平时分和期末分的总和必须为100%'));
                            },
                        }),
                    ]}
                >
                    <InputNumber min={0} max={100} />
                </Form.Item>
                <Form.Item>
                    <Button type="primary" htmlType="submit" loading={submitting}>
                        设置占比
                    </Button>
                </Form.Item>
            </Form>
        </Card>
    );
};

export default SetGradeWeights;
