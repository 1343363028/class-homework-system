// 科目相关 API
import request from './request'
import type { Subject, SubjectUpdate } from '@/types'

export const subjectApi = {
  list() {
    return request.get<Subject[]>('/subjects')
  },
  create(data: { name: string; color: string; icon: string }) {
    return request.post<Subject>('/subjects', data)
  },
  update(id: number, data: SubjectUpdate) {
    return request.put<Subject>(`/subjects/${id}`, data)
  },
  initPreset() {
    return request.post<{ message: string; detail: string }>('/subjects/init-preset')
  },
  delete(id: number) {
    return request.delete(`/subjects/${id}`)
  },
}
