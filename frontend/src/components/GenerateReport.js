import React, { useState } from 'react';
import { Select, Button, message, Typography } from 'antd';
import axiosInstance from '../axiosInstance';

const { Option } = Select;
const { Title } = Typography;

const GenerateReport = () => {
    const [reportType, setReportType] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleGenerate = async () => {
        if (!reportType) {
            message.error('请选择报表类型');
            return;
        }

        setLoading(true);
        try {
            const response = await axiosInstance.post('generate-report/', { type: reportType }, {
                responseType: 'blob', // 重要：指定响应类型为blob
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `${reportType}_report.pdf`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            message.success('报表生成成功');
        } catch (error) {
            console.error('Generate Report Error:', error);
            message.error('报表生成失败');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <Title level={3}>生成报表</Title>
            <Select
                placeholder="选择报表类型"
                style={{ width: 300, marginBottom: '20px' }}
                onChange={value => setReportType(value)}
            >
                <Option value="students">学生信息报表</Option>
                <Option value="grades">成绩报表</Option>
                <Option value="courses">课程报表</Option>
            </Select>
            <br />
            <Button
                type="primary"
                onClick={handleGenerate}
                loading={loading}
                disabled={!reportType}
            >
                生成并下载报表
            </Button>
        </div>
    );
};

export default GenerateReport;
