import { Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { ChatPage } from './pages/ChatPage';
import { DashboardPage } from './pages/DashboardPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { ExamPage } from './pages/ExamPage';
import { ModelSettingsPage } from './pages/ModelSettingsPage';
import { TeachingPage } from './pages/TeachingPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppShell />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/teaching" element={<TeachingPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/exam" element={<ExamPage />} />
        <Route path="/settings" element={<ModelSettingsPage />} />
      </Route>
    </Routes>
  );
}

export default App;
