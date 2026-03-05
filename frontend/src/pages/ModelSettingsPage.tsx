import { Alert, Button, Card, Form, Select, Space, Tag, Typography, message } from 'antd';
import { useEffect, useState } from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { fetchModelConfig, updateModelConfig } from '../services/api/settings';
import type { ModelConfig } from '../types';

export function ModelSettingsPage() {
  const [config, setConfig] = useState<ModelConfig | null>(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      setConfig(await fetchModelConfig());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const save = async (values: { default_llm_model: string }) => {
    setLoading(true);
    try {
      const next = await updateModelConfig(values.default_llm_model);
      setConfig(next);
      message.success('模型配置已更新');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title="模型配置" subtitle="管理默认大模型与提供商接入状态。" />
      <Card className="glass-card" loading={loading}>
        {!config ? null : (
          <Space direction="vertical" size={12} style={{ width: '100%' }}>
            <Alert
              type="info"
              showIcon
              message="提供商状态基于后端 .env 中 API Key 是否配置。"
            />
            <div>
              <Typography.Text strong>当前默认模型：</Typography.Text>
              <Tag style={{ marginLeft: 8 }}>{config.default_llm_model}</Tag>
            </div>
            <Space wrap>
              <Tag color={config.configured_providers.deepseek ? 'green' : 'default'}>
                DeepSeek: {config.configured_providers.deepseek ? '已配置' : '未配置'}
              </Tag>
              <Tag color={config.configured_providers.openai ? 'green' : 'default'}>
                OpenAI: {config.configured_providers.openai ? '已配置' : '未配置'}
              </Tag>
              <Tag color={config.configured_providers.zhipu ? 'green' : 'default'}>
                智谱: {config.configured_providers.zhipu ? '已配置' : '未配置'}
              </Tag>
            </Space>
            <Form layout="inline" initialValues={{ default_llm_model: config.default_llm_model }} onFinish={(v) => void save(v)}>
              <Form.Item name="default_llm_model" rules={[{ required: true, message: '请选择模型' }]}>
                <Select style={{ width: 220 }} options={config.candidate_models.map((m) => ({ value: m, label: m }))} />
              </Form.Item>
              <Form.Item>
                <Button htmlType="submit" type="primary" loading={loading}>
                  保存
                </Button>
              </Form.Item>
              <Form.Item>
                <Button onClick={() => void load()} disabled={loading}>
                  刷新
                </Button>
              </Form.Item>
            </Form>
          </Space>
        )}
      </Card>
    </div>
  );
}
