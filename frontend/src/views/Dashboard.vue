<template>
  <div>
    <h1 class="text-3xl font-bold mb-8">Dashboard</h1>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-700">
        <p class="text-sm text-gray-400 font-medium uppercase tracking-wider mb-2">Active Flows (24h)</p>
        <p class="text-4xl font-bold text-blue-400">{{ summary.active_flows || 0 }}</p>
      </div>
      <div class="bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-700">
        <p class="text-sm text-gray-400 font-medium uppercase tracking-wider mb-2">Total Traffic</p>
        <p class="text-4xl font-bold text-green-400">{{ formatBytes(totalBytes) }}</p>
      </div>
      <div class="bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-700">
        <p class="text-sm text-gray-400 font-medium uppercase tracking-wider mb-2">Top Protocol</p>
        <p class="text-4xl font-bold text-purple-400">TCP</p>
      </div>
    </div>

    <div class="bg-gray-800 rounded-lg shadow-xl overflow-hidden border border-gray-700">
      <div class="p-4 bg-gray-750 border-b border-gray-700 flex justify-between items-center">
        <h2 class="font-bold text-lg">Top Talkers (by flows count)</h2>
      </div>
      <table class="w-full text-left">
        <thead class="bg-gray-900 text-gray-400 uppercase text-xs">
          <tr>
            <th class="p-4">IP Source</th>
            <th class="p-4">IP Destination</th>
            <th class="p-4 text-center">Port</th>
            <th class="p-4">Protocol</th>
            <th class="p-4 text-right">Observation Count</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-700">
          <tr v-for="flow in summary.top_talkers" :key="flow.id" class="hover:bg-gray-750 transition">
            <td class="p-4 font-mono text-blue-300">{{ flow.ip_src }}</td>
            <td class="p-4 font-mono text-gray-300">{{ flow.ip_dst }}</td>
            <td class="p-4 text-center text-green-400 font-bold">{{ flow.port_dst }}</td>
            <td class="p-4">{{ flow.protocol }}</td>
            <td class="p-4 text-right font-bold text-yellow-500">{{ flow.total_count }}</td>
          </tr>
          <tr v-if="!summary.top_talkers || summary.top_talkers.length === 0">
            <td colspan="5" class="p-8 text-center text-gray-500 italic">No data available</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const summary = ref({
  active_flows: 0,
  top_talkers: []
})

const totalBytes = computed(() => {
  return summary.value.top_talkers.reduce((acc, flow) => acc + (flow.bytes || 0), 0)
})

function formatBytes(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(async () => {
  try {
    const response = await axios.get('/api/v1/stats/summary')
    summary.value = response.data
  } catch (error) {
    console.error('Failed to fetch summary:', error)
  }
})
</script>
