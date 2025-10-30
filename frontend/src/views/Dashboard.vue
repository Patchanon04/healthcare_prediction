<template>
  <div class="space-y-6">
      <!-- Date Range Filter + Export -->
      <div class="bg-white rounded-xl shadow p-5">
        <div class="flex flex-wrap items-end gap-4">
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input v-model="startDate" type="date" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent" />
          </div>
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input v-model="endDate" type="date" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent" />
          </div>
          <button @click="applyDateRange" class="px-6 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition font-semibold">
            Apply
          </button>
          <button @click="exportPDF" :disabled="!reportData" class="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed">
            Export PDF
          </button>
        </div>
      </div>

      <!-- Summary Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="bg-white rounded-xl shadow p-5">
          <div class="text-sm text-gray-500">Total Patients</div>
          <div class="text-3xl font-bold text-[#2C597D] mt-1">{{ reportData?.summary?.total_patients ?? '-' }}</div>
          <div v-if="reportData?.summary?.patients_with_predictions !== undefined" class="text-xs text-gray-400 mt-1">
            {{ reportData.summary.patients_with_predictions }} with diagnoses
          </div>
        </div>
        <div class="bg-white rounded-xl shadow p-5">
          <div class="text-sm text-gray-500">Total Predictions</div>
          <div class="text-3xl font-bold text-[#2C597D] mt-1">{{ reportData?.summary?.total_predictions ?? '-' }}</div>
        </div>
        <div class="bg-white rounded-xl shadow p-5">
          <div class="text-sm text-gray-500">Avg Confidence</div>
          <div class="text-3xl font-bold text-[#2C597D] mt-1">{{ avgConfidence }}</div>
        </div>
      </div>

      <!-- Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-xl shadow p-5">
          <h3 class="text-lg font-semibold mb-2">Predictions per day</h3>
          <canvas ref="dailyCanvas" height="140"></canvas>
        </div>

        <div class="bg-white rounded-xl shadow p-5">
          <h3 class="text-lg font-semibold mb-2">Diagnosis distribution</h3>
          <canvas ref="distCanvas" height="140"></canvas>
        </div>
      </div>
    
    <!-- Error Modal -->
    <Modal :show="showErrorModal" title="Error" @close="showErrorModal = false">
      <p class="text-gray-700">{{ errorMessage }}</p>
      <template #footer>
        <button @click="showErrorModal = false" class="px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition">
          OK
        </button>
      </template>
    </Modal>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import Modal from '../components/Modal.vue'
import { getReportSummary } from '../services/api'

export default {
  name: 'Dashboard',
  components: { Modal },
  setup() {
    const reportData = ref(null)
    const startDate = ref('')
    const endDate = ref('')
    const showErrorModal = ref(false)
    const errorMessage = ref('')

    const dailyCanvas = ref(null)
    const distCanvas = ref(null)

    let dailyChart = null
    let distChart = null

    const avgConfidence = computed(() => {
      const v = reportData.value?.summary?.avg_confidence
      if (v == null) return '-'
      return Math.round(v * 100) + '%'
    })

    // Set default date range (last 14 days)
    const initDateRange = () => {
      const end = new Date()
      const start = new Date()
      start.setDate(end.getDate() - 13)
      endDate.value = end.toISOString().split('T')[0]
      startDate.value = start.toISOString().split('T')[0]
    }

    const showError = (msg) => {
      errorMessage.value = msg
      showErrorModal.value = true
    }

    const loadChartJs = () => new Promise((resolve, reject) => {
      if (window.Chart) return resolve(window.Chart)
      const s = document.createElement('script')
      s.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js'
      s.onload = () => resolve(window.Chart)
      s.onerror = reject
      document.body.appendChild(s)
    })

    const loadJsPDF = () => new Promise((resolve, reject) => {
      if (window.jspdf) return resolve(window.jspdf)
      const s1 = document.createElement('script')
      s1.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'
      s1.onload = () => {
        const s2 = document.createElement('script')
        s2.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js'
        s2.onload = () => resolve(window.jspdf)
        s2.onerror = reject
        document.body.appendChild(s2)
      }
      s1.onerror = reject
      document.body.appendChild(s1)
    })

    const fetchReportData = async () => {
      try {
        const data = await getReportSummary({ start: startDate.value, end: endDate.value })
        reportData.value = data
        renderCharts()
      } catch (err) {
        console.error('Failed to fetch report:', err)
        showError('Failed to load report data. Please try again.')
      }
    }

    const applyDateRange = () => {
      fetchReportData()
    }

    const renderCharts = async () => {
      await loadChartJs()
      renderDailyChart()
      renderDistChart()
    }

    const renderDailyChart = () => {
      const ctx = dailyCanvas.value.getContext('2d')
      const series = reportData.value?.daily_series || []
      const labels = series.map(d => d.date)
      const data = series.map(d => d.count)
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

    const renderDistChart = () => {
      const ctx = distCanvas.value.getContext('2d')
      const dist = reportData.value?.diagnosis_distribution || []
      const labels = dist.map(d => d.diagnosis)
      const data = dist.map(d => d.count)
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

    const exportPDF = async () => {
      if (!reportData.value) return
      await loadJsPDF()
      const { jsPDF } = window.jspdf
      const doc = new jsPDF()

      // Header
      doc.setFontSize(18)
      doc.text('MedML Diagnosis Report', 14, 20)
      doc.setFontSize(11)
      doc.text(`Period: ${reportData.value.date_range.start} to ${reportData.value.date_range.end}`, 14, 28)
      doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 34)

      // Summary
      doc.setFontSize(14)
      doc.text('Summary', 14, 44)
      doc.setFontSize(10)
      const summary = reportData.value.summary
      doc.text(`Total Patients: ${summary.total_patients}`, 14, 52)
      doc.text(`Total Predictions: ${summary.total_predictions}`, 14, 58)
      doc.text(`Average Confidence: ${summary.avg_confidence}%`, 14, 64)

      // Diagnosis Distribution
      doc.setFontSize(14)
      doc.text('Diagnosis Distribution', 14, 76)
      const distData = reportData.value.diagnosis_distribution.map(d => [d.diagnosis, d.count])
      doc.autoTable({
        startY: 80,
        head: [['Diagnosis', 'Count']],
        body: distData,
        theme: 'grid',
        headStyles: { fillColor: [0, 188, 212] }
      })

      // Recent Transactions
      let finalY = doc.lastAutoTable.finalY + 10
      doc.setFontSize(14)
      doc.text('Recent Transactions (max 100)', 14, finalY)
      const txnData = reportData.value.recent_transactions.slice(0, 50).map(t => [
        t.uploaded_at.split('T')[0],
        t.patient_name,
        t.diagnosis,
        `${t.confidence}%`
      ])
      doc.autoTable({
        startY: finalY + 4,
        head: [['Date', 'Patient', 'Diagnosis', 'Confidence']],
        body: txnData,
        theme: 'striped',
        headStyles: { fillColor: [0, 188, 212] },
        styles: { fontSize: 8 }
      })

      doc.save(`MedML_Report_${startDate.value}_to_${endDate.value}.pdf`)
    }

    onMounted(async () => {
      initDateRange()
      await fetchReportData()
    })

    return { 
      reportData, 
      startDate, 
      endDate, 
      avgConfidence, 
      dailyCanvas, 
      distCanvas, 
      applyDateRange, 
      exportPDF,
      showErrorModal,
      errorMessage
    }
  }
}
</script>
