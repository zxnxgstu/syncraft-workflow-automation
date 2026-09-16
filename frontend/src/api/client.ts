const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const ACCESS = 'syncraft-access'
const REFRESH = 'syncraft-refresh'

export const tokenStore = {
  access: () => localStorage.getItem(ACCESS),
  refresh: () => localStorage.getItem(REFRESH),
  set: (access:string, refresh:string) => { localStorage.setItem(ACCESS, access); localStorage.setItem(REFRESH, refresh) },
  clear: () => { localStorage.removeItem(ACCESS); localStorage.removeItem(REFRESH) },
}

function readableApiError(payload: unknown, fallback: string): string {
  if (!payload || typeof payload !== 'object') return fallback
  const detail = (payload as {detail?: unknown}).detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const messages = detail.map((item:any) => {
      if (typeof item === 'string') return item
      const where = Array.isArray(item?.loc) ? item.loc.filter((x:any)=>x!=='body').join('.') : ''
      const msg = typeof item?.msg === 'string' ? item.msg : 'Invalid value'
      return where ? `${where}: ${msg}` : msg
    }).filter(Boolean)
    if (messages.length) return messages.join(' · ')
  }
  if (detail && typeof detail === 'object') {
    const maybeMessage = (detail as {message?: unknown}).message
    if (typeof maybeMessage === 'string') return maybeMessage
  }
  return fallback
}

async function refreshTokens(){
  const refresh = tokenStore.refresh(); if(!refresh) return false
  const r = await fetch(`${API}/api/v1/auth/refresh`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({refresh_token:refresh})})
  if(!r.ok){tokenStore.clear(); return false}
  const data = await r.json(); tokenStore.set(data.access_token, data.refresh_token); return true
}

export async function api<T>(path:string, init:RequestInit = {}, retry=true):Promise<T>{
  const headers = new Headers(init.headers || {})
  if(!headers.has('Content-Type') && init.body) headers.set('Content-Type','application/json')
  const access = tokenStore.access(); if(access) headers.set('Authorization',`Bearer ${access}`)

  let r: Response
  try {
    r = await fetch(`${API}${path}`, {...init, headers})
  } catch {
    throw new Error('Cannot reach the Syncraft API. Make sure the backend container is running.')
  }

  if(r.status===401 && retry && await refreshTokens()) return api<T>(path, init, false)
  if(!r.ok){
    const fallback = r.status===401 ? 'Invalid email or password' : `Request failed (${r.status})`
    let message = fallback
    try { message = readableApiError(await r.json(), fallback) } catch {}
    throw new Error(message)
  }
  if(r.status===204) return undefined as T
  return r.json()
}

export const apiUrl = API
