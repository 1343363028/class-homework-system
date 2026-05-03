<template>
  <el-container class="dashboard">
    <el-header class="header">
      <div class="header-left">
        <span class="title">作业登记系统</span>
      </div>
      <div class="header-right">
        <span>{{ user?.name }}</span>
        <el-button link type="primary" @click="handleLogout">退出</el-button>
      </div>
    </el-header>

    <el-main>
      <h3 style="margin-bottom: 16px">我的作业</h3>
      <el-table :data="homeworks" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" />
        <el-table-column label="描述" min-width="200">
          <template #default="{ row }">
            <el-text type="info">{{ row.description || '暂无' }}</el-text>
          </template>
        </el-table-column>
        <el-table-column label="截止日期" width="160">
          <template #default="{ row }">
            {{ row.due_date ? formatDate(row.due_date) : '不限期' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.submitted_count > 0" type="success">已交</el-tag>
            <el-tag v-else type="danger">未交</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.submitted_count === 0" link type="primary" size="small" @click="handleSubmit(row)">提交</el-button>
            <el-text v-else type="success" size="small">已提交</el-text>
          </template>
        </el-table-column>
      </el-table>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { getHomeworkList, studentSubmit } from '../api'

const router = useRouter()
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const homeworks = ref([])

function formatDate(d) {
  return d ? dayjs(d).format('YYYY-MM-DD HH:mm') : ''
}

async function loadHomeworks() {
  try {
    homeworks.value = await getHomeworkList(true)
  } catch (e) {
    ElMessage.error('加载作业列表失败')
  }
}

async function handleSubmit(hw) {
  try {
    await ElMessageBox.confirm(`确认提交「${hw.title}」？`, '确认提交', { type: 'info' })
    await studentSubmit(hw.id)
    ElMessage.success('提交成功')
    await loadHomeworks()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '提交失败')
    }
  }
}

function handleLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}

onMounted(loadHomeworks)
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f7fa;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.title {
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
