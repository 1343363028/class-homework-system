<template>
  <el-container class="dashboard">
    <el-header class="header">
      <div class="header-left">
        <span class="title">作业登记系统</span>
      </div>
      <div class="header-right">
        <span>{{ user?.name }} (学习委员)</span>
        <el-button link type="primary" @click="handleLogout">退出</el-button>
      </div>
    </el-header>

    <el-main>
      <el-tabs v-model="activeTab">
        <!-- Homework Management -->
        <el-tab-pane label="发布作业" name="publish">
          <el-card>
            <el-form :model="hwForm" label-width="80px">
              <el-form-item label="标题">
                <el-input v-model="hwForm.title" placeholder="请输入作业标题" />
              </el-form-item>
              <el-form-item label="描述">
                <el-input v-model="hwForm.description" type="textarea" :rows="4" placeholder="作业描述" />
              </el-form-item>
              <el-form-item label="截止日期">
                <el-date-picker v-model="hwForm.due_date" type="datetime" placeholder="选择截止日期" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="publishing" @click="handlePublish">发布作业</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-tab-pane>

        <!-- Homework List -->
        <el-tab-pane label="作业列表" name="list">
          <el-table :data="homeworks" stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="title" label="标题" />
            <el-table-column label="提交情况" width="150">
              <template #default="{ row }">
                <el-tag :type="row.submitted_count === row.total_count ? 'success' : 'warning'">
                  {{ row.submitted_count }} / {{ row.total_count }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="截止日期" width="170">
              <template #default="{ row }">
                {{ row.due_date ? formatDate(row.due_date) : '不限期' }}
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="170">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="viewSubmissions(row)">提交状态</el-button>
                <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <!-- Submission Detail Dialog -->
      <el-dialog v-model="dialogVisible" :title="`作业：${selectedHomework?.title} - 提交状态`" width="700px">
        <div style="margin-bottom: 12px; display: flex; gap: 12px">
          <el-button type="primary" :disabled="selectedStudents.length === 0" @click="batchMark">
            标记为已提交 ({{ selectedStudents.length }})
          </el-button>
          <el-button type="info" @click="loadUnsubmitted">只看未交名单</el-button>
          <el-button @click="showAll = true; loadSubmissions()">显示全部</el-button>
        </div>
        <el-table :data="displayStudents" @selection-change="handleSelectionChange" stripe>
          <el-table-column v-if="!showUnsubmittedOnly" type="selection" width="55" />
          <el-table-column prop="student_id" label="学号" width="120" />
          <el-table-column prop="student_name" label="姓名" width="120" />
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.is_submitted" type="success">已交</el-tag>
              <el-tag v-else type="danger">未交</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="提交时间" width="170">
            <template #default="{ row }">
              {{ row.submitted_at ? formatDate(row.submitted_at) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button v-if="row.is_submitted" link type="warning" size="small" @click="handleUndo(row)">撤销</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-dialog>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { getHomeworkList, createHomework, deleteHomework, getHomeworkSubmissions, getUnsubmitted, batchSubmit, undoSubmission } from '../api'

const router = useRouter()
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const activeTab = ref('list')

// Homework list
const homeworks = ref([])
const loading = ref(false)

async function loadHomeworks() {
  loading.value = true
  try {
    homeworks.value = await getHomeworkList()
  } catch (e) {
    ElMessage.error('加载作业列表失败')
  } finally {
    loading.value = false
  }
}

function formatDate(d) {
  return d ? dayjs(d).format('YYYY-MM-DD HH:mm') : ''
}

// Publish homework
const hwForm = ref({ title: '', description: '', due_date: null })
const publishing = ref(false)

async function handlePublish() {
  if (!hwForm.value.title.trim()) {
    ElMessage.warning('请输入作业标题')
    return
  }
  publishing.value = true
  try {
    await createHomework(hwForm.value)
    ElMessage.success('发布成功')
    hwForm.value = { title: '', description: '', due_date: null }
    await loadHomeworks()
  } catch (e) {
    ElMessage.error('发布失败')
  } finally {
    publishing.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除「${row.title}」？`, '提示', { type: 'warning' })
    await deleteHomework(row.id)
    ElMessage.success('已删除')
    await loadHomeworks()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// Submission dialog
const dialogVisible = ref(false)
const selectedHomework = ref(null)
const allStudents = ref([])
const selectedStudents = ref([])
const showUnsubmittedOnly = ref(false)
const showAll = ref(true)

const displayStudents = computed(() => {
  if (showUnsubmittedOnly.value) {
    return allStudents.value.filter((s) => !s.is_submitted)
  }
  return allStudents.value
})

function handleSelectionChange(val) {
  selectedStudents.value = val
}

async function viewSubmissions(hw) {
  selectedHomework.value = hw
  dialogVisible.value = true
  showUnsubmittedOnly.value = false
  showAll.value = true
  await loadSubmissions()
}

async function loadSubmissions() {
  try {
    allStudents.value = await getHomeworkSubmissions(selectedHomework.value.id)
  } catch (e) {
    ElMessage.error('加载提交状态失败')
  }
}

async function loadUnsubmitted() {
  try {
    const data = await getUnsubmitted(selectedHomework.value.id)
    allStudents.value = data.map((d) => ({
      ...d,
      student_name: d.name,
      student_id: d.student_id,
      is_submitted: false,
    }))
    showUnsubmittedOnly.value = true
  } catch (e) {
    ElMessage.error('加载失败')
  }
}

async function batchMark() {
  if (selectedStudents.value.length === 0) return
  try {
    await batchSubmit({
      homework_id: selectedHomework.value.id,
      user_ids: selectedStudents.value.map((s) => s.user_id),
      status: 'submitted',
    })
    ElMessage.success(`已登记 ${selectedStudents.value.length} 名同学`)
    await loadSubmissions()
    await loadHomeworks()
    selectedStudents.value = []
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function handleUndo(row) {
  try {
    await ElMessageBox.confirm(`确认撤销 ${row.student_name} 的提交记录？`, '提示', { type: 'warning' })
    await undoSubmission(row.id)
    ElMessage.success('已撤销')
    await loadSubmissions()
    await loadHomeworks()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
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
