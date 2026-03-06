import { Col, Row, message } from 'antd';
import { useEffect, useState } from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { StatCard } from '../components/common/StatCard';
import { fetchDocuments } from '../services/api/documents';
import { fetchExamList } from '../services/api/exam';
import { fetchModelConfig } from '../services/api/settings';

export function DashboardPage() {
  const [docCount, setDocCount] = useState<number>(0);
  const [examCount, setExamCount] = useState<number>(0);
  const [providerCount, setProviderCount] = useState<number>(0);

  useEffect(() => {
    const load = async () => {
      try {
        const [docs, exams, modelCfg] = await Promise.all([
          fetchDocuments(),
          fetchExamList(),
          fetchModelConfig()
        ]);
        setDocCount(docs.length);
        setExamCount(exams.length);
        setProviderCount(
          [
            modelCfg.configured_providers.deepseek,
            modelCfg.configured_providers.openai,
            modelCfg.configured_providers.zhipu
          ].filter(Boolean).length
        );
      } catch {
        message.error('仪表盘数据加载失败');
      }
    };
    void load();
  }, []);

  return (
    <div className="fade-up">
      <PageHeader title="教学工作台" subtitle="集中处理资料、备课和课堂答疑。" />
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <StatCard title="已上传文档" value={docCount} suffix="份" />
        </Col>
        <Col xs={24} md={8}>
          <StatCard title="已生成试卷" value={examCount} suffix="份" />
        </Col>
        <Col xs={24} md={8}>
          <StatCard title="可用模型提供商" value={providerCount} suffix="个" />
        </Col>
      </Row>
    </div>
  );
}
