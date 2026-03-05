import { Space, Typography } from 'antd';

interface PageHeaderProps {
  title: string;
  subtitle: string;
}

export function PageHeader({ title, subtitle }: PageHeaderProps) {
  return (
    <Space direction="vertical" size={0} style={{ marginBottom: 16 }}>
      <Typography.Title level={2} className="page-title">
        {title}
      </Typography.Title>
      <Typography.Text className="page-subtitle">{subtitle}</Typography.Text>
    </Space>
  );
}
