import type { ReactNode } from 'react'
import { Sparkles } from 'lucide-react'
export default function EmptyState({title,copy,action}:{title:string;copy:string;action?:ReactNode}){return <div className="empty-state"><span className="empty-icon"><Sparkles size={20}/></span><h3>{title}</h3><p>{copy}</p>{action}</div>}
