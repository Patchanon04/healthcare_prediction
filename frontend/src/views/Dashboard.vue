<template>
  <AppShell title="Dashboard">
    <div class="space-y-6">
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl shadow p-5">
          <div class="text-sm text-gray-500">Total Patients</div>
          <div class="text-3xl font-bold text-[#2C597D] mt-1">{{ summary?.total_patients ?? '-' }}</div>
        </div>
        <div class="bg-white rounded-xl shadow p-5">
          <div class="text-sm text-gray-500">Total Predictions</div>
          <div class="text-3xl font-bold text-[#2C597D] mt-1">{{ summary?.total_predictions ?? '-' }}</div>
        </div>
        <div class="bg-white rounded-xl shadow p-5">
          <div class="text-sm text-gray-500">Today Predictions</div>
          <div class="text-3xl font-bold text-[#2C597D] mt-1">{{ summary?.today_predictions ?? '-' }}</div>
        </div>
        <div class="bg-white rounded-xl shadow p-5">
          <div class="text-sm text-gray-500">Avg Confidence</div>
          <div class="text-3xl font-bold text-[#2C597D] mt-1">{{ avgConfidence }}</div>
        </div>
      </div>

      <!-- Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-xl shadow p-5">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-lg font-semibold">Predictions per day</h3>
            <select v-model.number="days" class="border rounded px-2 py-1 text-sm">
              <option :value="7">7 days</option>
              <option :value="14">14 days</option>
              <option :value="30">30 days</option>
            </select>
          </div>
          <canvas ref="dailyCanvas" height="140"></canvas>
        </div>

        <div class="bg-white rounded-xl shadow p-5">
          <h3 class="text-lg font-semibold mb-2">Diagnosis distribution</h3>
          <canvas ref="distCanvas" height="140"></canvas>
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import AppShell from '../components/AppShell.vue'
import { getMetricsSummary, getMetricsDaily, getDiagnosisDistribution } from '../services/api'

export default {
  name: 'Dashboard',
  components: { AppShell },
  setup() {
    const summary = ref(null)
    const days = ref(14)
    const daily = ref([])
    const dist = ref([])

    const dailyCanvas = ref(null)
    const distCanvas = ref(null)

    let dailyChart = null
    let distChart = null

    const avgConfidence = computed(() => {
      const v = summary.value?.avg_confidence
      if (v == null) return '-'
      return Math.round(v * 100) + '%'
    })

    const loadChartJs = () => new Promise((resolve, reject) => {
      if (window.Chart) return resolve(window.Chart)
      const s = document.createElement('script')
      s.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js'
      s.onload = () => resolve(window.Chart)
      s.onerror = reject
      document.body.appendChild(s)
    })

    const fetchSummary = async () => {
      summary.value = await getMetricsSummary()
    }

    const fetchDaily = async () => {
      const res = await getMetricsDaily(days.value)
      daily.value = res.series || []
      renderDailyChart()
    }

    const fetchDist = async () => {
      const res = await getDiagnosisDistribution()
      dist.value = res.distribution || []
      renderDistChart()
    }

    const renderDailyChart = async () => {
      await loadChartJs()
      const ctx = dailyCanvas.value.getContext('2d')
      const labels = daily.value.map(d => d.date)
      const data = daily.value.map(d => d.count)
      if (dailyChart) dailyChart.destroy()
      dailyChart = new window.Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Predictions',
            data,
            tension: 0.35,
            borderColor: '#00BCD4',
            backgroundColor: 'rgba(0,188,212,0.15)',
            fill: true,
            pointRadius: 2
          }]
        },
        options: {
          responsive: true,
          scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
          plugins: { legend: { display: false } }
        }
      })
    }

    const renderDistChart = async () => {
      await loadChartJs()
      const ctx = distCanvas.value.getContext('2d')
      const labels = dist.value.map(d => d.diagnosis)
      const data = dist.value.map(d => d.count)
      if (distChart) distChart.destroy()
      distChart = new window.Chart(ctx, {
        type: 'doughnut',
        data: {
          labels,
          datasets: [{
            data,
            backgroundColor: ['#00BCD4','#00ACC1','#0097A7','#26C6DA','#4DD0E1','#80DEEA','#B2EBF2']
          }]
        },
        options: {
          plugins: { legend: { position: 'bottom' } }
        }
      })
    }

    onMounted(async () => {
      await fetchSummary()
      await Promise.all([fetchDaily(), fetchDist()])
    })

    watch(days, fetchDaily)

    return { summary, days, avgConfidence, dailyCanvas, distCanvas }
  }
}
</script>
