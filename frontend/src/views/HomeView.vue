<template>
  <AppShell title="Home">
    <div class="bg-white rounded-xl shadow p-6">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">History</h2>
      <HistoryList />
    </div>
  </AppShell>
</template>

<script>
import AppShell from '../components/AppShell.vue'
import HistoryList from '../components/HistoryList.vue'

export default {
  name: 'HomeView',
  components: { AppShell, HistoryList }
}
</script>
