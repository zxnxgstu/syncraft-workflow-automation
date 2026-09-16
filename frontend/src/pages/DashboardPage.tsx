import { useEffect, useMemo, useState } from 'react'
import type { CSSProperties } from 'react'
import { Activity, ArrowUpRight, CheckCircle2, Clock3, Layers3, Plus, RefreshCw, TrendingUp, XCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import StatusBadge from '../components/StatusBadge'

type ActivityRecord={id:number;status:'success'|'failed';started_at:string}
type MetricData={total_executions:number;success_executions:number;success_rate:number;failed_executions:number;average_duration_ms:number;workflows:number;active_workflows:number}
type RecentExecution={id:number;workflow_name:string;status:string;duration_ms:number;started_at:string}
type Dash={metrics:MetricData;recent_executions:RecentExecution[];execution_activity:ActivityRecord[]}
type Bucket={key:string;start:Date;success:number;failed:number;label:string}

const empty:Dash={metrics:{total_executions:0,success_executions:0,success_rate:0,failed_executions:0,average_duration_ms:0,workflows:0,active_workflows:0},recent_executions:[],execution_activity:[]}
const pad=(value:number)=>String(value).padStart(2,'0')

function groupActivity(records:ActivityRecord[]){
  const parsed=records.map(record=>({record,date:new Date(record.started_at)})).filter(item=>!Number.isNaN(item.date.getTime()))
  const dateKey=(date:Date)=>`${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())}`
  const days=new Set(parsed.map(item=>dateKey(item.date)))
  const granularity:'day'|'hour'=days.size>=2?'day':'hour'
  const buckets=new Map<string,Bucket>()
  for(const {record,date} of parsed){
    const day=dateKey(date);const key=granularity==='day'?day:`${day}T${pad(date.getHours())}`
    let bucket=buckets.get(key)
    if(!bucket){
      const start=granularity==='day'?new Date(date.getFullYear(),date.getMonth(),date.getDate()):new Date(date.getFullYear(),date.getMonth(),date.getDate(),date.getHours())
      const label=granularity==='day'?start.toLocaleDateString([],{month:'short',day:'numeric'}):start.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})
      bucket={key,start,success:0,failed:0,label};buckets.set(key,bucket)
    }
    if(record.status==='success')bucket.success+=1
    else if(record.status==='failed')bucket.failed+=1
  }
  const limit=granularity==='day'?14:24
  return {granularity,buckets:[...buckets.values()].sort((a,b)=>a.start.getTime()-b.start.getTime()).slice(-limit)}
}

function AreaChart({records}:{records:ActivityRecord[]}){
  const [{granularity,buckets},setGrouped]=useState(()=>groupActivity(records));const [hovered,setHovered]=useState<number|null>(null)
  useEffect(()=>{setGrouped(groupActivity(records));setHovered(null)},[records])
  const geometry=useMemo(()=>{const max=Math.max(...buckets.map(bucket=>bucket.success+bucket.failed),1);const top=25,bottom=155,left=52,right=472,height=bottom-top;const slot=(right-left)/Math.max(buckets.length,1);const width=Math.min(46,Math.max(18,slot*.55));const y=(value:number)=>bottom-(value/max)*height;const bars=buckets.map((bucket,index)=>{const center=left+slot*index+slot/2;return{x:center-width/2,center,width,successTop:y(bucket.success),totalTop:y(bucket.success+bucket.failed),bucket}});return{max,top,bottom,left,right,bars}},[buckets])
  if(!buckets.length)return <div className="chart-empty"><Activity size={24}/><span>No execution activity yet</span><small>Run a workflow to populate this chart.</small></div>
  const active=hovered===null?null:geometry.bars[hovered];const rangeLabel=granularity==='hour'?`Hourly activity · ${buckets[0].start.toLocaleDateString([],{month:'short',day:'numeric',year:'numeric'})}`:'Daily activity'
  return <div className="chart-wrap"><div className="chart-meta"><span className="chart-range">{rangeLabel}</span><span className="chart-legend"><i className="success"/>Successful <i className="failed"/>Failed</span></div><svg viewBox="0 0 500 190" className="area-chart bar-chart" role="img" aria-label={`${rangeLabel}. ${records.length} executions shown.`}>{[geometry.top,(geometry.top+geometry.bottom)/2,geometry.bottom].map((y,index)=><g key={y}><line x1={geometry.left} y1={y} x2={geometry.right} y2={y} className="gridline"/><text x="38" y={y+4} textAnchor="end">{index===0?geometry.max:index===1?Math.round(geometry.max/2):0}</text></g>)}{geometry.bars.map((bar,index)=><g key={bar.bucket.key} className="chart-hit" onMouseEnter={()=>setHovered(index)} onMouseLeave={()=>setHovered(null)} onFocus={()=>setHovered(index)} onBlur={()=>setHovered(null)} tabIndex={0} aria-label={`${bar.bucket.label}: ${bar.bucket.success} successful, ${bar.bucket.failed} failed`}><rect x={bar.x-10} y={geometry.top-5} width={bar.width+20} height={geometry.bottom-geometry.top+18} fill="transparent"/><rect x={bar.x} y={bar.successTop} width={bar.width} height={geometry.bottom-bar.successTop} rx="6" className="success-bar"/>{bar.bucket.failed>0&&<rect x={bar.x} y={bar.totalTop} width={bar.width} height={bar.successTop-bar.totalTop} rx="6" className="failed-bar"/>}<text x={bar.center} y="181" textAnchor="middle">{bar.bucket.label}</text></g>)}</svg>{active&&<div className="chart-tooltip" style={{left:`${active.center/5}%`,top:`${Math.max(active.totalTop-8,18)/1.9}%`}}><b>{active.bucket.start.toLocaleString([],{month:'short',day:'numeric',hour:granularity==='hour'?'2-digit':undefined,minute:granularity==='hour'?'2-digit':undefined})}</b><span><i className="success"/>Successful: {active.bucket.success}</span><span><i className="failed"/>Failed: {active.bucket.failed}</span><small>Total: {active.bucket.success+active.bucket.failed}</small></div>}</div>
}

export default function DashboardPage(){
  const [data,setData]=useState<Dash>(empty);const [loading,setLoading]=useState(true);const [error,setError]=useState('');const nav=useNavigate()
  const load=()=>{setLoading(true);setError('');api<Dash>('/api/v1/dashboard').then(setData).catch(e=>setError(e instanceof Error?e.message:'Could not load dashboard data.')).finally(()=>setLoading(false))}
  useEffect(load,[]);const m=data.metrics
  return <>
    <div className="page-header dashboard-heading"><div><span className="eyebrow">Overview</span><h1>Automation <span>control center</span></h1><p>Monitor your workflows, execution health and recent activity.</p></div><div className="header-actions"><button className="btn ghost" onClick={load}><RefreshCw size={17} className={loading?'spin':''}/>Refresh</button><button className="btn primary" onClick={()=>nav('/workflows/new')}><Plus size={18}/>New workflow</button></div></div>
    {error&&<div className="alert error dashboard-error" role="alert"><span>{error}</span><button onClick={load}>Try again</button></div>}
    <div className={`metric-grid ${loading?'is-loading':''}`} aria-busy={loading}><div className="metric"><span className="metric-icon blue"><Activity/></span><div><small>Total executions</small><strong>{m.total_executions}</strong><em><TrendingUp size={14}/>all time</em></div></div><div className="metric"><span className="metric-icon green"><CheckCircle2/></span><div><small>Success rate</small><strong>{m.success_rate}%</strong><em>healthy</em></div></div><div className="metric"><span className="metric-icon red"><XCircle/></span><div><small>Failed</small><strong>{m.failed_executions}</strong><em>needs review</em></div></div><div className="metric"><span className="metric-icon violet"><Clock3/></span><div><small>Avg. duration</small><strong>{(m.average_duration_ms/1000).toFixed(2)}s</strong><em>per run</em></div></div></div>
    <div className="dash-grid"><section className="panel analytics-panel"><div className="panel-head"><div><h2>Execution activity</h2><p>Completed runs grouped from real execution timestamps.</p></div><span className="soft-badge"><span className="live-dot"/>Live data</span></div><AreaChart records={data.execution_activity}/></section><section className="panel health-panel"><div className="panel-head"><div><h2>Workspace health</h2><p>At a glance.</p></div></div><div className="health-ring" style={{'--value':`${Math.min(m.success_rate,100)*3.6}deg`} as CSSProperties}><div><strong>{m.success_rate}%</strong><small>success</small></div></div><div className="health-stats"><span><Layers3 size={17}/><b>{m.active_workflows}/{m.workflows}</b> active workflows</span><span><CheckCircle2 size={17}/><b>{m.success_executions}</b> successful runs</span></div></section></div>
    <section className="panel recent-panel"><div className="panel-head"><div><h2>Recent executions</h2><p>Your latest workflow runs and statuses.</p></div><button className="text-btn" onClick={()=>nav('/executions')}>View all <ArrowUpRight size={16}/></button></div><div className="execution-table"><div className="table-head"><span>Workflow</span><span>Trigger</span><span>Status</span><span>Duration</span><span>Started</span></div>{data.recent_executions.length?data.recent_executions.map(row=><button className="table-row" key={row.id} onClick={()=>nav(`/executions/${row.id}`)}><span className="workflow-cell"><i className="flow-glyph"/><b>{row.workflow_name}</b></span><span>automation</span><span><StatusBadge status={row.status}/></span><span>{row.duration_ms} ms</span><span>{new Date(row.started_at).toLocaleString([], {month:'short',day:'2-digit',hour:'2-digit',minute:'2-digit'})}</span></button>):<div className="table-empty">No executions yet. Run a workflow to see activity here.</div>}</div></section>
  </>
}
