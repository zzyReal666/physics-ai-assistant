import { Col, Row } from 'antd';
import { PageHeader } from '../components/common/PageHeader';
import { StatCard } from '../components/common/StatCard';

export function DashboardPage() {
  return (
    <div className="fade-up">
      <PageHeader title="教学工作台" subtitle="集中处理资料、备课和课堂答疑。" />
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <StatCard title="今日答疑" value={12} suffix="次" />
        </Col>
        <Col xs={24} md={8}>
          <StatCard title="资料文档" value={18} suffix="份" />
        </Col>
        <Col xs={24} md={8}>
          <StatCard title="本周教案" value={6} suffix="份" />
        </Col>
      </Row>
    </div>
  );
}
