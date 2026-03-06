import { Button, Card, Input, message, Select, Space, Tag, Typography } from 'antd';
import { useState } from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { useChatSession } from '../stores/chatSession';

export function ChatPage() {
  const [question, setQuestion] = useState('');
  const { state, setLevel, sendQuestion, clear } = useChatSession();

  const submit = async () => {
    const text = question.trim();
    if (!text) {
      message.warning('请输入问题');
      return;
    }
    setQuestion('');
    await sendQuestion(text);
  };

  return (
    <div>
      <PageHeader title="AI 答疑" subtitle="支持按学生水平进行解释，并附带文档引用片段。" />
      <Card className="glass-card" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space wrap>
            <Typography.Text>学生水平：</Typography.Text>
            <Select
              value={state.level}
              style={{ width: 140 }}
              options={[
                { label: '初中', value: 'junior' },
                { label: '高中', value: 'senior' }
              ]}
              onChange={(v) => setLevel(v)}
            />
          </Space>
          <Input.TextArea
            rows={4}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="例如：质量2kg物体受10N拉力，摩擦系数0.2，求加速度"
          />
          <Space>
            <Button
              type="primary"
              loading={state.pendingCount > 0}
              onClick={() => void submit()}
            >
              提交问题
            </Button>
            <Button onClick={clear}>清空会话</Button>
          </Space>
        </Space>
      </Card>

      <Card className="glass-card">
        {state.messages.length === 0 && <Typography.Text>还没有对话记录。</Typography.Text>}
        {state.messages.map((msg) => (
          <div className={`chat-msg ${msg.role}`} key={msg.id}>
            <Typography.Text strong>{msg.role === 'user' ? '你' : 'AI'}：</Typography.Text>
            <Typography.Paragraph style={{ whiteSpace: 'pre-wrap', marginBottom: 8 }}>
              {msg.content}
            </Typography.Paragraph>
            {msg.status === 'loading' && <Tag color="processing">回答中</Tag>}
            {msg.status === 'error' && <Tag color="red">失败</Tag>}
            {msg.answer && (
              <Space wrap>
                <Tag color={msg.answer.from_llm ? 'green' : 'gold'}>
                  {msg.answer.from_llm ? 'LLM' : 'Fallback'}
                </Tag>
                {msg.answer.model_used && <Tag>{msg.answer.model_used}</Tag>}
              </Space>
            )}
            {msg.answer?.references?.length ? (
              <div style={{ marginTop: 10 }}>
                <Typography.Text type="secondary">参考片段：</Typography.Text>
                {msg.answer.references.map((ref, i) => (
                  <Typography.Paragraph key={`${ref.source}-${i}`} style={{ margin: '4px 0 0' }}>
                    [{ref.source}] {ref.content}
                  </Typography.Paragraph>
                ))}
              </div>
            ) : null}
          </div>
        ))}
      </Card>
    </div>
  );
}
