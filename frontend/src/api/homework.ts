// 作业相关 API
import request from './request'
import type { Homework, HomeworkCreate, HomeworkUpdate, CountdownItem } from '@/types'

export const homeworkApi = {
  list(startDate?: string, endDate?: string) {
    return request.get<Homework[]>('/homeworks', {
      params: { start_date: startDate, end_date: endDate },
    })
  },
  getByDate(date: string) {
    return request.get<{ date: string; homeworks: Homework[] }>(`/homeworks/by-date/${date}`)
  },
  countdown() {
    return request.get<{ items: CountdownItem[] }>('/homeworks/countdown')
  },
  create(data: HomeworkCreate) {
    return request.post<Homework>('/homeworks', data)
  },
  update(id: number, data: HomeworkUpdate) {
    return request.put<Homework>(`/homeworks/${id}`, data)
  },
  delete(id: number) {
    return request.delete(`/homeworks/${id}`)
  },
}
