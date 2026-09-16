import { useId } from 'react'
import { Link } from 'react-router-dom'

export default function Logo({ compact = false, to = '/dashboard' }: { compact?: boolean; to?: string }) {
  const uid = useId().replace(/:/g,'')
  const g1 = `syncraft-g1-${uid}`
  const g2 = `syncraft-g2-${uid}`
  return (
    <Link to={to} className="logo logo-syncraft" aria-label="Syncraft home">
      <span className="logo-mark syncraft-mark" aria-hidden="true">
        <svg viewBox="0 0 64 64" role="img">
          <defs>
            <linearGradient id={g1} x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stopColor="#dfff4f"/>
              <stop offset=".52" stopColor="#8cf873"/>
              <stop offset="1" stopColor="#61f0d1"/>
            </linearGradient>
            <linearGradient id={g2} x1="1" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#72ffd1"/>
              <stop offset=".52" stopColor="#86f981"/>
              <stop offset="1" stopColor="#c8ff4d"/>
            </linearGradient>
          </defs>
          <path d="M17 40.5 10.5 34a10.6 10.6 0 0 1 0-15l8.3-8.3a10.6 10.6 0 0 1 15 0l3.7 3.7" fill="none" stroke={`url(#${g1})`} strokeWidth="7" strokeLinecap="round"/>
          <path d="m47 23.5 6.5 6.5a10.6 10.6 0 0 1 0 15l-8.3 8.3a10.6 10.6 0 0 1-15 0l-3.7-3.7" fill="none" stroke={`url(#${g2})`} strokeWidth="7" strokeLinecap="round"/>
          <path d="m23 41 18-18" fill="none" stroke="#efffe9" strokeOpacity=".92" strokeWidth="6" strokeLinecap="round"/>
        </svg>
      </span>
      {!compact && <span className="logo-word">Syncraft</span>}
    </Link>
  )
}
