import { createContext, useContext, useLayoutEffect, useState } from 'react'
import type { ReactNode } from 'react'

export type Theme = 'light' | 'dark'

type ThemeContextValue = {
  theme: Theme
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
}

const STORAGE_KEY = 'syncraft-theme'
const ThemeContext = createContext<ThemeContextValue | null>(null)

function storedTheme(): Theme {
  return localStorage.getItem(STORAGE_KEY) === 'light' ? 'light' : 'dark'
}

function applyTheme(theme: Theme) {
  document.documentElement.dataset.theme = theme
  document.documentElement.style.colorScheme = theme
  document.querySelector<HTMLMetaElement>('meta[name="theme-color"]')?.setAttribute('content', theme === 'light' ? '#f8faf8' : '#050b08')
  localStorage.setItem(STORAGE_KEY, theme)
}

export function ThemeProvider({children}:{children:ReactNode}) {
  const [theme,setThemeState] = useState<Theme>(storedTheme)

  useLayoutEffect(()=>applyTheme(theme),[theme])

  const setTheme = (next:Theme) => {
    applyTheme(next)
    setThemeState(next)
  }

  return <ThemeContext.Provider value={{theme,setTheme,toggleTheme:()=>setTheme(theme === 'dark' ? 'light' : 'dark')}}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  const value = useContext(ThemeContext)
  if(!value) throw new Error('useTheme must be used inside ThemeProvider')
  return value
}
