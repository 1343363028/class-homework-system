// 科目状态管理
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { subjectApi } from '@/api/subject'
import type { Subject, SubjectUpdate } from '@/types'

export const useSubjectStore = defineStore('subject', () => {
  const subjects = ref<Subject[]>([])
  const loaded = ref(false)

  async function load(force = false) {
    if (loaded.value && !force) return
    const res = await subjectApi.list()
    subjects.value = res.data
    loaded.value = true
  }

  function getColor(subjectId: number): string {
    return subjects.value.find((x) => x.id === subjectId)?.color || '#5A6B7D'
  }
  function getName(subjectId: number): string {
    return subjects.value.find((x) => x.id === subjectId)?.name || '未知科目'
  }
  function getIcon(subjectId: number): string {
    return subjects.value.find((x) => x.id === subjectId)?.icon || 'book'
  }

  async function create(data: { name: string; color: string; icon: string }) {
    const res = await subjectApi.create(data)
    subjects.value.push(res.data)
    return res.data
  }

  async function update(id: number, data: SubjectUpdate) {
    const res = await subjectApi.update(id, data)
    const idx = subjects.value.findIndex((s) => s.id === id)
    if (idx >= 0) subjects.value[idx] = res.data
    return res.data
  }

  async function initPreset() {
    const res = await subjectApi.initPreset()
    await load(true)
    return res.data
  }

  async function remove(id: number) {
    await subjectApi.delete(id)
    subjects.value = subjects.value.filter((s) => s.id !== id)
  }

  return { subjects, loaded, load, getColor, getName, getIcon, create, update, initPreset, remove }
})
