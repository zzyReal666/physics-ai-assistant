import { Button, Card, Form, Input, Select, Space, Table, Tag, Typography, message } from 'antd';
import { useState } from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { downloadExamLatex, generateExam } from '../services/api/exam';
import type { ExamGenerateResponse } from '../types';

export function ExamPage() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ExamGenerateResponse | null>(null);

  const submit = async () => {
    const values = await form.validateFields();
    setLoading(true);
    try {
      const data = await generateExam(values);
      setResult(data);
      message.success('试卷生成完成');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title="出卷助手" subtitle="按知识点和难度快速生成阶段测试卷。" />
      <Card className="glass-card" style={{ marginBottom: 16 }}>
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            difficulty: 'medium',
            total_score: 100,
            question_types: '选择题4道 + 计算题2道',
            paper_type: '阶段测试'
          }}
        >
          <Form.Item name="knowledge_points" label="知识点范围" rules={[{ required: true, message: '请输入范围' }]}>
            <Input placeholder="例如：必修一 第三章 牛顿运动定律" />
          </Form.Item>
          <Space wrap style={{ width: '100%' }}>
            <Form.Item name="difficulty" label="难度" rules={[{ required: true }]}>
              <Select
                style={{ width: 160 }}
                options={[
                  { value: 'easy', label: '简单' },
                  { value: 'medium', label: '中等' },
                  { value: 'hard', label: '困难' }
                ]}
              />
            </Form.Item>
            <Form.Item name="total_score" label="总分" rules={[{ required: true }]}>
              <Input type="number" style={{ width: 120 }} />
            </Form.Item>
            <Form.Item name="paper_type" label="试卷类型" rules={[{ required: true }]}>
              <Input style={{ width: 180 }} />
            </Form.Item>
          </Space>
          <Form.Item name="question_types" label="题型组合">
            <Input />
          </Form.Item>
          <Button type="primary" loading={loading} onClick={() => void submit()}>
            生成试卷
          </Button>
        </Form>
      </Card>

      {result && (
        <Card className="glass-card fade-up">
          <Space style={{ marginBottom: 10 }}>
            <Typography.Text strong>{result.title}</Typography.Text>
            <Tag>{result.exam_id}</Tag>
            <Button type="link" href={downloadExamLatex(result.download_url)} target="_blank">
              下载 LaTeX
            </Button>
          </Space>
          <Table
            size="small"
            rowKey={(r) => r.title}
            dataSource={result.questions}
            pagination={false}
            columns={[
              { title: '题型', dataIndex: 'type', width: 90 },
              { title: '题目', dataIndex: 'title' },
              { title: '分值', dataIndex: 'score', width: 80 },
              { title: '答案思路', dataIndex: 'answer_outline' }
            ]}
          />
        </Card>
      )}
    </div>
  );
}
