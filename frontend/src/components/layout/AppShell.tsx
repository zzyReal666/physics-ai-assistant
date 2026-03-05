import {
  BookOutlined,
  DashboardOutlined,
  MessageOutlined,
  SettingOutlined,
  ToolOutlined
} from '@ant-design/icons';
import { Layout, Menu, Typography } from 'antd';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';

const { Sider, Content, Header } = Layout;

const items = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: '仪表盘' },
  { key: '/documents', icon: <BookOutlined />, label: '文档管理' },
  { key: '/teaching', icon: <ToolOutlined />, label: '备课助手' },
  { key: '/chat', icon: <MessageOutlined />, label: 'AI 答疑' },
  { key: '/settings', icon: <SettingOutlined />, label: '模型配置' }
];

export function AppShell() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Layout style={{ minHeight: '100vh', background: 'transparent' }}>
      <Sider
        width={240}
        style={{ background: '#102a27', borderRight: '1px solid #203f3b', paddingTop: 20 }}
      >
        <Typography.Title level={4} style={{ color: '#d7f8f2', margin: '0 16px 16px' }}>
          物理教学助手
        </Typography.Title>
        <Menu
          mode="inline"
          items={items}
          selectedKeys={[location.pathname]}
          onClick={({ key }) => navigate(key)}
          style={{ background: 'transparent', color: '#d7f8f2', borderRight: 0 }}
          theme="dark"
        />
      </Sider>
      <Layout style={{ background: 'transparent' }}>
        <Header
          style={{ background: 'transparent', padding: '20px 24px 0', height: 'auto', lineHeight: '1.2' }}
        >
          <Typography.Text style={{ color: '#476762' }}>
            Physics AI Assistant · 教师端 MVP
          </Typography.Text>
        </Header>
        <Content style={{ margin: 24, marginTop: 8 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
