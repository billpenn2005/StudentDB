// src/components/BulkImport.js

import React, { useState } from 'react';
import { Upload, Button, Select, message, Typography } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import axiosInstance from '../axiosInstance';

const { Option } = Select;
const { Title } = Typography;

const BulkImport = () => {
    const [fileList, setFileList] = useState([]);
    const [importType, setImportType] = useState('students');
    const [uploading, setUploading] = useState(false);

    const handleChange = ({ fileList }) => setFileList(fileList);

    const handleUpload = async () => {
        if (fileList.length === 0) {
            message.error('请先选择文件');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileList[0].originFileObj);

        setUploading(true);
        try {
            let response;
            if (importType === 'students') {
                response = await axiosInstance.post('bulk-import/import_students/', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
            } else if (importType === 'teachers') {
                response = await axiosInstance.post('bulk-import/import_teachers/', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
            } else if (importType === 'course_prototypes') {
                response = await axiosInstance.post('bulk-import/import_course_prototypes/', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
            } else if (importType === 'course_instances') {
                response = await axiosInstance.post('bulk-import/import_course_instances/', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
            }
            // 处理其他类型...

            message.success(`导入成功: ${response.data.created} 条`);
            if (response.data.errors.length > 0) {
                message.warning(`部分导入失败: ${response.data.errors.length} 条`);
            }
            setFileList([]);
        } catch (error) {
            console.error('Import Error:', error);
            message.error('导入失败');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <Title level={3}>批量导入</Title>
            <Select value={importType} onChange={setImportType} style={{ width: 200, marginBottom: '20px' }}>
                <Option value="students">导入学生</Option>
                <Option value="teachers">导入教师</Option>
                <Option value="course_prototypes">导入课程原型</Option>
                <Option value="course_instances">导入课程实例</Option>
                {/* 添加更多选项 */}
            </Select>
            <Upload
                beforeUpload={() => false}
                onChange={handleChange}
                fileList={fileList}
                accept=".csv"
            >
                <Button icon={<UploadOutlined />}>选择文件</Button>
            </Upload>
            <Button
                type="primary"
                onClick={handleUpload}
                disabled={fileList.length === 0}
                loading={uploading}
                style={{ marginTop: '20px' }}
            >
                {uploading ? '导入中...' : '开始导入'}
            </Button>
        </div>
    );
};

export default BulkImport;
