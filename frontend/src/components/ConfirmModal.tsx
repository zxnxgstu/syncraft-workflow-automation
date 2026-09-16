import { X } from 'lucide-react'
export default function ConfirmModal({open,title,copy,onCancel,onConfirm,confirmLabel='Confirm'}:{open:boolean;title:string;copy:string;onCancel:()=>void;onConfirm:()=>void;confirmLabel?:string}){
 if(!open)return null; return <div className="modal-backdrop" onMouseDown={onCancel}><div className="modal" onMouseDown={e=>e.stopPropagation()}><button className="modal-close" onClick={onCancel}><X size={17}/></button><h2>{title}</h2><p>{copy}</p><div className="modal-actions"><button className="btn ghost" onClick={onCancel}>Cancel</button><button className="btn danger" onClick={onConfirm}>{confirmLabel}</button></div></div></div>
}
