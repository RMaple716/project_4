import React from 'react';
import { Typography, Button } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';

const { Title, Paragraph } = Typography;

const ItineraryDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  console.log('ItineraryDetail 组件已加载, ID:', id); // 调试日志

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Title level={3}>行程详情</Title>
      <Paragraph>行程ID: {id}</Paragraph>
      
      <Button onClick={() => navigate('/itineraries')}>
        返回列表
      </Button>
    </div>
  );
};

export default ItineraryDetail;
