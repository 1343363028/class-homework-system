<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="login-title">作业登记系统</h2>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="登录" name="login" />
        <el-tab-pane label="注册" name="register" />
      </el-tabs>

      <!-- Login Form -->
      <el-form v-if="activeTab === 'login'" :model="loginForm" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="loginForm.student_id" placeholder="学号" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="handleLogin">登录</el-button>
      </el-form>

      <!-- Register Form -->
      <el-form v-if="activeTab === 'register'" :model="registerForm" @submit.prevent="handleRegister">
        <el-form-item label="姓名">
          <el-input v-model="registerForm.name" placeholder="请输入姓名" size="large" />
        </el-form-item>
        <el-form-item label="学号">
          <el-input v-model="registerForm.student_id" placeholder="请输入学号" size="large" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="registerForm.password" type="password" placeholder="设置密码" size="large" show-password />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="registerForm.role">
            <el-radio value="student">学生</el-radio>
            <el-radio value="committee">学习委员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="handleRegister">注册</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, register } from '../api'

const router = useRouter()
const activeTab = ref('login')
const loading = ref(false)

const loginForm = ref({ student_id: '', password: '' })
const registerForm = ref({ student_id: '', name: '', password: '', role: 'student' })

async function handleLogin() {
  if (!loginForm.value.student_id || !loginForm.value.password) {
    ElMessage.warning('请输入学号和密码')
    return
  }
  loading.value = true
  try {
    const res = await login(loginForm.value.student_id, loginForm.value.password)
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    ElMessage.success('登录成功')
    if (res.user.role === 'committee') {
      router.push('/committee')
    } else {
      router.push('/student')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!registerForm.value.student_id || !registerForm.value.name || !registerForm.value.password) {
    ElMessage.warning('请填写完整信息')
    return
  }
  loading.value = true
  try {
    await register(registerForm.value)
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 420px;
  padding: 20px;
}
.login-title {
  text-align: center;
  margin-bottom: 24px;
  color: #333;
}
</style>
