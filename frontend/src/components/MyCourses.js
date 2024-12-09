// src/components/MyCourses.js

import React from 'react';
import { Typography, Card, List } from 'antd';

const { Title } = Typography;

const MyCourses = () => {
    // 示例数据，可以从 API 获取
    const courses = [
        '数学 101',
        '物理 201',
        '化学 301',
    ];

    return (
        <div style={styles.container}>
            <Title level={2}>我的课程</Title>
            <Card title="课程列表" bordered={false} style={styles.card}>
                <List
                    bordered
                    dataSource={courses}
                    renderItem={item => <List.Item>{item}</List.Item>}
                />
            </Card>
            {/* 添加更多课程相关的内容 */}
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

export default MyCourses;
