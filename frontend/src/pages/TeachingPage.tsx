import { Button, Card, Form, Input, message, Space, Tag, Typography } from 'antd';
import { useState } from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { createTeachingPlan } from '../services/api/teaching';
import type { TeachingPlanResponse } from '../types';

export function TeachingPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TeachingPlanResponse | null>(null);
  const [form] = Form.useForm();

  const submit = async () => {
    const values = await form.validateFields();
    setLoading(true);
    try {
      const data = await createTeachingPlan(values.topic, values.class_info, values.requirements || '');
      setResult(data);
      message.success('教案生成完成');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title="备课助手" subtitle="输入主题与班级信息，快速生成结构化教案。" />
      <Card className="glass-card" style={{ marginBottom: 16 }}>
        <Form layout="vertical" form={form} initialValues={{ class_info: '高二重点班，45分钟' }}>
          <Form.Item name="topic" label="教学主题" rules={[{ required: true, message: '请输入主题' }]}>
            <Input placeholder="例如：牛顿第二定律" />
          </Form.Item>
          <Form.Item name="class_info" label="班级信息" rules={[{ required: true, message: '请输入班级信息' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="requirements" label="特殊要求">
            <Input.TextArea rows={4} placeholder="例如：包含实验演示和3道典型例题" />
          </Form.Item>
          <Button type="primary" loading={loading} onClick={() => void submit()}>
            生成教案
          </Button>
        </Form>
      </Card>
      {result && (
        <Card className="glass-card fade-up">
          <Space style={{ marginBottom: 12 }}>
            <Tag color={result.from_llm ? 'green' : 'gold'}>{result.from_llm ? 'LLM生成' : '示例输出'}</Tag>
            {result.model_used && <Tag>{result.model_used}</Tag>}
          </Space>
          <Typography.Paragraph style={{ whiteSpace: 'pre-wrap' }}>{result.plan_markdown}</Typography.Paragraph>
        </Card>
      )}
    </div>
  );
}
