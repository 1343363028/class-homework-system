<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import AppNavbar from '@/components/AppNavbar.vue'
import CountdownFloat from '@/components/CountdownFloat.vue'
import { useSubjectStore } from '@/stores/subject'

const subjectStore = useSubjectStore()
const showForm = ref(false)
const editingId = ref<number | null>(null)
const initLoading = ref(false)

const form = reactive({
  name: '',
  color: '#2E86C1',
  icon: 'book',
})

const presetColors = [
  '#2E86C1', '#529286', '#E67E22', '#8E44AD',
  '#16A085', '#C0392B', '#D4AC0D', '#3498DB',
  '#1ABC9C', '#9B59B6', '#34495E', '#E74C3C',
  '#FF6B35', '#F7DC6F', '#48C9B0', '#AF7AC5',
]

// 预置图标（emoji + 文本标识），同时支持自定义输入
const presetIcons = [
  '📚', '⚛️', '⚡', 'ƒ', '〰️', '⭐', '🔌', '⚙️',
  '📐', '🧮', '🔬', '🧪', '💡', '📝', '🎯', '🏆',
]

function openCreate() {
  editingId.value = null
  form.name = ''
  form.color = presetColors[subjectStore.subjects.length % presetColors.length]
  form.icon = '📚'
  showForm.value = true
}

function openEdit(id: number) {
  const s = subjectStore.subjects.find((x) => x.id === id)
  if (!s) return
  editingId.value = id
  form.name = s.name
  form.color = s.color
  form.icon = s.icon
  showForm.value = true
}

async function submit() {
  if (!form.name.trim()) {
    alert('请输入科目名称')
    return
  }
  if (!form.icon.trim()) {
    alert('请输入或选择图标')
    return
  }
  try {
    if (editingId.value) {
      await subjectStore.update(editingId.value, { ...form })
    } else {
      await subjectStore.create({ ...form })
    }
    showForm.value = false
  } catch (e: any) {
    alert(e.message || '操作失败')
  }
}

async function initPreset() {
  if (!confirm('确定初始化预置六门科目？已存在的科目将跳过。')) return
  initLoading.value = true
  try {
    const res = await subjectStore.initPreset()
    alert(res.message)
  } catch (e: any) {
    alert(e.message || '初始化失败')
  } finally {
    initLoading.value = false
  }
}

async function remove(id: number, name: string) {
  if (!confirm(`确定删除科目「${name}」？关联的作业将不受影响但会显示为未知科目。`)) return
  try {
    await subjectStore.remove(id)
  } catch (e: any) {
    alert(e.message || '删除失败')
  }
}

onMounted(() => subjectStore.load(true))
</script>

<template>
  <div>
    <AppNavbar />
    <div class="main-content">
      <div class="page-header">
        <div>
          <h2 class="page-title">科目管理</h2>
          <p class="page-desc">添加、编辑、删除科目，自定义颜色与图标</p>
        </div>
        <div class="header-actions">
          <button class="btn-secondary" :disabled="initLoading" @click="initPreset">
            {{ initLoading ? '初始化中...' : '初始化预置科目' }}
          </button>
          <button class="btn-primary" @click="openCreate">+ 添加科目</button>
        </div>
      </div>

      <div v-if="subjectStore.subjects.length === 0" class="empty-state">
        <div class="empty-icon">🎨</div>
        <p>暂无科目，点击右上角添加或初始化预置科目</p>
      </div>

      <div v-else class="subject-grid">
        <div v-for="s in subjectStore.subjects" :key="s.id" class="subject-card card">
          <div class="subject-icon" :style="{ background: s.color + '22', color: s.color }">
            {{ s.icon }}
          </div>
          <div class="subject-info">
            <div class="subject-name">{{ s.name }}</div>
            <div class="subject-color">{{ s.color }}</div>
          </div>
          <div class="subject-actions">
            <button class="btn-icon edit" @click="openEdit(s.id)" title="编辑">✏️</button>
            <button class="btn-icon delete" @click="remove(s.id, s.name)" title="删除">🗑️</button>
          </div>
        </div>
      </div>
    </div>

    <CountdownFloat />

    <!-- 表单弹窗 -->
    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="card modal">
        <h3 class="modal-title">{{ editingId ? '编辑科目' : '添加科目' }}</h3>

        <div class="form-group">
          <label class="form-label">科目名称</label>
          <input v-model="form.name" class="input" type="text" placeholder="如：大学物理" />
        </div>

        <div class="form-group">
          <label class="form-label">颜色</label>
          <div class="color-picker">
            <button
              v-for="color in presetColors"
              :key="color"
              class="color-swatch"
              :class="{ active: form.color === color }"
              :style="{ background: color }"
              @click="form.color = color"
            ></button>
            <input v-model="form.color" type="color" class="color-input" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">图标（可自定义输入）</label>
          <div class="icon-preview">
            <div class="icon-preview-box" :style="{ background: form.color + '22', color: form.color }">
              {{ form.icon || '?' }}
            </div>
            <input v-model="form.icon" class="input icon-input" type="text" placeholder="输入 emoji 或文字" maxlength="8" />
          </div>
          <div class="icon-picker">
            <button
              v-for="icon in presetIcons"
              :key="icon"
              class="icon-swatch"
              :class="{ active: form.icon === icon }"
              @click="form.icon = icon"
            >{{ icon }}</button>
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
.main-content { max-width: 1000px; margin: 0 auto; padding: 24px; position: relative; z-index: 1; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.page-title { font-size: 22px; font-weight: 700; color: var(--text-primary); }
.page-desc { font-size: 13px; color: var(--text-tertiary); margin-top: 4px; }
.header-actions { display: flex; gap: 10px; }
.btn-primary { padding: 10px 20px; background: var(--accent); border: none; border-radius: var(--radius-sm); color: #fff; font-size: 14px; transition: all var(--transition); }
.btn-primary:hover { background: var(--accent-hover); transform: translateY(-1px); }
.btn-secondary { padding: 10px 20px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: var(--radius-sm); color: var(--text-secondary); font-size: 14px; transition: all var(--transition); }
.btn-secondary:hover { background: var(--bg-card-hover); }
.btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }

.empty-state { text-align: center; padding: 60px 20px; color: var(--text-tertiary); }
.empty-icon { font-size: 48px; margin-bottom: 12px; }

.subject-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.subject-card { display: flex; align-items: center; gap: 16px; padding: 18px; transition: all var(--transition); }
.subject-card:hover { border-color: var(--border-strong); transform: translateY(-2px); box-shadow: var(--shadow-md); }
.subject-icon { width: 48px; height: 48px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
.subject-info { flex: 1; min-width: 0; }
.subject-name { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.subject-color { font-size: 11px; color: var(--text-tertiary); margin-top: 4px; font-family: monospace; }
.subject-actions { display: flex; gap: 6px; }
.btn-icon { width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 13px; transition: all var(--transition); }
.btn-icon.edit:hover { background: var(--accent); border-color: var(--accent); }
.btn-icon.delete:hover { background: var(--danger); border-color: var(--danger); }

.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 100; padding: 20px; }
.modal { width: 100%; max-width: 480px; padding: 28px; animation: fadeIn 0.2s ease; }
.modal-title { font-size: 18px; font-weight: 600; color: var(--text-primary); margin-bottom: 20px; }
.form-group { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.form-label { font-size: 13px; color: var(--text-secondary); }

.color-picker { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.color-swatch { width: 28px; height: 28px; border-radius: 50%; border: 2px solid transparent; cursor: pointer; transition: all var(--transition); }
.color-swatch.active { border-color: #fff; box-shadow: 0 0 0 2px var(--accent); transform: scale(1.1); }
.color-input { width: 40px; height: 28px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: transparent; cursor: pointer; }

.icon-preview { display: flex; align-items: center; gap: 12px; }
.icon-preview-box { width: 48px; height: 48px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
.icon-input { flex: 1; }
.icon-picker { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.icon-swatch { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 16px; cursor: pointer; transition: all var(--transition); }
.icon-swatch:hover { border-color: var(--accent); }
.icon-swatch.active { background: rgba(46, 134, 193, 0.2); border-color: var(--accent); }

.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
</style>
