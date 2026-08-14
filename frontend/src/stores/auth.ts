// 认证状态管理
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User, Role } from '@/types'

const TOKEN_KEY = 'hw_token'
const USER_KEY = 'hw_user'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref<User | null>(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const role = computed<Role | null>(() => user.value?.role || null)
  const isCommissary = computed(() => role.value === 'commissary')
  const displayName = computed(() => user.value?.name || '')

  async function login(student_id: string, password?: string) {
    const res = await authApi.login(student_id, password)
    token.value = res.data.access_token
    localStorage.setItem(TOKEN_KEY, token.value)
    await fetchMe()
  }

  async function fetchMe() {
    try {
      const res = await authApi.getMe()
      user.value = res.data
      localStorage.setItem(USER_KEY, JSON.stringify(user.value))
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  return { token, user, isLoggedIn, role, isCommissary, displayName, login, fetchMe, logout }
})
