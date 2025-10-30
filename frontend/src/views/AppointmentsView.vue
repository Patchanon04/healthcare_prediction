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
          @click="showAddModal = true"
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

      <!-- Selected Date Appointments -->
      <div v-if="selectedDate" class="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h3 class="text-xl font-bold text-[#2C597D] mb-4">
          Appointments for {{ formatSelectedDate }}
        </h3>

        <div v-if="selectedDateAppointments.length === 0" class="text-center py-8">
          <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
          </svg>
          <p class="text-gray-500">No appointments on this date</p>
          <button 
            @click="showAddModal = true"
            class="mt-3 text-[#00BCD4] hover:underline font-semibold"
          >
            Add an appointment
          </button>
        </div>

        <div v-else class="space-y-3">
          <div 
            v-for="appointment in selectedDateAppointments" 
            :key="appointment.id"
            class="border-2 border-gray-200 rounded-xl p-4 hover:border-[#00BCD4] transition"
          >
            <div class="flex items-center justify-between">
              <!-- Left: Patient Info & Time -->
              <div class="flex items-center gap-4 flex-1">
                <router-link 
                  :to="`/patients/${appointment.patient_id}`"
                  class="w-12 h-12 rounded-full bg-gradient-to-br from-[#00BCD4] to-[#00ACC1] flex items-center justify-center text-white text-xl font-bold flex-shrink-0 hover:scale-110 transition"
                >
                  {{ appointment.patient_name.charAt(0).toUpperCase() }}
                </router-link>
                <div class="flex-1">
                  <router-link 
                    :to="`/patients/${appointment.patient_id}`"
                    class="text-lg font-semibold text-[#2C597D] hover:text-[#00BCD4] transition"
                  >
                    {{ appointment.patient_name }}
                  </router-link>
                  <p class="text-sm text-gray-500">MRN: {{ appointment.patient_mrn }}</p>
                  <p class="text-sm text-gray-600 mt-1">{{ appointment.reason || 'No reason specified' }}</p>
                </div>
              </div>

              <!-- Right: Time & Actions -->
              <div class="flex items-center gap-4">
                <div class="text-right">
                  <div class="flex items-center gap-2 text-[#2C597D] font-bold text-lg">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    {{ formatTime(appointment.appointment_date) }}
                  </div>
                  <p class="text-sm text-gray-500 mt-1">{{ appointment.duration_minutes }} minutes</p>
                  <span 
                    :class="[
                      'inline-block px-3 py-1 rounded-full text-xs font-semibold mt-2',
                      getStatusClass(appointment.status)
                    ]"
                  >
                    {{ getStatusLabel(appointment.status) }}
                  </span>
                </div>

                <!-- Actions -->
                <div class="flex gap-2">
                  <button 
                    @click="editAppointment(appointment)"
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
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import AppShell from '../components/AppShell.vue'

export default {
  name: 'AppointmentsView',
  components: { AppShell },
  setup() {
    const toast = useToast()
    const loading = ref(false)
    const saving = ref(false)
    const showAddModal = ref(false)
    const editingAppointment = ref(null)
    const appointments = ref([])
    const patients = ref([])
    
    // Calendar state
    const currentDate = ref(new Date())
    const selectedDate = ref(null)

    const form = ref({
      patient_id: '',
      date: '',
      time: '',
      duration_minutes: 30,
      status: 'scheduled',
      reason: '',
      notes: ''
    })

    // Calendar computed properties
    const currentMonthYear = computed(() => {
      return currentDate.value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    })

    const formatSelectedDate = computed(() => {
      if (!selectedDate.value) return ''
      return new Date(selectedDate.value).toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })
    })

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
        days.push({
          day: prevMonthLastDay - i,
          date: date.toISOString().split('T')[0],
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
        const dateStr = date.toISOString().split('T')[0]
        const dayAppointments = appointments.value.filter(a => 
          a.appointment_date.startsWith(dateStr)
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
          date: date.toISOString().split('T')[0],
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
        .filter(a => a.appointment_date.startsWith(selectedDate.value))
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
    }

    const fetchAppointments = async () => {
      loading.value = true
      try {
        // Mock data for now - replace with actual API call
        const today = new Date()
        const tomorrow = new Date(today)
        tomorrow.setDate(tomorrow.getDate() + 1)
        const nextWeek = new Date(today)
        nextWeek.setDate(nextWeek.getDate() + 7)
        
        appointments.value = [
          {
            id: 1,
            patient_id: 1,
            patient_name: 'John Doe',
            patient_mrn: 'MRN001',
            appointment_date: `${today.toISOString().split('T')[0]}T10:00:00`,
            duration_minutes: 30,
            status: 'scheduled',
            reason: 'Annual checkup',
            notes: ''
          },
          {
            id: 2,
            patient_id: 2,
            patient_name: 'Jane Smith',
            patient_mrn: 'MRN002',
            appointment_date: `${today.toISOString().split('T')[0]}T14:30:00`,
            duration_minutes: 45,
            status: 'confirmed',
            reason: 'Follow-up consultation',
            notes: 'Patient requested afternoon slot'
          },
          {
            id: 3,
            patient_id: 3,
            patient_name: 'Bob Johnson',
            patient_mrn: 'MRN003',
            appointment_date: `${tomorrow.toISOString().split('T')[0]}T09:00:00`,
            duration_minutes: 60,
            status: 'scheduled',
            reason: 'Initial consultation',
            notes: ''
          },
          {
            id: 4,
            patient_id: 1,
            patient_name: 'John Doe',
            patient_mrn: 'MRN001',
            appointment_date: `${nextWeek.toISOString().split('T')[0]}T11:00:00`,
            duration_minutes: 30,
            status: 'scheduled',
            reason: 'Follow-up',
            notes: ''
          }
        ]
        
        // Auto-select today if it has appointments
        const todayStr = today.toISOString().split('T')[0]
        const todayAppointments = appointments.value.filter(a => a.appointment_date.startsWith(todayStr))
        if (todayAppointments.length > 0) {
          selectedDate.value = todayStr
        }
      } catch (e) {
        toast.error('Failed to load appointments')
      } finally {
        loading.value = false
      }
    }

    const fetchPatients = async () => {
      try {
        const { listPatients } = await import('../services/api')
        const data = await listPatients({ page: 1, pageSize: 100 })
        patients.value = data.results || []
      } catch (e) {
        toast.error('Failed to load patients')
      }
    }

    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { 
        weekday: 'short', 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    }

    const formatTime = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
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

    const editAppointment = (appointment) => {
      editingAppointment.value = appointment
      const date = new Date(appointment.appointment_date)
      form.value = {
        patient_id: appointment.patient_id,
        date: date.toISOString().split('T')[0],
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
        // TODO: API call to delete
        appointments.value = appointments.value.filter(a => a.id !== id)
        toast.success('Appointment deleted successfully')
      } catch (e) {
        toast.error('Failed to delete appointment')
      }
    }

    const saveAppointment = async () => {
      saving.value = true
      try {
        // TODO: API call to create/update
        const appointmentDate = `${form.value.date}T${form.value.time}:00`
        
        if (editingAppointment.value) {
          // Update existing
          const index = appointments.value.findIndex(a => a.id === editingAppointment.value.id)
          if (index !== -1) {
            appointments.value[index] = {
              ...appointments.value[index],
              appointment_date: appointmentDate,
              duration_minutes: form.value.duration_minutes,
              status: form.value.status,
              reason: form.value.reason,
              notes: form.value.notes
            }
          }
          toast.success('Appointment updated successfully')
        } else {
          // Create new
          const patient = patients.value.find(p => p.id === form.value.patient_id)
          appointments.value.push({
            id: Date.now(),
            patient_name: patient?.full_name || 'Unknown',
            patient_mrn: patient?.mrn || '',
            patient_id: form.value.patient_id,
            appointment_date: appointmentDate,
            duration_minutes: form.value.duration_minutes,
            status: form.value.status,
            reason: form.value.reason,
            notes: form.value.notes
          })
          toast.success('Appointment created successfully')
        }
        
        closeModal()
      } catch (e) {
        toast.error('Failed to save appointment')
      } finally {
        saving.value = false
      }
    }

    const closeModal = () => {
      showAddModal.value = false
      editingAppointment.value = null
      form.value = {
        patient_id: '',
        date: '',
        time: '',
        duration_minutes: 30,
        status: 'scheduled',
        reason: '',
        notes: ''
      }
    }

    onMounted(() => {
      fetchAppointments()
      fetchPatients()
    })

    return {
      loading,
      saving,
      showAddModal,
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
      formatDate,
      formatTime,
      getStatusClass,
      getStatusLabel,
      editAppointment,
      deleteAppointment,
      saveAppointment,
      closeModal
    }
  }
}
</script>
