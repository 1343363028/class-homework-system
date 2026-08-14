<script setup lang="ts">
import { ref, computed } from 'vue'
import dayjs from 'dayjs'
import type { Homework } from '@/types'
import { useSubjectStore } from '@/stores/subject'

const props = defineProps<{ homeworks: Homework[]; selectedDate: string }>()
const emit = defineEmits<{
  (e: 'select-date', date: string): void
  (e: 'prev-month'): void
  (e: 'next-month'): void
}>()

const subjectStore = useSubjectStore()
const currentMonth = ref(dayjs(props.selectedDate || undefined))
const weekDays = ['一', '二', '三', '四', '五', '六', '日']
const today = computed(() => dayjs().format('YYYY-MM-DD'))

const calendarDays = computed(() => {
  const start = currentMonth.value.startOf('month')
  const end = currentMonth.value.endOf('month')
  let startWeekday = start.day() - 1
  if (startWeekday < 0) startWeekday = 6
  const days: any[] = []
  for (let i = startWeekday - 1; i >= 0; i--) days.push(buildDay(start.subtract(i + 1, 'day'), false))
  for (let i = 0; i < end.date(); i++) days.push(buildDay(start.add(i, 'day'), true))
  while (days.length < 42) days.push(buildDay(start.add(days.length - startWeekday, 'day'), false))
  return days
})

function buildDay(d: dayjs.Dayjs, inMonth: boolean) {
  const dateStr = d.format('YYYY-MM-DD')
  const dayHomeworks = props.homeworks.filter(
    (h) => h.assigned_date === dateStr || h.due_date === dateStr
  )
  return {
    date: dateStr,
    day: d.date(),
    inMonth,
    isToday: dateStr === today.value,
    isPast: d.isBefore(dayjs().startOf('day')),
    isAssigned: dayHomeworks.some((h) => h.assigned_date === dateStr),
    isDue: dayHomeworks.some((h) => h.due_date === dateStr),
    isSelected: dateStr === props.selectedDate,
    homeworks: dayHomeworks,
  }
}

function selectDay(date: string) {
  emit('select-date', date)
}

function prevMonth() {
  currentMonth.value = currentMonth.value.subtract(1, 'month')
  emit('prev-month')
}
function nextMonth() {
  currentMonth.value = currentMonth.value.add(1, 'month')
  emit('next-month')
}

function subjectColor(id: number) {
  return subjectStore.getColor(id)
}
</script>

<template>
  <div class="calendar">
    <div class="cal-header">
      <button class="cal-nav-btn" @click="prevMonth" aria-label="上一月">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <div class="cal-title">{{ currentMonth.format('YYYY 年 M 月') }}</div>
      <button class="cal-nav-btn" @click="nextMonth" aria-label="下一月">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <div class="cal-weekdays">
      <div v-for="w in weekDays" :key="w" class="cal-weekday">{{ w }}</div>
    </div>

    <div class="cal-grid">
      <div
        v-for="d in calendarDays"
        :key="d.date"
        class="cal-day"
        :class="{
          'out-month': !d.inMonth,
          'is-past': d.isPast && d.inMonth,
          'is-today': d.isToday,
          'is-selected': d.isSelected,
        }"
        @click="selectDay(d.date)"
      >
        <span class="day-num">{{ d.day }}</span>
        <span v-if="d.isAssigned" class="badge badge-assigned">布</span>
        <span v-if="d.isDue" class="badge badge-due">止</span>
        <div class="day-marks">
          <span
            v-for="h in d.homeworks.slice(0, 4)"
            :key="h.id"
            class="mark-dot"
            :style="{ background: subjectColor(h.subject_id) }"
          ></span>
          <span v-if="d.homeworks.length > 4" class="mark-more">+{{ d.homeworks.length - 4 }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calendar { width: 100%; }
.cal-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 16px;
}
.cal-nav-btn {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  transition: all var(--transition);
}
.cal-nav-btn:hover { background: var(--accent); color: #fff; border-color: var(--accent); }
.cal-title { font-size: 18px; font-weight: 600; color: var(--text-primary); letter-spacing: 1px; }

.cal-weekdays { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 8px; }
.cal-weekday {
  text-align: center; font-size: 12px; color: var(--text-tertiary);
  padding: 8px 0; font-weight: 500;
}

.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }
.cal-day {
  position: relative;
  min-height: 88px;
  padding: 6px 8px;
  background: var(--bg-secondary);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition);
  display: flex; flex-direction: column;
}
.cal-day:hover { background: var(--bg-card-hover); border-color: var(--accent); transform: translateY(-2px); box-shadow: var(--shadow-md); }
.cal-day.out-month { opacity: 0.3; }
.cal-day.is-past { opacity: 0.45; }
.cal-day.is-today {
  background: linear-gradient(135deg, rgba(46, 134, 193, 0.25), rgba(82, 146, 134, 0.15));
  border-color: var(--accent);
  box-shadow: 0 0 12px var(--accent-glow);
}
.cal-day.is-today .day-num { color: var(--accent-hover); font-weight: 700; }
.cal-day.is-selected { border-color: var(--accent-light); box-shadow: 0 0 0 2px var(--accent-light); }

.day-num { font-size: 14px; color: var(--text-primary); font-weight: 500; }
.day-marks { display: flex; flex-wrap: wrap; gap: 2px; margin-top: 4px; }
.mark-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
.mark-more { font-size: 9px; color: var(--text-tertiary); }

.badge { position: absolute; top: 4px; right: 4px; font-size: 9px; padding: 1px 4px; border-radius: 3px; font-weight: 600; }
.badge-assigned { background: rgba(82, 146, 134, 0.3); color: var(--accent-light); }
.badge-due { background: rgba(231, 76, 60, 0.3); color: var(--danger); }

@media (max-width: 640px) {
  .cal-day { min-height: 56px; }
  .day-num { font-size: 12px; }
}
</style>
