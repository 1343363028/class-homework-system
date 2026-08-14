<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { homeworkApi } from '@/api/homework'
import type { CountdownItem } from '@/types'

const items = ref<CountdownItem[]>([])
const loading = ref(false)
const collapsed = ref(false)

// ===== 拖动相关状态 =====
const panelX = ref(window.innerWidth - 320)
const panelY = ref(window.innerHeight - 360)
const isDragging = ref(false)
const dragOffsetX = ref(0)
const dragOffsetY = ref(0)

// 从 localStorage 恢复位置
const savedPos = localStorage.getItem('cd_pos')
if (savedPos) {
  try {
    const pos = JSON.parse(savedPos)
    panelX.value = pos.x
    panelY.value = pos.y
  } catch {}
}

let timer: number | null = null

async function load() {
  loading.value = true
  try {
    const res = await homeworkApi.countdown()
    items.value = res.data.items
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

function urgencyClass(item: CountdownItem): string {
  if (item.is_overdue) return 'overdue'
  if (item.days_left === 0) return 'today'
  if (item.days_left <= 1) return 'urgent'
  if (item.days_left <= 3) return 'soon'
  return 'normal'
}

function urgencyText(item: CountdownItem): string {
  if (item.is_overdue) return '已截止'
  if (item.days_left === 0) return '今日截止'
  return `还剩 ${item.days_left} 天`
}

function periodText(period: string): string {
  return period === 'noon' ? '中午' : '晚上'
}

// ===== 拖动逻辑 =====
function onDragStart(e: MouseEvent) {
  // 点击折叠按钮时不触发拖动
  const target = e.target as HTMLElement
  if (target.closest('.cd-toggle')) return
  isDragging.value = true
  const panel = e.currentTarget as HTMLElement
  const rect = panel.getBoundingClientRect()
  dragOffsetX.value = e.clientX - rect.left
  dragOffsetY.value = e.clientY - rect.top
  document.addEventListener('mousemove', onDragMove)
  document.addEventListener('mouseup', onDragEnd)
  e.preventDefault()
}

function onDragMove(e: MouseEvent) {
  if (!isDragging.value) return
  let x = e.clientX - dragOffsetX.value
  let y = e.clientY - dragOffsetY.value
  // 边界约束
  const panelW = 300
  const panelH = collapsed.value ? 48 : 320
  x = Math.max(0, Math.min(x, window.innerWidth - panelW))
  y = Math.max(0, Math.min(y, window.innerHeight - panelH))
  panelX.value = x
  panelY.value = y
}

function onDragEnd() {
  if (!isDragging.value) return
  isDragging.value = false
  document.removeEventListener('mousemove', onDragMove)
  document.removeEventListener('mouseup', onDragEnd)
  // 保存位置
  localStorage.setItem('cd_pos', JSON.stringify({ x: panelX.value, y: panelY.value }))
}

// 触摸支持
function onTouchStart(e: TouchEvent) {
  const target = e.target as HTMLElement
  if (target.closest('.cd-toggle')) return
  isDragging.value = true
  const panel = e.currentTarget as HTMLElement
  const rect = panel.getBoundingClientRect()
  const touch = e.touches[0]
  dragOffsetX.value = touch.clientX - rect.left
  dragOffsetY.value = touch.clientY - rect.top
  document.addEventListener('touchmove', onTouchMove, { passive: false })
  document.addEventListener('touchend', onTouchEnd)
}

function onTouchMove(e: TouchEvent) {
  if (!isDragging.value) return
  e.preventDefault()
  const touch = e.touches[0]
  let x = touch.clientX - dragOffsetX.value
  let y = touch.clientY - dragOffsetY.value
  const panelW = 300
  const panelH = collapsed.value ? 48 : 320
  x = Math.max(0, Math.min(x, window.innerWidth - panelW))
  y = Math.max(0, Math.min(y, window.innerHeight - panelH))
  panelX.value = x
  panelY.value = y
}

function onTouchEnd() {
  isDragging.value = false
  document.removeEventListener('touchmove', onTouchMove)
  document.removeEventListener('touchend', onTouchEnd)
  localStorage.setItem('cd_pos', JSON.stringify({ x: panelX.value, y: panelY.value }))
}

onMounted(() => {
  load()
  timer = window.setInterval(load, 60000)
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
  document.removeEventListener('mousemove', onDragMove)
  document.removeEventListener('mouseup', onDragEnd)
})

defineExpose({ refresh: load })
</script>

<template>
  <div
    class="countdown-float"
    :class="{ collapsed, dragging: isDragging }"
    :style="{ left: panelX + 'px', top: panelY + 'px' }"
    @mousedown="onDragStart"
    @touchstart="onTouchStart"
  >
    <div class="cd-header">
      <div class="cd-title">
        <span class="cd-icon">⏰</span>
        <span>截止倒计时</span>
        <span class="cd-drag-hint" title="可拖动">⋮⋮</span>
      </div>
      <button class="cd-toggle" @click.stop="collapsed = !collapsed" aria-label="折叠">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
          :style="{ transform: collapsed ? 'rotate(0deg)' : 'rotate(180deg)' }">
          <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <div v-show="!collapsed" class="cd-body">
      <div v-if="loading" class="cd-loading">加载中...</div>
      <div v-else-if="items.length === 0" class="cd-empty">暂无待截止作业</div>
      <div v-else class="cd-list">
        <div
          v-for="item in items"
          :key="item.homework_id"
          class="cd-item"
          :class="urgencyClass(item)"
        >
          <div class="cd-item-left">
            <span class="cd-dot" :style="{ background: item.subject_color }"></span>
            <div class="cd-item-info">
              <div class="cd-item-title">{{ item.title }}</div>
              <div class="cd-item-subject">{{ item.subject_name }} · {{ periodText(item.due_period) }}截止</div>
            </div>
          </div>
          <div class="cd-item-right">
            <div class="cd-days">{{ urgencyText(item) }}</div>
            <div class="cd-due">{{ item.due_date }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.countdown-float {
  position: fixed;
  width: 300px;
  background: rgba(15, 34, 51, 0.95);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md), 0 0 20px rgba(46, 134, 193, 0.15);
  backdrop-filter: blur(12px);
  z-index: 1000;
  user-select: none;
  overflow: hidden;
}
.countdown-float.dragging {
  box-shadow: var(--shadow-md), 0 0 30px rgba(46, 134, 193, 0.4);
  border-color: var(--accent);
}

.cd-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: linear-gradient(135deg, rgba(46, 134, 193, 0.2), rgba(82, 146, 134, 0.1));
  border-bottom: 1px solid var(--border);
  cursor: move;
}
.cd-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}
.cd-icon { font-size: 14px; }
.cd-drag-hint {
  font-size: 10px;
  color: var(--text-tertiary);
  letter-spacing: -2px;
  margin-left: 4px;
  cursor: grab;
}
.cd-toggle {
  width: 22px; height: 22px;
  display: flex; align-items: center; justify-content: center;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  border-radius: 4px;
  transition: all var(--transition-fast);
}
.cd-toggle:hover { background: var(--bg-card-hover); color: var(--text-primary); }

.cd-body { padding: 8px; max-height: 280px; overflow-y: auto; }
.cd-loading, .cd-empty {
  padding: 24px;
  text-align: center;
  color: var(--text-tertiary);
  font-size: 13px;
}
.cd-list { display: flex; flex-direction: column; gap: 4px; }

.cd-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  margin-bottom: 4px;
  transition: background var(--transition-fast);
  border-left: 3px solid transparent;
}
.cd-item:hover { background: var(--bg-card-hover); }
.cd-item.urgent { border-left-color: var(--danger); background: rgba(231, 76, 60, 0.08); }
.cd-item.today { border-left-color: var(--warning); background: rgba(212, 172, 13, 0.08); }
.cd-item.soon { border-left-color: var(--accent); }
.cd-item.overdue { border-left-color: var(--text-tertiary); opacity: 0.6; }

.cd-item-left { display: flex; align-items: center; gap: 8px; flex: 1; min-width: 0; }
.cd-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.cd-item-info { min-width: 0; }
.cd-item-title { font-size: 13px; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cd-item-subject { font-size: 11px; color: var(--text-tertiary); margin-top: 2px; }
.cd-item-right { text-align: right; flex-shrink: 0; margin-left: 8px; }
.cd-days { font-size: 12px; font-weight: 600; color: var(--accent-hover); }
.cd-item.urgent .cd-days { color: var(--danger); }
.cd-item.today .cd-days { color: var(--warning); }
.cd-item.overdue .cd-days { color: var(--text-tertiary); }
.cd-due { font-size: 10px; color: var(--text-tertiary); margin-top: 2px; }
</style>
