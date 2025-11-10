<template>
  <AppShell title="Second Opinion Tasks">
    <div class="space-y-6">
      <div class="flex items-center justify-between bg-white rounded-xl shadow p-5">
        <div>
          <h1 class="text-2xl font-bold text-[#2C597D]">งาน Second Opinion</h1>
          <p class="text-gray-500 mt-1">
            งานที่ได้รับมอบหมายให้ให้ความเห็นลำดับที่สอง (Second Opinion) ทั้งหมด {{ tasks.length }} รายการ
          </p>
        </div>
        <div class="flex items-center gap-3">
          <button
            @click="fetchTasks"
            :disabled="loading"
            class="inline-flex items-center gap-2 px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition disabled:opacity-60"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582M20 20v-5h-.581m-1.262 2.262A7.5 7.5 0 016.34 6.34M6 9h.01M18 15h-.01" />
            </svg>
            รีเฟรช
          </button>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow overflow-hidden">
        <div v-if="loading" class="py-10 text-center text-gray-500">
          กำลังโหลดข้อมูลงาน...
        </div>

        <div v-else-if="error" class="py-10 px-6 text-center text-red-500">
          {{ error }}
        </div>

        <div v-else-if="!tasks.length" class="py-12 text-center text-gray-500">
          <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          ยังไม่มีงานที่ได้รับมอบหมาย
        </div>

        <div v-else class="divide-y">
          <div
            v-for="task in tasks"
            :key="task.id"
            class="p-6 hover:bg-gray-50 transition flex flex-col gap-3 md:flex-row md:items-center md:justify-between"
          >
            <div class="min-w-0">
              <div class="flex items-center gap-3 flex-wrap">
                <span class="text-lg font-semibold text-[#2C597D] truncate">
                  {{ task.patientName }}
                </span>
                <span class="inline-flex items-center px-3 py-1 text-xs font-semibold rounded-full bg-[#00BCD4]/10 text-[#007E8C] uppercase tracking-wide">
                  {{ task.statusLabel }}
                </span>
              </div>
              <p class="text-sm text-gray-600 mt-1 line-clamp-2">
                {{ task.question || 'ไม่มีรายละเอียดคำถาม' }}
              </p>
              <div class="flex flex-wrap gap-4 text-xs text-gray-500 mt-2">
                <span>สร้างเมื่อ: {{ formatDate(task.createdAt) }}</span>
                <span v-if="task.diagnosisId">Diagnosis ID: {{ task.diagnosisId }}</span>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0">
              <router-link
                v-if="task.diagnosisId"
                :to="{ name: 'DiagnosisDetail', params: { id: task.diagnosisId } }"
                class="inline-flex items-center gap-2 px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition"
              >
                ไปยัง Diagnosis
              </router-link>
              <router-link
                :to="{ name: 'Patients', query: { highlight: task.patientId } }"
                class="inline-flex items-center gap-2 px-4 py-2 border border-[#00BCD4] text-[#00BCD4] rounded-lg hover:bg-[#00BCD4]/10 transition"
              >
                ดูประวัติผู้ป่วย
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script>
import AppShell from '../components/AppShell.vue'
import { getSecondOpinionNotifications } from '../services/api'

export default {
  name: 'SecondOpinionTasks',
  components: { AppShell },
  data() {
    return {
      loading: false,
      tasks: [],
      error: null,
    }
  },
  methods: {
    async fetchTasks() {
      this.loading = true
      this.error = null
      try {
        const data = await getSecondOpinionNotifications()
        const notifications = data.notifications || []
        this.tasks = notifications.map(item => ({
          id: item.request_id,
          patientId: item.patient_id,
          patientName: item.patient_name || 'ไม่ระบุชื่อผู้ป่วย',
          diagnosisId: item.diagnosis_id,
          question: item.message,
          status: item.status || 'pending',
          statusLabel: (item.status || 'pending').replace(/_/g, ' ').toUpperCase(),
          createdAt: item.created_at,
        }))
      } catch (e) {
        console.error('Failed to load second opinion tasks:', e)
        this.error = e?.response?.data?.detail || 'ไม่สามารถโหลดงานที่ได้รับมอบหมายได้'
      } finally {
        this.loading = false
      }
    },
    formatDate(isoString) {
      if (!isoString) return '-'
      try {
        const date = new Date(isoString)
        return date.toLocaleString(undefined, {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
      } catch {
        return isoString
      }
    }
  },
  created() {
    this.fetchTasks()
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
