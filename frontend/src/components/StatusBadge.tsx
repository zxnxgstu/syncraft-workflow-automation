export default function StatusBadge({status}:{status:string}){return <span className={`status-badge ${status.toLowerCase()}`}><i/>{status}</span>}
