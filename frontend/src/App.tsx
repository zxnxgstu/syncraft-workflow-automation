import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import AppShell from './components/AppShell'
import { tokenStore } from './api/client'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import WorkflowsPage from './pages/WorkflowsPage'
import BuilderPage from './pages/BuilderPage'
import ExecutionsPage from './pages/ExecutionsPage'
import TemplatesPage from './pages/TemplatesPage'
import IntegrationsPage from './pages/IntegrationsPage'
import SettingsPage from './pages/SettingsPage'

function RequireAuth(){return tokenStore.access()?<Outlet/>:<Navigate to="/login" replace/>}
export default function App(){return <Routes><Route path="/login" element={<LoginPage/>}/><Route element={<RequireAuth/>}><Route element={<AppShell/>}><Route path="/dashboard" element={<DashboardPage/>}/><Route path="/workflows" element={<WorkflowsPage/>}/><Route path="/workflows/:id" element={<BuilderPage/>}/><Route path="/executions" element={<ExecutionsPage/>}/><Route path="/executions/:id" element={<ExecutionsPage/>}/><Route path="/templates" element={<TemplatesPage/>}/><Route path="/integrations" element={<IntegrationsPage/>}/><Route path="/settings" element={<SettingsPage/>}/></Route></Route><Route path="*" element={<Navigate to={tokenStore.access()?'/dashboard':'/login'} replace/>}/></Routes>}
