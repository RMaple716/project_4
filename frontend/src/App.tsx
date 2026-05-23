import React from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, theme } from 'antd';
import { 
  HomeOutlined, 
  PlusOutlined, 
  CalendarOutlined,
  CompassOutlined 
} from '@ant-design/icons';
import { routes } from './routes';

const { Header, Content, Footer } = Layout;

// 内部组件，可以使用useNavigate和useLocation
const AppContent: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { token: { colorBgContainer, borderRadiusLG } } = theme.useToken();

  console.log('当前路径:', location.pathname); // 调试日志

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/requirement',
      icon: <PlusOutlined />,
      label: '新建行程',
    },
    {
      key: '/itineraries',
      icon: <CalendarOutlined />,
      label: '我的行程',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    console.log('点击菜单:', key); // 调试日志
    navigate(key);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px' }}>
        <div style={{ 
          color: 'white', 
          fontSize: '20px', 
          fontWeight: 'bold',
          marginRight: '48px'
        }}>
          <CompassOutlined /> 旅游行程规划
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ flex: 1, minWidth: 0 }}
        />
      </Header>
      
      <Content style={{ padding: '0' }}>
        <div
          style={{
            background: colorBgContainer,
            minHeight: 280,
            borderRadius: borderRadiusLG,
          }}
        >
          <Routes>
            {routes.map((route, index) => (
              <Route
                key={index}
                path={route.path}
                element={route.element}
              />
            ))}
          </Routes>
        </div>
      </Content>
      
      <Footer style={{ textAlign: 'center' }}>
        旅游行程规划系统 ©2026 Created with React + TypeScript
      </Footer>
    </Layout>
  );
};

// 主应用组件，提供BrowserRouter上下文
const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
};

export default App;
