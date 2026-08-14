// 路由配置与权限拦截
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { title: '登录', public: true } },
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue'), meta: { title: '作业日历' } },
  { path: '/homework/:date', name: 'homework-by-date', component: () => import('@/views/HomeworkListView.vue'), meta: { title: '当日作业' } },
  { path: '/manage', name: 'manage', component: () => import('@/views/ManageView.vue'), meta: { title: '作业管理', requireCommissary: true } },
  { path: '/subjects', name: 'subjects', component: () => import('@/views/SubjectManageView.vue'), meta: { title: '科目管理', requireCommissary: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  document.title = `${to.meta.title || ''} - 班级作业查询系统`
  if (to.meta.public) {
    if (auth.isLoggedIn && to.name === 'login') next({ name: 'home' })
    else next()
    return
  }
  if (!auth.isLoggedIn) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  if (to.meta.requireCommissary && !auth.isCommissary) {
    next({ name: 'home' })
    return
  }
  next()
})

export default router
