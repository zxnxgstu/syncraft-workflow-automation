import { useEffect, useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { Blocks, CirclePlay, LayoutDashboard, LogOut, Menu, Moon, Network, PanelLeftClose, PanelLeftOpen, Search, Settings, Sun, Workflow, X, Zap } from 'lucide-react'
import Logo from './Logo'
import { useTheme } from './ThemeProvider'
import { tokenStore } from '../api/client'

const nav=[['Dashboard','/dashboard',LayoutDashboard],['Workflows','/workflows',Workflow],['Executions','/executions',CirclePlay],['Templates','/templates',Blocks],['Integrations','/integrations',Network]] as const
const SIDEBAR_KEY='syncraft-sidebar-collapsed'

export default function AppShell(){
 const {theme,toggleTheme}=useTheme()
 const [collapsed,setCollapsed]=useState(()=>localStorage.getItem(SIDEBAR_KEY)==='true')
 const [mobileOpen,setMobileOpen]=useState(false)
 const [search,setSearch]=useState('')
 const navg=useNavigate(); const loc=useLocation()

 useEffect(()=>{localStorage.setItem(SIDEBAR_KEY,String(collapsed))},[collapsed])
 useEffect(()=>{setSearch('');setMobileOpen(false)},[loc.pathname])

 const logout=()=>{tokenStore.clear();navg('/login')}
 const toggleSidebar=()=>setCollapsed(v=>!v)

 return <div className={`app-shell ${collapsed?'collapsed':''} ${mobileOpen?'mobile-open':''}`}>
  {mobileOpen&&<button className="sidebar-scrim" aria-label="Close navigation" onClick={()=>setMobileOpen(false)}/>} 
  <aside className="sidebar" aria-label="Primary navigation">
   <div className="sidebar-top">
    <Logo compact={collapsed}/>
    <button className="icon-btn sidebar-toggle" onClick={toggleSidebar} aria-label={collapsed?'Expand sidebar':'Collapse sidebar'}>
      {collapsed ? <PanelLeftOpen size={18}/> : <PanelLeftClose size={18}/>}
    </button>
   </div>
   {!collapsed&&<div className="workspace-label"><span className="workspace-pulse"/><span>Automation workspace</span></div>}
   <nav>
    {nav.map(([label,path,Icon]) => (
      <NavLink key={path} to={path} aria-label={label} className={({isActive})=>`nav-link ${isActive?'active':''}`}>
        <Icon size={19}/>{!collapsed&&<span>{label}</span>}
      </NavLink>
    ))}
   </nav>
   <div className="sidebar-footer">
    <NavLink to="/settings" aria-label="Settings" className="nav-link"><Settings size={19}/>{!collapsed&&<span>Settings</span>}</NavLink>
    <button className="nav-link button-link" type="button" aria-label="Sign out" onClick={logout}><LogOut size={19}/>{!collapsed&&<span>Sign out</span>}</button>
   </div>
  </aside>
  <section className="main-area">
   <header className="topbar"><button className="icon-btn mobile-menu" onClick={()=>setMobileOpen(v=>!v)} aria-label={mobileOpen?'Close navigation':'Open navigation'}>{mobileOpen?<X size={20}/>:<Menu size={20}/>}</button><div className="global-search"><Search size={19}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search workflows, executions, templates..."/></div><div className="top-actions"><button className="theme-switch" onClick={toggleTheme} aria-label={theme==='dark'?'Use light theme':'Use dark theme'}><span className={theme==='light'?'active':''}><Sun size={18}/></span><span className={theme==='dark'?'active':''}><Moon size={17}/></span></button><button className="quick-btn" onClick={()=>navg('/workflows/new')}><Zap size={18}/>New workflow</button><div className="user-chip"><span>N</span><div><strong>Nikita</strong><small>Workspace owner</small></div></div></div></header>
   <main className="content"><Outlet context={{search}}/></main>
  </section>
 </div>
}
