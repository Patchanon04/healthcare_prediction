<template>
  <AppShell title="Appointments">
    <div class="max-w-7xl mx-auto">
      <!-- Header with Add Button -->
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-3xl font-bold text-[#2C597D]">Appointments Calendar</h1>
          <p class="text-gray-500 mt-1">View and manage patient appointments</p>
        </div>
        <button 
          @click="openCreateModal()"
          class="bg-gradient-to-r from-[#00BCD4] to-[#00ACC1] text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          New Appointment
        </button>
      </div>

      <!-- Calendar Navigation -->
      <div class="bg-white rounded-xl shadow-sm p-4 mb-6">
        <div class="flex items-center justify-between mb-4">
          <button 
            @click="previousMonth"
            class="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <svg class="w-6 h-6 text-[#2C597D]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
          </button>
          <h2 class="text-2xl font-bold text-[#2C597D]">
            {{ currentMonthYear }}
          </h2>
          <button 
            @click="nextMonth"
            class="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <svg class="w-6 h-6 text-[#2C597D]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
        </div>

        <!-- Calendar Grid -->
        <div class="grid grid-cols-7 gap-2">
          <!-- Day Headers -->
          <div v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day" class="text-center font-semibold text-gray-600 py-2">
            {{ day }}
          </div>
          
          <!-- Calendar Days -->
          <div 
            v-for="day in calendarDays" 
            :key="day.date"
            @click="selectDate(day)"
            :class="[
              'min-h-[100px] p-2 border-2 rounded-lg cursor-pointer transition',
              day.isCurrentMonth ? 'bg-white hover:border-[#00BCD4]' : 'bg-gray-50 text-gray-400',
              day.isToday ? 'border-orange-500 bg-orange-50' : 'border-gray-200',
              day.isSelected ? 'border-[#00BCD4] bg-[#00BCD4]/5' : '',
              day.hasAppointments ? 'font-semibold' : ''
            ]"
          >
            <div class="text-right mb-1">{{ day.day }}</div>
            <div v-if="day.appointmentCount > 0" class="text-xs text-center">
              <span class="inline-block px-2 py-1 bg-[#00BCD4] text-white rounded-full">
                {{ day.appointmentCount }} {{ day.appointmentCount === 1 ? 'appt' : 'appts' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Day Appointments Modal -->
      <div v-if="showDayModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" @click.self="closeDayModal">
        <div class="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden">
          <!-- Modal Header -->
          <div class="p-6 border-b border-gray-200 flex justify-between items-center bg-gradient-to-r from-[#00BCD4] to-[#00ACC1]">
            <div>
              <h2 class="text-2xl font-bold text-white">
                {{ formatSelectedDate }}
              </h2>
              <p class="text-white/80 mt-1">
                {{ selectedDateAppointments.length }} {{ selectedDateAppointments.length === 1 ? 'appointment' : 'appointments' }}
              </p>
            </div>
            <button @click="closeDayModal" class="text-white hover:bg-white/20 p-2 rounded-lg transition">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <!-- Modal Body -->
          <div class="p-6 overflow-y-auto max-h-[calc(80vh-120px)]">
            <div v-if="selectedDateAppointments.length === 0" class="text-center py-12">
              <svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
              <p class="text-gray-500 text-lg mb-4">No appointments on this date</p>
              <button 
                @click="() => { closeDayModal(); openCreateModal(selectedDate.value) }"
                class="bg-gradient-to-r from-[#00BCD4] to-[#00ACC1] text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition"
              >
                Add an appointment
              </button>
            </div>

            <div v-else class="space-y-4">
              <div 
                v-for="appointment in selectedDateAppointments" 
                :key="appointment.id"
                class="border-2 border-gray-200 rounded-xl p-5 hover:border-[#00BCD4] hover:shadow-md transition"
              >
                <div class="flex items-start justify-between gap-4">
                  <!-- Left: Time Badge -->
                  <div class="flex-shrink-0">
                    <div class="bg-gradient-to-br from-[#00BCD4] to-[#00ACC1] text-white rounded-xl p-3 text-center min-w-[80px]">
                      <div class="text-2xl font-bold">{{ formatTime(appointment.appointment_date) }}</div>
                      <div class="text-xs opacity-90 mt-1">{{ appointment.duration_minutes }} min</div>
                    </div>
                  </div>

                  <!-- Middle: Patient Info -->
                  <div class="flex-1">
                    <div class="flex items-start gap-3">
                      <router-link 
                        :to="`/patients/${appointment.patient_id}`"
                        @click="closeDayModal"
                        class="w-12 h-12 rounded-full bg-gradient-to-br from-orange-400 to-orange-500 flex items-center justify-center text-white text-xl font-bold flex-shrink-0 hover:scale-110 transition"
                      >
                        {{ appointment.patient_name.charAt(0).toUpperCase() }}
                      </router-link>
                      <div class="flex-1">
                        <router-link 
                          :to="`/patients/${appointment.patient_id}`"
                          @click="closeDayModal"
                          class="text-xl font-bold text-[#2C597D] hover:text-[#00BCD4] transition block"
                        >
                          {{ appointment.patient_name }}
                        </router-link>
                        <p class="text-sm text-gray-500">MRN: {{ appointment.patient_mrn }}</p>
                        <div class="mt-2 flex items-start gap-2">
                          <svg class="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                          </svg>
                          <p class="text-sm text-gray-600">{{ appointment.reason || 'No reason specified' }}</p>
                        </div>
                        <span 
                          :class="[
                            'inline-block px-3 py-1 rounded-full text-xs font-semibold mt-3',
                            getStatusClass(appointment.status)
                          ]"
                        >
                          {{ getStatusLabel(appointment.status) }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Right: Actions -->
                  <div class="flex gap-2 flex-shrink-0">
                    <button 
                      @click="editAppointment(appointment); closeDayModal()"
                      class="p-2 text-[#00BCD4] hover:bg-[#00BCD4]/10 rounded-lg transition"
                      title="Edit"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                      </svg>
                    </button>
                    <button 
                      @click="deleteAppointment(appointment.id)"
                      class="p-2 text-red-500 hover:bg-red-50 rounded-lg transition"
                      title="Delete"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Add/Edit Modal -->
      <div v-if="showAddModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="p-6 border-b border-gray-200 flex justify-between items-center sticky top-0 bg-white">
            <h2 class="text-2xl font-bold text-[#2C597D]">
              {{ editingAppointment ? 'Edit Appointment' : 'New Appointment' }}
            </h2>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <form @submit.prevent="saveAppointment" class="p-6 space-y-4">
            <!-- Patient Selection -->
            <div>
              <label class="block text-sm font-medium text-[#2C597D] mb-2">Patient *</label>
              <select 
                v-model="form.patient_id" 
                required
                class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition"
              >
                <option value="">Select a patient</option>
                <option v-for="patient in patients" :key="patient.id" :value="patient.id">
                  {{ patient.full_name }} ({{ patient.mrn }})
                </option>
              </select>
            </div>

            <!-- Date & Time -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-[#2C597D] mb-2">Date *</label>
                <input 
                  v-model="form.date" 
                  type="date"
                  required
                  class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-[#2C597D] mb-2">Time *</label>
                <input 
                  v-model="form.time" 
                  type="time"
                  required
                  class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition"
                />
              </div>
            </div>

            <!-- Duration & Status -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-[#2C597D] mb-2">Duration (minutes) *</label>
                <input 
                  v-model.number="form.duration_minutes" 
                  type="number"
                  min="15"
                  step="15"
                  required
                  class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-[#2C597D] mb-2">Status *</label>
                <select 
                  v-model="form.status" 
                  required
                  class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition"
                >
                  <option value="scheduled">Scheduled</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                  <option value="no_show">No Show</option>
                </select>
              </div>
            </div>

            <!-- Reason -->
            <div>
              <label class="block text-sm font-medium text-[#2C597D] mb-2">Reason for Visit</label>
              <textarea 
                v-model="form.reason" 
                rows="3"
                class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition resize-none"
                placeholder="e.g., Follow-up checkup, Annual physical, etc."
              ></textarea>
            </div>

            <!-- Notes -->
            <div>
              <label class="block text-sm font-medium text-[#2C597D] mb-2">Notes</label>
              <textarea 
                v-model="form.notes" 
                rows="3"
                class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition resize-none"
                placeholder="Additional notes..."
              ></textarea>
            </div>

            <!-- Actions -->
            <div class="flex gap-4 pt-4">
              <button 
                type="submit"
                :disabled="saving"
                class="flex-1 bg-gradient-to-r from-[#00BCD4] to-[#00ACC1] text-white rounded-xl py-3 font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition disabled:opacity-50"
              >
                {{ saving ? 'Saving...' : (editingAppointment ? 'Update' : 'Create') }}
              </button>
              <button 
                type="button"
                @click="closeModal"
                class="flex-1 bg-gray-100 text-gray-700 rounded-xl py-3 font-semibold hover:bg-gray-200 transition"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import AppShell from '../components/AppShell.vue'
import {
  listAppointments,
  createAppointment as createAppointmentApi,
  updateAppointment as updateAppointmentApi,
  deleteAppointment as deleteAppointmentApi,
  listPatients
} from '../services/api'

export default {
  name: 'AppointmentsView',
  components: { AppShell },
  setup() {
    const toast = useToast()
    const loading = ref(false)
    const saving = ref(false)
    const showAddModal = ref(false)
    const showDayModal = ref(false)
    const editingAppointment = ref(null)
    const appointments = ref([])
    const patients = ref([])
    const allowAutoFetch = ref(true)
    
    // Calendar state
    const currentDate = ref(new Date())
    const selectedDate = ref(null)

    const defaultFormState = () => ({
      patient_id: '',
      date: '',
      time: '09:00',
      duration_minutes: 30,
      status: 'scheduled',
      reason: '',
      notes: ''
    })

    const form = ref(defaultFormState())

    // Calendar computed properties
    const currentMonthYear = computed(() => {
      return currentDate.value.toLocaleDateString('en-GB', { month: 'long', year: 'numeric' })
    })

    const formatDisplayDate = (value) => {
      const date = value instanceof Date ? value : new Date(value)
      if (Number.isNaN(date.getTime())) return ''
      return date.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    }

    const formatSelectedDate = computed(() => {
      if (!selectedDate.value) return ''
      return formatDisplayDate(selectedDate.value)
    })

    const formatLocalDate = (date) => {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    const toLocalDateKey = (value) => formatLocalDate(new Date(value))

    const calendarDays = computed(() => {
      const year = currentDate.value.getFullYear()
      const month = currentDate.value.getMonth()
      
      // First day of month
      const firstDay = new Date(year, month, 1)
      const startingDayOfWeek = firstDay.getDay()
      
      // Last day of month
      const lastDay = new Date(year, month + 1, 0)
      const daysInMonth = lastDay.getDate()
      
      // Previous month days
      const prevMonthLastDay = new Date(year, month, 0).getDate()
      
      const days = []
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      // Add previous month days
      for (let i = startingDayOfWeek - 1; i >= 0; i--) {
        const date = new Date(year, month - 1, prevMonthLastDay - i)
        const dateStr = formatLocalDate(date)
        days.push({
          day: prevMonthLastDay - i,
          date: dateStr,
          isCurrentMonth: false,
          isToday: false,
          isSelected: false,
          hasAppointments: false,
          appointmentCount: 0
        })
      }
      
      // Add current month days
      for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(year, month, day)
        const dateStr = formatLocalDate(date)
        const dayAppointments = appointments.value.filter(a => 
          toLocalDateKey(a.appointment_date) === dateStr
        )
        
        days.push({
          day,
          date: dateStr,
          isCurrentMonth: true,
          isToday: date.getTime() === today.getTime(),
          isSelected: selectedDate.value === dateStr,
          hasAppointments: dayAppointments.length > 0,
          appointmentCount: dayAppointments.length
        })
      }
      
      // Add next month days to complete the grid
      const remainingDays = 42 - days.length // 6 rows * 7 days
      for (let day = 1; day <= remainingDays; day++) {
        const date = new Date(year, month + 1, day)
        days.push({
          day,
          date: formatLocalDate(date),
          isCurrentMonth: false,
          isToday: false,
          isSelected: false,
          hasAppointments: false,
          appointmentCount: 0
        })
      }
      
      return days
    })

    const selectedDateAppointments = computed(() => {
      if (!selectedDate.value) return []
      return appointments.value
        .filter(a => toLocalDateKey(a.appointment_date) === selectedDate.value)
        .sort((a, b) => a.appointment_date.localeCompare(b.appointment_date))
    })

    // Calendar navigation
    const previousMonth = () => {
      currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
    }

    const nextMonth = () => {
      currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
    }

    const selectDate = (day) => {
      if (!day.isCurrentMonth) return
      selectedDate.value = day.date
      showDayModal.value = true
    }

    const closeDayModal = () => {
      showDayModal.value = false
    }

    const fetchAppointments = async () => {
      if (loading.value) return
      loading.value = true
      try {
        const reference = currentDate.value
        const rangeStart = new Date(reference.getFullYear(), reference.getMonth(), 1)
        const rangeEnd = new Date(reference.getFullYear(), reference.getMonth() + 1, 0)
        const data = await listAppointments({
          page: 1,
          pageSize: 500,
          start: formatLocalDate(rangeStart),
          end: formatLocalDate(rangeEnd)
        })
        const records = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
        appointments.value = records
          .map(record => ({
            ...record,
            appointment_date: record.appointment_date
          }))
          .sort((a, b) => new Date(a.appointment_date) - new Date(b.appointment_date))
      } catch (e) {
        toast.error(e.message || 'Failed to load appointments')
      } finally {
        loading.value = false
      }
    }

    const fetchPatients = async () => {
      try {
        const data = await listPatients({ page: 1, pageSize: 200 })
        patients.value = data.results || []
      } catch (e) {
        toast.error('Failed to load patients')
      }
    }

    const formatTime = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleTimeString('th-TH', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false
      })
    }

    const getStatusClass = (status) => {
      const classes = {
        scheduled: 'bg-blue-100 text-blue-700',
        confirmed: 'bg-green-100 text-green-700',
        completed: 'bg-gray-100 text-gray-700',
        cancelled: 'bg-red-100 text-red-700',
        no_show: 'bg-orange-100 text-orange-700'
      }
      return classes[status] || 'bg-gray-100 text-gray-700'
    }

    const getStatusLabel = (status) => {
      const labels = {
        scheduled: 'Scheduled',
        confirmed: 'Confirmed',
        completed: 'Completed',
        cancelled: 'Cancelled',
        no_show: 'No Show'
      }
      return labels[status] || status
    }

    const openCreateModal = (dateStr = null) => {
      editingAppointment.value = null
      const baseDate = dateStr
        ? new Date(dateStr)
        : selectedDate.value
          ? new Date(selectedDate.value)
          : new Date()
      form.value = {
        ...defaultFormState(),
        date: formatLocalDate(baseDate)
      }
      showAddModal.value = true
    }

    const editAppointment = (appointment) => {
      editingAppointment.value = appointment
      const date = new Date(appointment.appointment_date)
      form.value = {
        patient_id: appointment.patient_id,
        date: formatLocalDate(date),
        time: date.toTimeString().slice(0, 5),
        duration_minutes: appointment.duration_minutes,
        status: appointment.status,
        reason: appointment.reason,
        notes: appointment.notes
      }
      showAddModal.value = true
    }

    const deleteAppointment = async (id) => {
      if (!confirm('Are you sure you want to delete this appointment?')) return
      try {
        await deleteAppointmentApi(id)
        toast.success('Appointment deleted successfully')
        await fetchAppointments()
        if (selectedDate.value) {
          showDayModal.value = true
        }
      } catch (e) {
        toast.error(e.message || 'Failed to delete appointment')
      }
    }

    const saveAppointment = async () => {
      saving.value = true
      try {
        const appointmentDate = new Date(`${form.value.date}T${form.value.time}:00`)
        if (Number.isNaN(appointmentDate.getTime())) {
          throw new Error('Invalid date or time')
        }

        const payload = {
          patient_id: form.value.patient_id,
          appointment_date: appointmentDate.toISOString(),
          duration_minutes: form.value.duration_minutes,
          status: form.value.status,
          reason: form.value.reason,
          notes: form.value.notes
        }

        if (editingAppointment.value) {
          await updateAppointmentApi(editingAppointment.value.id, payload)
          toast.success('Appointment updated successfully')
        } else {
          await createAppointmentApi(payload)
          toast.success('Appointment created successfully')
        }

        allowAutoFetch.value = false
        currentDate.value = new Date(appointmentDate.getFullYear(), appointmentDate.getMonth(), 1)
        await fetchAppointments()
        allowAutoFetch.value = true

        selectedDate.value = formatLocalDate(appointmentDate)
        showDayModal.value = true
        closeModal()
      } catch (e) {
        allowAutoFetch.value = true
        toast.error(e.message || 'Failed to save appointment')
      } finally {
        saving.value = false
      }
    }

    const closeModal = () => {
      showAddModal.value = false
      editingAppointment.value = null
      form.value = defaultFormState()
    }

    onMounted(() => {
      fetchAppointments()
      fetchPatients()
    })

    watch(currentDate, async () => {
      if (!allowAutoFetch.value) return
      await fetchAppointments()
    })

    return {
      loading,
      saving,
      showAddModal,
      showDayModal,
      editingAppointment,
      appointments,
      patients,
      form,
      currentDate,
      selectedDate,
      currentMonthYear,
      formatSelectedDate,
      calendarDays,
      selectedDateAppointments,
      previousMonth,
      nextMonth,
      selectDate,
      closeDayModal,
      formatDisplayDate,
      formatTime,
      getStatusClass,
      getStatusLabel,
      openCreateModal,
      editAppointment,
      deleteAppointment,
      saveAppointment,
      closeModal
    }
  }
}
</script>
