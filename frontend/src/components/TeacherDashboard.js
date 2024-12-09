// src/components/TeacherDashboard.js

import React from 'react';
import { Typography, Card, List } from 'antd';

const { Title, Paragraph } = Typography;

const TeacherDashboard = () => {
    // 示例数据，可以根据实际需求从 API 获取
    const courses = [
        '高级数学 501',
        '量子物理 601',
        '有机化学 701',
    ];

    return (
        <div style={styles.container}>
            <Title level={2}>老师仪表盘</Title>
            <Card title="管理的课程" bordered={false} style={styles.card}>
                <List
                    bordered
                    dataSource={courses}
                    renderItem={item => <List.Item>{item}</List.Item>}
                />
            </Card>
            {/* 添加更多老师相关的内容 */}
        </div>
    );
};

const styles = {
    container: {
        textAlign: 'center',
        paddingTop: '50px',
    },
    card: {
        maxWidth: '600px',
        margin: 'auto',
    },
};

export default TeacherDashboard;
