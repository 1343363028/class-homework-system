// 平台检测与适配
import { computed } from 'vue'

export function usePlatform() {
  const ua = navigator.userAgent.toLowerCase()
  const isTauri = computed(() => '__TAURI_INTERNALS__' in window)
  const isCapacitor = computed(() => typeof (window as any).Capacitor !== 'undefined')
  const isWeb = computed(() => !isTauri.value && !isCapacitor.value)
  const isMobile = computed(() => /android|iphone|ipad|ipod/.test(ua) || isCapacitor.value)
  const isDesktop = computed(() => isTauri.value || (!isMobile.value && window.innerWidth >= 1024))

  const apiBase = computed(() => {
    if (isTauri.value || isCapacitor.value) {
      return import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'
    }
    return '/api'
  })

  return { isTauri, isCapacitor, isWeb, isMobile, isDesktop, apiBase }
}
