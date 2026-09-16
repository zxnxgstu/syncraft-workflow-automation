import { FormEvent, useState } from 'react'
import { ArrowRight, Braces, Eye, EyeOff, LockKeyhole, Send, Webhook } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import Logo from '../components/Logo'
import NetworkOrb from '../components/NetworkOrb'
import { api, tokenStore } from '../api/client'

const DEMO_EMAIL='demo@syncraft.dev'
const DEMO_PASSWORD='Syncraft123!'

export default function LoginPage(){
  const nav=useNavigate()
  const [mode,setMode]=useState<'login'|'register'>('login')
  const [fullName,setFullName]=useState('')
  const [email,setEmail]=useState(DEMO_EMAIL)
  const [password,setPassword]=useState(DEMO_PASSWORD)
  const [show,setShow]=useState(false)
  const [busy,setBusy]=useState(false)
  const [error,setError]=useState('')

  const updateEmail=(value:string)=>{setEmail(value); if(error)setError('')}
  const updatePassword=(value:string)=>{setPassword(value); if(error)setError('')}
  const switchMode=()=>{
    const next=mode==='login'?'register':'login'
    setMode(next); setError('')
    if(next==='login'){setEmail(DEMO_EMAIL);setPassword(DEMO_PASSWORD)}
  }
  const submit=async(e:FormEvent)=>{
    e.preventDefault();setBusy(true);setError('')
    try{
      const path=mode==='login'?'/api/v1/auth/login':'/api/v1/auth/register'
      const normalizedEmail=email.trim().toLowerCase()==='demo@syncraft.local'?DEMO_EMAIL:email.trim()
      const body=mode==='login'?{email:normalizedEmail,password}:{email:normalizedEmail,password,full_name:fullName.trim()}
      const d=await api<{access_token:string;refresh_token:string}>(path,{method:'POST',body:JSON.stringify(body)})
      tokenStore.set(d.access_token,d.refresh_token)
      nav('/dashboard')
    }catch(err){
      setError(err instanceof Error?err.message:'Unable to sign in. Please try again.')
    }finally{setBusy(false)}
  }

  return <div className="auth-page auth-v3">
    <div className="auth-space-lines" aria-hidden="true"/>
    <div className="auth-nebula auth-nebula-one" aria-hidden="true"/>
    <div className="auth-nebula auth-nebula-two" aria-hidden="true"/>

    <section className="auth-showcase auth-showcase-v3">
      <div className="auth-brand-row"><Logo to="/login"/></div>
      <div className="hero-layout">
        <div className="showcase-copy showcase-copy-v3">
          <h1>Make your tools<br/><em>work in sync.</em></h1>
          <p>Build automations that listen, transform data, call APIs and send updates — without babysitting every step.</p>
        </div>
        <NetworkOrb/>
      </div>

      <div className="flow-stage flow-stage-v3" aria-hidden="true">
        <div className="flow-card flow-card-a">
          <span className="flow-card-icon"><Webhook size={26}/></span>
          <div><b>Webhook</b><small>Catch an event</small></div>
          <i className="flow-status"/>
        </div>
        <div className="flow-link"><span/></div>
        <div className="flow-card flow-card-b">
          <span className="flow-card-icon"><Braces size={26}/></span>
          <div><b>Transform</b><small>Shape the payload</small></div>
          <i className="flow-status"/>
        </div>
        <div className="flow-link delay"><span/></div>
        <div className="flow-card flow-card-c">
          <span className="flow-card-icon"><Send size={26}/></span>
          <div><b>Notify</b><small>Send it instantly</small></div>
          <i className="flow-status"/>
        </div>
      </div>
    </section>

    <section className="auth-panel auth-panel-v3">
      <form className="auth-card auth-card-v3" onSubmit={submit}>
        <div className="auth-heading auth-heading-v3">
          <span className="auth-icon"><LockKeyhole size={23}/></span>
          <h2>{mode==='login'?'Welcome back':'Create account'}</h2>
          <p>{mode==='login'?'Enter your workspace.':'Start building automations.'}</p>
        </div>

        {error&&<div className="alert error auth-error" role="alert">{error}</div>}
        {mode==='register'&&<label>Full name<input value={fullName} onChange={e=>{setFullName(e.target.value);if(error)setError('')}} required autoComplete="name"/></label>}
        <label>Email address<input type="email" value={email} onChange={e=>updateEmail(e.target.value)} required name="syncraft-email" autoComplete="off"/></label>
        <label>Password<div className="password-field"><input type={show?'text':'password'} value={password} onChange={e=>updatePassword(e.target.value)} required name="syncraft-password" autoComplete={mode==='login'?'off':'new-password'}/><button type="button" aria-label="Toggle password visibility" onClick={()=>setShow(v=>!v)}>{show?<EyeOff size={20}/>:<Eye size={20}/>}</button></div></label>

        <button className="btn primary auth-submit" disabled={busy}>
          {busy?(mode==='login'?'Signing in...':'Creating account...'):<>{mode==='login'?'Sign in':'Create account'} <ArrowRight size={19}/></>}
        </button>

        <button type="button" className="auth-switch" onClick={switchMode}>
          {mode==='login'?'New here? Create an account':'Already have an account? Sign in'}
        </button>
      </form>
    </section>
  </div>
}
