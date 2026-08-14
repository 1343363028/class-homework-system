<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push('/login')
}

const navItems = computed(() => {
  const items = [
    { name: 'home', label: '日历主页', icon: '📅' },
    { name: 'homework-by-date', label: '当日作业', icon: '📋' },
  ]
  if (auth.isCommissary) {
    items.push({ name: 'manage', label: '作业管理', icon: '✏️' })
    items.push({ name: 'subjects', label: '科目管理', icon: '🎨' })
  }
  return items
})
</script>

<template>
  <header class="navbar">
    <div class="nav-inner">
      <div class="nav-brand" @click="router.push('/')">
        <span class="brand-icon">
          <svg width="22" height="22" viewBox="0 0 32 32" fill="none">
            <rect x="6" y="8" width="20" height="18" rx="2" stroke="#2E86C1" stroke-width="2"/>
            <line x1="6" y1="13" x2="26" y2="13" stroke="#2E86C1" stroke-width="2"/>
            <circle cx="16" cy="19" r="2" fill="#529286"/>
          </svg>
        </span>
        <span class="brand-text">班级作业查询系统</span>
      </div>

      <nav class="nav-menu">
        <router-link
          v-for="item in navItems"
          :key="item.name"
          :to="item.name === 'homework-by-date' ? { name: item.name, params: { date: 'today' } } : { name: item.name }"
          class="nav-item"
          active-class="active"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="nav-user">
        <div class="user-info">
          <span class="user-name">{{ auth.displayName }}</span>
          <span class="user-role" :class="{ commissary: auth.isCommissary }">
            {{ auth.isCommissary ? '学委' : '学生' }}
          </span>
        </div>
        <button class="logout-btn" @click="logout" aria-label="退出登录" title="退出登录">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}
.nav-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 24px;
}
.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  flex-shrink: 0;
}
.brand-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}
.nav-menu {
  display: flex;
  gap: 4px;
  flex: 1;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  transition: all var(--transition);
}
.nav-item:hover { color: var(--text-primary); background: var(--bg-card-hover); }
.nav-item.active { color: var(--accent-hover); background: rgba(46, 134, 193, 0.15); box-shadow: inset 0 -2px 0 var(--accent); }
.nav-icon { font-size: 14px; }
.nav-user { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
.user-info { display: flex; align-items: center; gap: 8px; }
.user-name { font-size: 13px; color: var(--text-primary); font-weight: 500; }
.user-role { font-size: 11px; padding: 2px 8px; border-radius: 10px; background: rgba(82, 146, 134, 0.2); color: var(--accent-light); }
.user-role.commissary { background: rgba(46, 134, 193, 0.2); color: var(--accent-hover); }
.logout-btn {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  transition: all var(--transition);
}
.logout-btn:hover { background: var(--danger); color: #fff; border-color: var(--danger); }

@media (max-width: 768px) {
  .nav-inner { padding: 0 12px; gap: 8px; }
  .brand-text { display: none; }
  .nav-label { display: none; }
  .nav-item { padding: 8px 10px; }
  .user-name { display: none; }
}
</style>
