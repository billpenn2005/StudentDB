// src/components/MyCourses.js

import React, { useContext, useState, useEffect } from 'react';
import { Typography, Card, List, Spin, message } from 'antd';
import axiosInstance from '../axiosInstance'; // 确保路径正确
import { AuthContext } from '../contexts/AuthContext'; // 确保路径正确

const { Title } = Typography;

const MyCourses = () => {
    const { user } = useContext(AuthContext); // 获取当前用户信息
    const [courses, setCourses] = useState([]); // 初始化课程状态为一个空数组
    const [loading, setLoading] = useState(false); // 初始化加载状态

    useEffect(() => {
        const fetchCourses = async () => {
            setLoading(true); // 开始加载
            try {
                const response = await axiosInstance.get('course-instances/list_selected_courses/');
                setCourses(response.data); // 设置课程数据
                message.success('课程信息获取成功');
            } catch (error) {
                console.error(error);
                message.error('课程信息获取失败，请稍后再试');
            } finally {
                setLoading(false); // 结束加载
            }
        };

        fetchCourses(); // 调用数据获取函数
    }, []); // 依赖数组为空，表示只在组件挂载时执行一次

    return (
        <div style={styles.container}>
            <Title level={2}>我的选课</Title>
            <Card title="课程列表" bordered={false} style={styles.card}>
                {loading ? (
                    <Spin tip="正在加载课程..." />
                ) : (
                    <List
                        bordered
                        dataSource={courses}
                        renderItem={item => (
                            <List.Item>
                                <Typography.Text strong>{item.course_prototype.name}</Typography.Text> - {item.semester}
                            </List.Item>
                        )}
                        locale={{ emptyText: '您当前没有选课记录' }}
                    />
                )}
            </Card>
            {/* 根据需要添加更多课程相关的内容 */}
        </div>
    );
};

const styles = {
    container: {
        textAlign: 'center',
        paddingTop: '50px',
        paddingLeft: '20px',
        paddingRight: '20px',
    },
    card: {
        maxWidth: '800px',
        margin: 'auto',
    },
};

export default MyCourses;
