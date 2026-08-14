<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSubjectStore } from '@/stores/subject'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const subjectStore = useSubjectStore()

type RoleChoice = 'student' | 'commissary'
const selectedRole = ref<RoleChoice>('student')

const form = reactive({
  student_id: '',
  password: '',
})
const loading = ref(false)
const errorMsg = ref('')

// 学委账号列表（用于前端提示）
const commissaryIds = ['U202512649', 'U202512660', 'U202512670', 'U202512676']

const needPassword = computed(() => selectedRole.value === 'commissary')

async function handleLogin() {
  if (!form.student_id) {
    errorMsg.value = '请输入学号'
    return
  }
  // 学号格式校验
  const sid = form.student_id.trim().toUpperCase()
  if (!/^U2025126\d{2}$/.test(sid)) {
    errorMsg.value = '学号格式应为 U2025126XX'
    return
  }
  const num = parseInt(sid.slice(-2))
  if (num < 47 || num > 80) {
    errorMsg.value = '学号不在允许范围内（U202512647 ~ U202512680）'
    return
  }
  if (needPassword.value && !form.password) {
    errorMsg.value = '学委登录需要输入密码'
    return
  }
  // 角色与学号一致性校验
  const isCommissaryId = commissaryIds.includes(sid)
  if (selectedRole.value === 'commissary' && !isCommissaryId) {
    errorMsg.value = '该学号不是学委账号'
    return
  }
  if (selectedRole.value === 'student' && isCommissaryId) {
    errorMsg.value = '该学号是学委账号，请选择学委登录'
    return
  }

  loading.value = true
  errorMsg.value = ''
  try {
    await auth.login(sid, needPassword.value ? form.password : undefined)
    await subjectStore.load()
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (e: any) {
    errorMsg.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-grid"></div>
      <div class="bg-glow glow-1"></div>
      <div class="bg-glow glow-2"></div>
    </div>

    <div class="login-card">
      <div class="login-header">
        <div class="logo">
          <svg width="40" height="40" viewBox="0 0 32 32" fill="none">
            <rect x="6" y="8" width="20" height="18" rx="2" stroke="#2E86C1" stroke-width="2"/>
            <line x1="6" y1="13" x2="26" y2="13" stroke="#2E86C1" stroke-width="2"/>
            <line x1="11" y1="6" x2="11" y2="10" stroke="#529286" stroke-width="2" stroke-linecap="round"/>
            <line x1="21" y1="6" x2="21" y2="10" stroke="#529286" stroke-width="2" stroke-linecap="round"/>
            <circle cx="16" cy="19" r="2" fill="#2E86C1"/>
          </svg>
        </div>
        <h1 class="login-title">班级作业查询系统</h1>
        <p class="login-subtitle">Homework Query System</p>
      </div>

      <!-- 角色选择 -->
      <div class="role-select">
        <button
          class="role-btn"
          :class="{ active: selectedRole === 'student' }"
          @click="selectedRole = 'student'; errorMsg = ''"
        >
          <span class="role-icon">🎓</span>
          <span class="role-name">学生登录</span>
          <span class="role-desc">免密登录</span>
        </button>
        <button
          class="role-btn"
          :class="{ active: selectedRole === 'commissary' }"
          @click="selectedRole = 'commissary'; errorMsg = ''"
        >
          <span class="role-icon">📋</span>
          <span class="role-name">学委登录</span>
          <span class="role-desc">需密码</span>
        </button>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">学号</label>
          <input
            v-model="form.student_id"
            class="input"
            type="text"
            placeholder="U202512647 ~ U202512680"
            autocomplete="off"
          />
        </div>

        <div v-if="needPassword" class="form-group">
          <label class="form-label">密码</label>
          <input
            v-model="form.password"
            class="input"
            type="password"
            placeholder="请输入密码"
            autocomplete="off"
          />
        </div>

        <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

        <button class="login-btn" :disabled="loading" type="submit">
          <span v-if="loading" class="spinner"></span>
          <span>{{ loading ? '登录中...' : '登 录' }}</span>
        </button>
      </form>

      <div class="login-hint">
        <p v-if="selectedRole === 'student'">学生账号直接输入学号即可登录，无需密码</p>
        <p v-else>学委账号：U202512649 / U202512660 / U202512670 / U202512676</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}
.login-bg { position: absolute; inset: 0; z-index: 0; }
.bg-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(46, 134, 193, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(46, 134, 193, 0.06) 1px, transparent 1px);
  background-size: 50px 50px;
}
.bg-glow { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.4; }
.glow-1 { width: 400px; height: 400px; background: var(--accent); top: -100px; left: -100px; }
.glow-2 { width: 300px; height: 300px; background: var(--accent-light); bottom: -50px; right: -50px; }

.login-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  padding: 40px 36px;
  background: rgba(15, 34, 51, 0.85);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(20px);
  box-shadow: var(--shadow-md), 0 0 40px rgba(46, 134, 193, 0.1);
  animation: fadeIn 0.4s ease;
}

.login-header { text-align: center; margin-bottom: 28px; }
.logo { display: flex; justify-content: center; margin-bottom: 16px; }
.login-title { font-size: 22px; font-weight: 700; color: var(--text-primary); letter-spacing: 1px; }
.login-subtitle { font-size: 11px; color: var(--text-tertiary); letter-spacing: 2px; margin-top: 4px; }

.role-select { display: flex; gap: 12px; margin-bottom: 24px; }
.role-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 14px 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  transition: all var(--transition);
}
.role-btn:hover { border-color: var(--accent); background: var(--bg-card-hover); }
.role-btn.active {
  background: linear-gradient(135deg, rgba(46, 134, 193, 0.25), rgba(82, 146, 134, 0.15));
  border-color: var(--accent);
  box-shadow: 0 0 12px var(--accent-glow);
}
.role-icon { font-size: 22px; }
.role-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.role-desc { font-size: 10px; color: var(--text-tertiary); }
.role-btn.active .role-name { color: var(--accent-hover); }

.login-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 13px; color: var(--text-secondary); }

.error-msg {
  padding: 10px 14px;
  background: rgba(231, 76, 60, 0.1);
  border: 1px solid rgba(231, 76, 60, 0.3);
  border-radius: var(--radius-sm);
  color: var(--danger);
  font-size: 13px;
  animation: fadeIn 0.2s ease;
}

.login-btn {
  margin-top: 8px;
  padding: 12px;
  background: linear-gradient(135deg, var(--accent), var(--accent-light));
  border: none;
  border-radius: var(--radius-sm);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 4px;
  transition: all var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.login-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 24px var(--accent-glow); }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.login-hint {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px dashed var(--border);
  text-align: center;
  font-size: 12px;
  color: var(--text-tertiary);
  line-height: 1.6;
}
</style>
