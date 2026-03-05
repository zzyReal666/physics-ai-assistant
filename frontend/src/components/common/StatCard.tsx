import { Card, Statistic } from 'antd';

interface StatCardProps {
  title: string;
  value: string | number;
  suffix?: string;
}

export function StatCard({ title, value, suffix }: StatCardProps) {
  return (
    <Card className="glass-card fade-up" style={{ height: '100%' }}>
      <Statistic title={title} value={value} suffix={suffix} />
    </Card>
  );
}
