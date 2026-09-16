import { Cloud, Database, Github, MessageCircle, PanelsTopLeft } from 'lucide-react'

export default function NetworkOrb(){
  return (
    <div className="network-orb" aria-hidden="true">
      <div className="orb-halo orb-halo-a"/>
      <div className="orb-halo orb-halo-b"/>
      <div className="orb-core">
        <div className="orb-grid"/>
        <div className="orb-shine"/>
        <div className="orb-brand-mark"><span/><span/></div>
      </div>
      <div className="orbit orbit-one"><span className="orbit-dot dot-a"/><span className="orbit-dot dot-b"/></div>
      <div className="orbit orbit-two"><span className="orbit-dot dot-c"/></div>
      <div className="orbit orbit-three"><span className="orbit-dot dot-d"/></div>
      <div className="orbit-chip chip-github"><Github size={20}/></div>
      <div className="orbit-chip chip-message"><MessageCircle size={20}/></div>
      <div className="orbit-chip chip-cloud"><Cloud size={20}/></div>
      <div className="orbit-chip chip-data"><Database size={20}/></div>
      <div className="orbit-chip chip-app"><PanelsTopLeft size={20}/></div>
    </div>
  )
}
