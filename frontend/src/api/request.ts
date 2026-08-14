// Axios 请求实例与拦截器
import axios, { type AxiosInstance } from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  timeout: 15000,
})

request.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        const auth = useAuthStore()
        auth.logout()
        router.push('/login')
      }
      return Promise.reject({
        status,
        message: data?.detail || data?.message || '请求失败',
      })
    }
    return Promise.reject({ status: 0, message: '网络错误，请检查连接' })
  }
)

export default request
