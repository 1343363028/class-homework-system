// 认证相关 API
import request from './request'
import type { TokenResponse, User } from '@/types'

export const authApi = {
  login(student_id: string, password?: string) {
    return request.post<TokenResponse>('/auth/login', { student_id, password: password || null })
  },
  getMe() {
    return request.get<User>('/auth/me')
  },
}
