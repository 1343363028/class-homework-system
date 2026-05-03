import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import CommitteeDashboard from '../views/CommitteeDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/committee', name: 'Committee', component: CommitteeDashboard },
  { path: '/student', name: 'Student', component: StudentDashboard },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if ((to.name === 'Committee' || to.name === 'Student') && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
