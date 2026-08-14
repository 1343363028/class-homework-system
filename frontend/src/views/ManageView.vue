<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import dayjs from 'dayjs'
import AppNavbar from '@/components/AppNavbar.vue'
import CountdownFloat from '@/components/CountdownFloat.vue'
import { homeworkApi } from '@/api/homework'
import { useSubjectStore } from '@/stores/subject'
import type { Homework, DuePeriod } from '@/types'

const subjectStore = useSubjectStore()
const homeworks = ref<Homework[]>([])
const loading = ref(false)
const showForm = ref(false)
const editingId = ref<number | null>(null)

const form = reactive({
  subject_id: 0,
  title: '',
  content: '',
  assigned_date: dayjs().format('YYYY-MM-DD'),
  due_date: dayjs().add(7, 'day').format('YYYY-MM-DD'),
  due_period: 'evening' as DuePeriod,
})

async function load() {
  loading.value = true
  try {
    const res = await homeworkApi.list()
    homeworks.value = res.data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.subject_id = subjectStore.subjects[0]?.id || 0
  form.title = ''
  form.content = ''
  form.assigned_date = dayjs().format('YYYY-MM-DD')
  form.due_date = dayjs().add(7, 'day').format('YYYY-MM-DD')
  form.due_period = 'evening'
  showForm.value = true
}

function openEdit(hw: Homework) {
  editingId.value = hw.id
  form.subject_id = hw.subject_id
  form.title = hw.title
  form.content = hw.content || ''
  form.assigned_date = hw.assigned_date
  form.due_date = hw.due_date
  form.due_period = hw.due_period
  showForm.value = true
}

async function submit() {
  if (!form.subject_id || !form.title) {
    alert('请填写科目和标题')
    return
  }
  if (dayjs(form.due_date).isBefore(dayjs(form.assigned_date))) {
    alert('截止日期不能早于布置日期')
    return
  }
  try {
    if (editingId.value) {
      await homeworkApi.update(editingId.value, { ...form })
    } else {
      await homeworkApi.create({ ...form })
    }
    showForm.value = false
    await load()
  } catch (e: any) {
    alert(e.message || '操作失败')
  }
}

async function remove(id: number) {
  if (!confirm('确定删除该作业？')) return
  try {
    await homeworkApi.delete(id)
    await load()
  } catch (e: any) {
    alert(e.message || '删除失败')
  }
}

function periodText(p: string): string {
  return p === 'noon' ? '中午' : '晚上'
}

onMounted(async () => {
  await subjectStore.load()
  await load()
})
</script>

<template>
  <div>
    <AppNavbar />
    <div class="main-content">
      <div class="page-header">
        <div>
          <h2 class="page-title">作业管理</h2>
          <p class="page-desc">添加、修改、删除作业，设置截止时段</p>
        </div>
        <button class="btn-primary" @click="openCreate">+ 添加作业</button>
      </div>

      <div v-if="loading" class="loading-state"><div class="spinner"></div></div>

      <div v-else-if="homeworks.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <p>暂无作业，点击右上角添加</p>
      </div>

      <div v-else class="hw-table card">
        <div class="table-header">
          <div>科目</div>
          <div>标题</div>
          <div class="col-date">布置日</div>
          <div class="col-date">截止日</div>
          <div class="col-period">时段</div>
          <div class="col-actions">操作</div>
        </div>
        <div v-for="hw in homeworks" :key="hw.id" class="table-row">
          <div>
            <span class="subject-tag" :style="{ background: subjectStore.getColor(hw.subject_id) + '33', color: subjectStore.getColor(hw.subject_id) }">
              {{ subjectStore.getName(hw.subject_id) }}
            </span>
          </div>
          <div class="hw-title-cell">{{ hw.title }}</div>
          <div class="col-date">{{ hw.assigned_date }}</div>
          <div class="col-date">{{ hw.due_date }}</div>
          <div class="col-period">
            <span class="period-tag" :class="hw.due_period">{{ periodText(hw.due_period) }}</span>
          </div>
          <div class="col-actions">
            <button class="btn-icon edit" @click="openEdit(hw)" title="编辑">✏️</button>
            <button class="btn-icon delete" @click="remove(hw.id)" title="删除">🗑️</button>
          </div>
        </div>
      </div>
    </div>

    <CountdownFloat />

    <!-- 表单弹窗 -->
    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="card modal">
        <h3 class="modal-title">{{ editingId ? '编辑作业' : '添加作业' }}</h3>
        <div class="form-group">
          <label class="form-label">科目</label>
          <select v-model="form.subject_id" class="select">
            <option v-for="s in subjectStore.subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">标题</label>
          <input v-model="form.title" class="input" type="text" placeholder="作业标题" />
        </div>
        <div class="form-group">
          <label class="form-label">内容（可选）</label>
          <textarea v-model="form.content" class="textarea" placeholder="作业具体要求..."></textarea>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">布置日期</label>
            <input v-model="form.assigned_date" class="input" type="date" />
          </div>
          <div class="form-group">
            <label class="form-label">截止日期</label>
            <input v-model="form.due_date" class="input" type="date" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">截止时段</label>
          <div class="period-select">
            <button type="button" class="period-option" :class="{ active: form.due_period === 'noon' }" @click="form.due_period = 'noon'">
              ☀️ 中午（12:00）
            </button>
            <button type="button" class="period-option" :class="{ active: form.due_period === 'evening' }" @click="form.due_period = 'evening'">
              🌙 晚上（23:59）
            </button>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showForm = false">取消</button>
          <button class="btn-primary" @click="submit">{{ editingId ? '保存' : '添加' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.main-content { max-width: 1100px; margin: 0 auto; padding: 24px; position: relative; z-index: 1; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.page-title { font-size: 22px; font-weight: 700; color: var(--text-primary); }
.page-desc { font-size: 13px; color: var(--text-tertiary); margin-top: 4px; }
.btn-primary { padding: 10px 20px; background: var(--accent); border: none; border-radius: var(--radius-sm); color: #fff; font-size: 14px; transition: all var(--transition); }
.btn-primary:hover { background: var(--accent-hover); transform: translateY(-1px); }
.btn-secondary { padding: 10px 20px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: var(--radius-sm); color: var(--text-secondary); font-size: 14px; transition: all var(--transition); }
.btn-secondary:hover { background: var(--bg-card-hover); }

.loading-state, .empty-state { text-align: center; padding: 60px 20px; color: var(--text-tertiary); }
.spinner { width: 32px; height: 32px; border: 3px solid rgba(46, 134, 193, 0.2); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty-icon { font-size: 48px; margin-bottom: 12px; }

.hw-table { padding: 0; overflow: hidden; }
.table-header, .table-row {
  display: grid;
  grid-template-columns: 120px 1fr 110px 110px 80px 100px;
  gap: 12px;
  padding: 14px 20px;
  align-items: center;
}
.table-header { background: var(--bg-tertiary); font-size: 12px; color: var(--text-tertiary); font-weight: 600; }
.table-row { border-top: 1px solid var(--border); transition: background var(--transition-fast); }
.table-row:hover { background: var(--bg-card-hover); }
.col-date { font-size: 13px; color: var(--text-secondary); }
.col-period { text-align: center; }
.col-actions { display: flex; gap: 6px; }
.hw-title-cell { font-size: 14px; color: var(--text-primary); }
.subject-tag { font-size: 12px; padding: 3px 8px; border-radius: 4px; font-weight: 500; }
.period-tag { font-size: 11px; padding: 2px 8px; border-radius: 3px; font-weight: 600; }
.period-tag.noon { background: rgba(243, 156, 18, 0.2); color: #F39C12; }
.period-tag.evening { background: rgba(149, 117, 205, 0.2); color: #9575CD; }

.btn-icon { width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 13px; transition: all var(--transition); }
.btn-icon.edit:hover { background: var(--accent); border-color: var(--accent); }
.btn-icon.delete:hover { background: var(--danger); border-color: var(--danger); }

.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 100; padding: 20px; }
.modal { width: 100%; max-width: 500px; padding: 28px; animation: fadeIn 0.2s ease; }
.modal-title { font-size: 18px; font-weight: 600; color: var(--text-primary); margin-bottom: 20px; }
.form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.form-label { font-size: 13px; color: var(--text-secondary); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.period-select { display: flex; gap: 8px; }
.period-option { flex: 1; padding: 10px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: var(--radius-sm); color: var(--text-secondary); font-size: 13px; transition: all var(--transition); }
.period-option:hover { border-color: var(--accent); }
.period-option.active { background: rgba(46, 134, 193, 0.2); border-color: var(--accent); color: var(--accent-hover); }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }

@media (max-width: 768px) {
  .table-header, .table-row { grid-template-columns: 100px 1fr 80px; font-size: 12px; }
  .col-date:nth-child(3), .col-period { display: none; }
  .table-header > div:nth-child(3), .table-header > div:nth-child(5) { display: none; }
}
</style>
