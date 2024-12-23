// src/components/MyCourses.js

import React, { useEffect, useContext, useState } from 'react';
import { List, Card, Button, Spin, Modal, message, Badge, Select } from 'antd';
import { AuthContext } from '../contexts/AuthContext';
import axiosInstance from '../axiosInstance';

const { Option } = Select;

const SelectedCourses = () => {
    const { selectedCourses, fetchSelectedCourses, fetchUser, loading: authLoading } = useContext(AuthContext);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [selectionBatches, setSelectionBatches] = useState([]);
    const [selectedBatchId, setSelectedBatchId] = useState(null);

    useEffect(() => {
        const loadSelectionBatches = async () => {
            try {
                const response = await axiosInstance.get('selection-batches/');
                const batches = response.data.results || response.data;
                setSelectionBatches(batches);
                // 自动选择当前有效的批次
                const now = new Date();
                const currentBatch = batches.find(batch =>
                    new Date(batch.start_selection_date) <= now && now <= new Date(batch.end_selection_date)
                );
                if (currentBatch) {
                    setSelectedBatchId(currentBatch.id);
                }
            } catch (error) {
                console.error('Fetch Selection Batches Error:', error);
                message.error('获取选课批次失败');
            }
        };
        loadSelectionBatches();
    }, []);

    useEffect(() => {
        const loadSelectedCourses = async () => {
            if (!selectedBatchId) {
                setLoading(false);
                return;
            }
            setLoading(true);
            await fetchSelectedCourses(selectedBatchId);
            setLoading(false);
        };
        loadSelectedCourses();
    }, [fetchSelectedCourses, selectedBatchId]);

    const handleUnenroll = (course) => {
        console.log('Unenrolling from course:', course.teacher?.user?.first_name);

        Modal.confirm({
            title: '确认退选',
            content: `您确定要退选课程 "${course.course_prototype.name}" 吗？`,
            okText: '确认',
            cancelText: '取消',
            onOk: async () => {
                setSubmitting(true);
                try {
                    await axiosInstance.post(`course-instances/${course.id}/drop/`);
                    message.success('退选成功');
                    await fetchUser();
                    await fetchSelectedCourses(selectedBatchId);
                } catch (error) {
                    console.error(error);
                    message.error('退选失败');
                } finally {
                    setSubmitting(false);
                }
            },
        });
    };

    const handleBatchChange = (value) => {
        setSelectedBatchId(value);
    };

    if (loading || authLoading) {
        return (
            <div style={{ textAlign: 'center', paddingTop: '50px' }}>
                <Spin tip="加载中..." size="large" />
            </div>
        );
    }

    return (
        <div style={{ padding: '20px' }}>
            <h2>已选课程</h2>
            <div style={{ marginBottom: '20px' }}>
                <span style={{ marginRight: '10px' }}>选择选课批次:</span>
                <Select
                    style={{ width: 300 }}
                    placeholder="请选择选课批次"
                    value={selectedBatchId}
                    onChange={handleBatchChange}
                >
                    {selectionBatches.map(batch => (
                        <Option key={batch.id} value={batch.id}>
                            {batch.name} ({new Date(batch.start_selection_date).toLocaleString()} - {new Date(batch.end_selection_date).toLocaleString()})
                        </Option>
                    ))}
                </Select>
            </div>
            {selectedCourses.length === 0 ? (
                <p>您当前没有选中的课程。</p>
            ) : (
                <List
                    grid={{ gutter: 16, column: 1 }}
                    dataSource={selectedCourses}
                    renderItem={course => (
                        <List.Item key={course.id}>
                            <Card
                                title={`${course.course_prototype.name} (${course.course_prototype.credits} 学分)`}
                                bordered
                                size="small"
                            >
                                <p><strong>描述：</strong> {course.description}</p>
                                <p>
                                    <strong>教师：</strong> 
                                    {course.teacher && course.teacher.user 
                                        ? `${course.teacher.user.first_name} ${course.teacher.user.last_name}` 
                                        : '未知'}
                                </p>
                                <p><strong>班级：</strong> {course.group}</p>
                                <Button
                                    type="danger"
                                    onClick={() => handleUnenroll(course)}
                                    loading={submitting}
                                    size="small"
                                    disabled={course.is_finalized} // 禁用退选按钮
                                >
                                    退选
                                </Button>
                                {course.is_finalized && (
                                    <Badge status="warning" text="已截止退选" style={{ marginLeft: '10px' }} />
                                )}
                            </Card>
                        </List.Item>
                    )}
                />
            )}
        </div>
    );
};

export default SelectedCourses;