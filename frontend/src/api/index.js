import api from './http'

export function login(student_id, password) {
  return api.post('/auth/login', { student_id, password })
}

export function register(data) {
  return api.post('/auth/register', data)
}

export function getMe() {
  return api.get('/auth/me')
}

export function getHomeworkList(includeStatus = false) {
  return api.get('/homework/', { params: { include_status: includeStatus } })
}

export function createHomework(data) {
  return api.post('/homework/', data)
}

export function deleteHomework(id) {
  return api.delete(`/homework/${id}`)
}

export function getHomeworkSubmissions(homeworkId) {
  return api.get(`/homework/${homeworkId}/submissions`)
}

export function getUnsubmitted(homeworkId) {
  return api.get(`/homework/${homeworkId}/unsubmitted`)
}

export function batchSubmit(data) {
  return api.post('/submission/batch', data)
}

export function undoSubmission(id) {
  return api.delete(`/submission/${id}`)
}

export function studentSubmit(homeworkId) {
  return api.post(`/submission/student/submit/${homeworkId}`)
}

export function listStudents(role) {
  return api.get('/users/', { params: { role } })
}
