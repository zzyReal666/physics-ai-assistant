import { Alert } from 'antd';

export function ErrorBoundary() {
  return <Alert type="error" message="页面发生错误" />;
}
