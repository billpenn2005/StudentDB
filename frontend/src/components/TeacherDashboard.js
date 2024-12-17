// src/components/TeacherDashboard.js

import React from 'react';
import { Card, Statistic, Row, Col } from 'antd';
import { BookOutlined, ProfileOutlined, TeamOutlined } from '@ant-design/icons';

const TeacherDashboard = () => {
    return (
        <div>
            <h1>老师仪表盘</h1>
            <Row gutter={16}>
                <Col span={8}>
                    <Card>
                        <Statistic
                            title="管理课程"
                            value={3} // 动态数据
                            prefix={<BookOutlined />}
                        />
                    </Card>
                </Col>
                <Col span={8}>
                    <Card>
                        <Statistic
                            title="录入成绩"
                            value={10} // 动态数据
                            prefix={<ProfileOutlined />}
                        />
                    </Card>
                </Col>
                <Col span={8}>
                    <Card>
                        <Statistic
                            title="管理学生"
                            value={50} // 动态数据
                            prefix={<TeamOutlined />}
                        />
                    </Card>
                </Col>
            </Row>
            {/* 其他仪表盘内容 */}
        </div>
    );
};

export default TeacherDashboard;
