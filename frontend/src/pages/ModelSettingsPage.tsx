import { Alert, Button, Card, Form, Input, Select, Space, Tag, Typography, message } from 'antd';
import { useEffect, useState } from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { fetchModelConfig, updateModelRuntimeConfig } from '../services/api/settings';
import type { ModelConfig } from '../types';

export function ModelSettingsPage() {
  const [config, setConfig] = useState<ModelConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchModelConfig();
      setConfig(data);
      form.setFieldsValue(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const save = async (values: {
    default_llm_model: string;
    deepseek_api_key: string;
    deepseek_base_url: string;
    openai_api_key: string;
    openai_base_url: string;
    zhipu_api_key: string;
    zhipu_base_url: string;
  }) => {
    setLoading(true);
    try {
      const next = await updateModelRuntimeConfig(values);
      setConfig(next);
      form.setFieldsValue(next);
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
              message="可在本页面直接维护运行时模型配置（保存到后端 data 目录）。"
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
            <Form
              form={form}
              layout="vertical"
              initialValues={config}
              onFinish={(v) => void save(v)}
              style={{ width: '100%' }}
            >
              <Form.Item
                name="default_llm_model"
                label="默认模型"
                rules={[{ required: true, message: '请选择模型' }]}
              >
                <Select
                  style={{ width: 260 }}
                  options={config.candidate_models.map((m) => ({ value: m, label: m }))}
                />
              </Form.Item>
              <Form.Item name="deepseek_api_key" label="DeepSeek API Key">
                <Input.Password placeholder="可留空" />
              </Form.Item>
              <Form.Item name="deepseek_base_url" label="DeepSeek Base URL">
                <Input />
              </Form.Item>
              <Form.Item name="openai_api_key" label="OpenAI API Key">
                <Input.Password placeholder="可留空" />
              </Form.Item>
              <Form.Item name="openai_base_url" label="OpenAI Base URL">
                <Input />
              </Form.Item>
              <Form.Item name="zhipu_api_key" label="智谱 API Key">
                <Input.Password placeholder="可留空" />
              </Form.Item>
              <Form.Item name="zhipu_base_url" label="智谱 Base URL">
                <Input />
              </Form.Item>
              <Space>
                <Button htmlType="submit" type="primary" loading={loading}>
                  保存
                </Button>
                <Button onClick={() => void load()} disabled={loading}>
                  刷新
                </Button>
              </Space>
            </Form>
          </Space>
        )}
      </Card>
    </div>
  );
}
