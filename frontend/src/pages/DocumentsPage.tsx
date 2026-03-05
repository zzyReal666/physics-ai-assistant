import { InboxOutlined, ReloadOutlined } from '@ant-design/icons';
import { Button, Card, Drawer, message, Space, Table, Tag, Typography, Upload } from 'antd';
import type { UploadProps } from 'antd';
import { useEffect, useState } from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { fetchDocumentDetail, fetchDocuments, uploadDocument } from '../services/api/documents';
import type { DocumentDetail, DocumentItem } from '../types';

const { Dragger } = Upload;

export function DocumentsPage() {
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [detail, setDetail] = useState<DocumentDetail | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      setDocs(await fetchDocuments());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadDocuments();
  }, []);

  const uploadProps: UploadProps = {
    multiple: false,
    showUploadList: true,
    customRequest: async ({ file, onSuccess, onError }) => {
      try {
        await uploadDocument(file as File);
        message.success('文档上传成功');
        onSuccess?.({}, new XMLHttpRequest());
        void loadDocuments();
      } catch (err) {
        message.error('文档上传失败');
        onError?.(err as Error);
      }
    }
  };

  const openDetail = async (id: string) => {
    setLoading(true);
    try {
      const data = await fetchDocumentDetail(id);
      setDetail(data);
      setDrawerOpen(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title="文档管理" subtitle="上传教材后，系统会自动记录并生成简化切片。" />
      <Card className="glass-card" style={{ marginBottom: 16 }}>
        <Dragger {...uploadProps} accept=".pdf,.docx,.pptx,.png,.jpg,.jpeg,.txt,.md">
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">拖拽文件到这里，或点击上传</p>
          <p className="ant-upload-hint">支持 PDF / Word / PPT / 图片 / TXT / Markdown</p>
        </Dragger>
      </Card>
      <Card className="glass-card" extra={<Button icon={<ReloadOutlined />} onClick={() => void loadDocuments()}>刷新</Button>}>
        <Table
          rowKey="id"
          loading={loading}
          dataSource={docs}
          columns={[
            { title: '文件名', dataIndex: 'filename' },
            { title: '类型', dataIndex: 'file_type', render: (v: string) => <Tag>{v}</Tag> },
            { title: '大小(B)', dataIndex: 'file_size' },
            { title: '状态', dataIndex: 'status' },
            { title: '上传时间', dataIndex: 'created_at' },
            {
              title: '操作',
              render: (_, record) => (
                <Button type="link" onClick={() => void openDetail(record.id)}>
                  查看
                </Button>
              )
            }
          ]}
        />
      </Card>
      <Drawer width={620} title={detail?.filename} open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        {detail && (
          <Space direction="vertical" size={14} style={{ width: '100%' }}>
            <Typography.Text>文件类型：{detail.file_type}</Typography.Text>
            <Typography.Text>切片数量：{detail.chunk_count}</Typography.Text>
            {detail.chunks.map((chunk) => (
              <Card size="small" key={chunk.index}>
                <Typography.Paragraph style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                  {chunk.content}
                </Typography.Paragraph>
              </Card>
            ))}
          </Space>
        )}
      </Drawer>
    </div>
  );
}
