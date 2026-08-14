<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import CalendarView from '@/components/CalendarView.vue'
import CountdownFloat from '@/components/CountdownFloat.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import { homeworkApi } from '@/api/homework'
import { useSubjectStore } from '@/stores/subject'
import type { Homework } from '@/types'

const router = useRouter()
const subjectStore = useSubjectStore()

const homeworks = ref<Homework[]>([])
const selectedDate = ref(dayjs().format('YYYY-MM-DD'))
const loading = ref(false)
const countdownRef = ref<InstanceType<typeof CountdownFloat> | null>(null)

async function loadHomeworks() {
  loading.value = true
  try {
    const start = dayjs(selectedDate.value).subtract(1, 'month').format('YYYY-MM-DD')
    const end = dayjs(selectedDate.value).add(1, 'month').format('YYYY-MM-DD')
    const res = await homeworkApi.list(start, end)
    homeworks.value = res.data
  } finally {
    loading.value = false
  }
}

function onSelectDate(date: string) {
  selectedDate.value = date
  router.push({ name: 'homework-by-date', params: { date } })
}

function prevMonth() {
  selectedDate.value = dayjs(selectedDate.value).subtract(1, 'month').format('YYYY-MM-DD')
}
function nextMonth() {
  selectedDate.value = dayjs(selectedDate.value).add(1, 'month').format('YYYY-MM-DD')
}

watch(selectedDate, loadHomeworks)

onMounted(async () => {
  await subjectStore.load()
  await loadHomeworks()
})

const todayCount = computed(() => {
  const today = dayjs().format('YYYY-MM-DD')
  return homeworks.value.filter((h) => h.assigned_date === today || h.due_date === today).length
})
const pendingCount = computed(() => {
  const today = dayjs()
  return homeworks.value.filter((h) => dayjs(h.due_date).isAfter(today)).length
})
const overdueCount = computed(() => {
  const today = dayjs().startOf('day')
  return homeworks.value.filter((h) => dayjs(h.due_date).isBefore(today)).length
})

import { computed } from 'vue'
</script>

<template>
  <div>
    <AppNavbar />
    <div class="main-content">
      <div class="page-header">
        <div>
          <h2 class="page-title">作业日历</h2>
          <p class="page-desc">点击日期查看当日作业，布置日与截止日均有标注</p>
        </div>
        <div class="legend">
          <div class="legend-item"><span class="legend-dot assigned"></span>布置日</div>
          <div class="legend-item"><span class="legend-dot due"></span>截止日</div>
          <div class="legend-item"><span class="legend-dot today"></span>今天</div>
        </div>
      </div>

      <div class="quick-stats">
        <div class="card stat-card">
          <div class="stat-value">{{ todayCount }}</div>
          <div class="stat-label">今日相关</div>
        </div>
        <div class="card stat-card">
          <div class="stat-value">{{ pendingCount }}</div>
          <div class="stat-label">待完成</div>
        </div>
        <div class="card stat-card">
          <div class="stat-value">{{ overdueCount }}</div>
          <div class="stat-label">已截止</div>
        </div>
      </div>

      <div class="card calendar-wrapper">
        <div v-if="loading" class="loading-overlay">
          <div class="spinner"></div>
        </div>
        <CalendarView
          :homeworks="homeworks"
          :selected-date="selectedDate"
          @select-date="onSelectDate"
          @prev-month="prevMonth"
          @next-month="nextMonth"
        />
      </div>
    </div>

    <CountdownFloat ref="countdownRef" />
  </div>
</template>

<style scoped>
.main-content { max-width: 1200px; margin: 0 auto; padding: 24px; position: relative; z-index: 1; }
.page-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.page-title { font-size: 22px; font-weight: 700; color: var(--text-primary); }
.page-desc { font-size: 13px; color: var(--text-tertiary); margin-top: 4px; }
.legend { display: flex; gap: 16px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-secondary); }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }
.legend-dot.assigned { background: var(--accent-light); }
.legend-dot.due { background: var(--danger); }
.legend-dot.today { background: var(--accent); box-shadow: 0 0 8px var(--accent-glow); }
.calendar-wrapper { position: relative; padding: 24px; margin-bottom: 24px; }
.loading-overlay { position: absolute; inset: 0; background: rgba(11, 28, 44, 0.6); display: flex; align-items: center; justify-content: center; z-index: 10; border-radius: var(--radius-md); }
.spinner { width: 32px; height: 32px; border: 3px solid rgba(46, 134, 193, 0.2); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.quick-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { text-align: center; padding: 24px; }
.stat-value { font-size: 28px; font-weight: 700; color: var(--accent-hover); margin-bottom: 4px; }
.stat-label { font-size: 12px; color: var(--text-tertiary); }
@media (max-width: 768px) { .main-content { padding: 12px; } .quick-stats { grid-template-columns: 1fr; } }
</style>
