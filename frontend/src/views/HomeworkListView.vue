<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dayjs from 'dayjs'
import AppNavbar from '@/components/AppNavbar.vue'
import CountdownFloat from '@/components/CountdownFloat.vue'
import { homeworkApi } from '@/api/homework'
import { useSubjectStore } from '@/stores/subject'
import type { Homework } from '@/types'

const route = useRoute()
const router = useRouter()
const subjectStore = useSubjectStore()

const homeworks = ref<Homework[]>([])
const loading = ref(false)

const queryDate = ref<string>(
  route.params.date === 'today' || !route.params.date
    ? dayjs().format('YYYY-MM-DD')
    : (route.params.date as string)
)

async function load() {
  loading.value = true
  try {
    const res = await homeworkApi.getByDate(queryDate.value)
    homeworks.value = res.data.homeworks
  } catch {
    homeworks.value = []
  } finally {
    loading.value = false
  }
}

function daysLeft(hw: Homework): number {
  return dayjs(hw.due_date).diff(dayjs().startOf('day'), 'day')
}

function isOverdue(hw: Homework): boolean {
  return dayjs(hw.due_date).isBefore(dayjs().startOf('day'))
}

function periodText(period: string): string {
  return period === 'noon' ? '中午' : '晚上'
}

function countdownText(hw: Homework): string {
  if (isOverdue(hw)) return '已截止'
  const d = daysLeft(hw)
  if (d === 0) return '今日截止'
  return `还剩 ${d} 天`
}

function countdownClass(hw: Homework): string {
  if (isOverdue(hw)) return 'overdue'
  const d = daysLeft(hw)
  if (d === 0) return 'due-today'
  if (d <= 1) return 'urgent'
  return ''
}

function goPrev() {
  const d = dayjs(queryDate.value).subtract(1, 'day').format('YYYY-MM-DD')
  router.push({ name: 'homework-by-date', params: { date: d } })
}
function goNext() {
  const d = dayjs(queryDate.value).add(1, 'day').format('YYYY-MM-DD')
  router.push({ name: 'homework-by-date', params: { date: d } })
}
function goToday() {
  router.push({ name: 'homework-by-date', params: { date: dayjs().format('YYYY-MM-DD') } })
}

function isAssignedDay(hw: Homework): boolean {
  return hw.assigned_date === queryDate.value
}

watch(() => route.params.date, (newDate) => {
  if (newDate && newDate !== 'today') {
    queryDate.value = newDate as string
    load()
  } else if (newDate === 'today') {
    queryDate.value = dayjs().format('YYYY-MM-DD')
    load()
  }
})

onMounted(async () => {
  await subjectStore.load()
  await load()
})
</script>

<template>
  <div>
    <AppNavbar />
    <div class="main-content">
      <div class="date-nav">
        <button class="nav-btn" @click="goPrev">‹ 前一天</button>
        <div class="date-display">
          <div class="date-text">{{ queryDate }}</div>
          <div class="date-weekday">{{ dayjs(queryDate).format('dddd') }}</div>
        </div>
        <button class="nav-btn" @click="goNext">后一天 ›</button>
        <button class="today-btn" @click="goToday">今天</button>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="homeworks.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <p>该日期暂无作业</p>
      </div>

      <div v-else class="hw-list">
        <div
          v-for="hw in homeworks"
          :key="hw.id"
          class="hw-card"
          :style="{ '--subject-color': subjectStore.getColor(hw.subject_id) }"
        >
          <div class="hw-subject-bar"></div>
          <div class="hw-content">
            <div class="hw-header">
              <span
                class="hw-subject-tag"
                :style="{ background: subjectStore.getColor(hw.subject_id) + '33', color: subjectStore.getColor(hw.subject_id) }"
              >
                {{ subjectStore.getName(hw.subject_id) }}
              </span>
              <span class="hw-type" :class="isAssignedDay(hw) ? 'assigned' : 'due'">
                {{ isAssignedDay(hw) ? '布置日' : '截止日' }}
              </span>
            </div>
            <div class="hw-title">{{ hw.title }}</div>
            <div v-if="hw.content" class="hw-content-text">{{ hw.content }}</div>
            <div class="hw-footer">
              <div class="hw-date">
                <span>布置：{{ hw.assigned_date }}</span>
                <span class="sep">→</span>
                <span>截止：{{ hw.due_date }} {{ periodText(hw.due_period) }}</span>
              </div>
              <div class="hw-countdown" :class="countdownClass(hw)">
                {{ countdownText(hw) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <CountdownFloat />
  </div>
</template>

<style scoped>
.main-content { max-width: 900px; margin: 0 auto; padding: 24px; position: relative; z-index: 1; }
.date-nav { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
.nav-btn { padding: 8px 16px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: var(--radius-sm); color: var(--text-secondary); font-size: 14px; transition: all var(--transition); }
.nav-btn:hover { background: var(--accent); color: #fff; border-color: var(--accent); }
.date-display { flex: 1; text-align: center; }
.date-text { font-size: 18px; font-weight: 600; color: var(--text-primary); }
.date-weekday { font-size: 12px; color: var(--text-tertiary); margin-top: 2px; }
.today-btn { padding: 8px 16px; background: var(--accent); border: none; border-radius: var(--radius-sm); color: #fff; font-size: 13px; transition: all var(--transition); }
.today-btn:hover { background: var(--accent-hover); }

.loading-state, .empty-state { text-align: center; padding: 60px 20px; color: var(--text-tertiary); }
.spinner { width: 32px; height: 32px; border: 3px solid rgba(46, 134, 193, 0.2); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 12px; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty-icon { font-size: 48px; margin-bottom: 12px; }

.hw-list { display: flex; flex-direction: column; gap: 12px; }
.hw-card { display: flex; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); overflow: hidden; transition: all var(--transition); animation: slideIn 0.3s ease; }
.hw-card:hover { border-color: var(--border-strong); transform: translateX(4px); }
@keyframes slideIn { from { opacity: 0; transform: translateX(-12px); } to { opacity: 1; transform: translateX(0); } }
.hw-subject-bar { width: 4px; background: var(--subject-color); flex-shrink: 0; }
.hw-content { flex: 1; padding: 16px 20px; }
.hw-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.hw-subject-tag { font-size: 12px; padding: 2px 8px; border-radius: 4px; font-weight: 500; }
.hw-type { font-size: 11px; padding: 2px 6px; border-radius: 3px; font-weight: 600; }
.hw-type.assigned { background: rgba(82, 146, 134, 0.2); color: var(--accent-light); }
.hw-type.due { background: rgba(231, 76, 60, 0.2); color: var(--danger); }
.hw-title { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px; }
.hw-content-text { font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 10px; white-space: pre-wrap; }
.hw-footer { display: flex; align-items: center; justify-content: space-between; font-size: 12px; color: var(--text-tertiary); }
.hw-date { display: flex; align-items: center; gap: 4px; }
.hw-date .sep { margin: 0 4px; opacity: 0.5; }
.hw-countdown { color: var(--accent-hover); font-weight: 500; }
.hw-countdown.urgent { color: var(--danger); }
.hw-countdown.due-today { color: var(--warning); font-weight: 600; }
.hw-countdown.overdue { color: var(--text-tertiary); }

@media (max-width: 640px) { .main-content { padding: 12px; } .date-display { min-width: 140px; } .date-text { font-size: 15px; } }
</style>
