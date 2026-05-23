import React from 'react';
import { Typography, Button } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';

const { Title, Paragraph } = Typography;

const TaskStatus: React.FC = () => {
  const navigate = useNavigate();
  const { taskId } = useParams();

  console.log('TaskStatus 组件已加载, TaskID:', taskId); // 调试日志

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Title level={3}>任务状态</Title>
      <Paragraph>任务ID: {taskId}</Paragraph>
      <Paragraph>这里将显示任务进度...</Paragraph>
      
      <Button onClick={() => navigate('/')}>
        返回首页
      </Button>
    </div>
  );
};

export default TaskStatus;
