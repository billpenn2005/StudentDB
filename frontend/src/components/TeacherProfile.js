// src/components/TeacherProfile.js

import React from 'react';
import { Typography, Card } from 'antd';

const { Title, Paragraph } = Typography;

const TeacherProfile = () => {
    return (
        <div style={styles.container}>
            <Title level={2}>个人信息</Title>
            <Card title="老师信息" bordered={false} style={styles.card}>
                <Paragraph>
                    姓名: 李四
                </Paragraph>
                <Paragraph>
                    教师编号: T12345
                </Paragraph>
                {/* 添加更多信息 */}
            </Card>
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

export default TeacherProfile;
