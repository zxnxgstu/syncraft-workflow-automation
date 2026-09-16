import { useEffect, useState } from 'react'
import { UserRound } from 'lucide-react'
import { api } from '../api/client'
import type { User } from '../types'

export default function SettingsPage(){
  const [user,setUser]=useState<User|null>(null)
  useEffect(()=>{api<User>('/api/v1/auth/me').then(setUser)},[])

  return <>
    <div className="page-header"><div><span className="eyebrow">Workspace</span><h1>Settings</h1><p>Manage your account information and workspace appearance.</p></div></div>
    <div className="settings-grid single">
      <section className="panel settings-card">
        <div className="settings-icon"><UserRound/></div>
        <h2>Profile</h2>
        <p>Your Syncraft account information.</p>
        <label>Full name<input value={user?.full_name||''} readOnly aria-readonly="true"/></label>
        <label>Email address<input value={user?.email||''} readOnly aria-readonly="true"/></label>
        <p className="field-help account-note">Account details are read-only in this workspace.</p>
      </section>
    </div>
  </>
}
