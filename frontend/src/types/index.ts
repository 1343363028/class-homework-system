// 类型定义
export type Role = 'student' | 'commissary'
export type DuePeriod = 'noon' | 'evening'

export interface User {
  id: number
  student_id: string
  name: string
  role: Role
  class_id: number
}

export interface TokenResponse {
  access_token: string
  token_type: string
  role: Role
  name: string
  student_id: string
}

export interface Subject {
  id: number
  class_id: number
  name: string
  color: string
  icon: string
}

export interface Homework {
  id: number
  class_id: number
  subject_id: number
  title: string
  content: string | null
  assigned_date: string
  due_date: string
  due_period: DuePeriod
  created_by: number
  created_at: string
  updated_at: string
  subject?: Subject
}

export interface CountdownItem {
  homework_id: number
  title: string
  subject_name: string
  subject_color: string
  due_date: string
  due_period: DuePeriod
  days_left: number
  is_overdue: boolean
}

export interface HomeworkCreate {
  subject_id: number
  title: string
  content?: string
  assigned_date: string
  due_date: string
  due_period: DuePeriod
}

export interface HomeworkUpdate {
  subject_id?: number
  title?: string
  content?: string
  assigned_date?: string
  due_date?: string
  due_period?: DuePeriod
}

export interface SubjectUpdate {
  name?: string
  color?: string
  icon?: string
}
