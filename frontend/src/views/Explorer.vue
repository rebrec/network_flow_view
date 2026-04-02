<template>
  <div>
    <h1 class="text-3xl font-bold mb-8 italic text-blue-400">NetVis Explorer <span class="text-gray-500 font-normal">V1</span></h1>

    <!-- Search Bar -->
    <div class="bg-gray-800 p-6 rounded-lg shadow-xl mb-8 border border-gray-700">
      <div class="flex space-x-4">
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-400 mb-2">NVQL Query</label>
          <input
            v-model="query"
            type="text"
            placeholder="src:10.1.1.1 and port:443"
            class="w-full bg-gray-700 border border-gray-600 rounded p-3 text-blue-300 font-mono text-lg focus:ring-2 focus:ring-blue-500 outline-none transition shadow-inner"
            @keyup.enter="handleSearch"
          >
        </div>
        <div class="flex items-end">
          <button
            class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded font-bold transition shadow-lg active:scale-95"
            @click="handleSearch"
          >
            Search
          </button>
        </div>
      </div>
      <div class="mt-3 text-xs text-gray-500 italic flex space-x-4">
        <span>Try: src.zone:PROD and not proto:UDP</span>
        <span>|</span>
        <span>src:10.1.1.1 and port:443</span>
      </div>
    </div>

    <!-- Results Table -->
    <div class="bg-gray-800 rounded-lg overflow-hidden shadow-2xl border border-gray-700">
      <div class="p-4 bg-gray-750 flex justify-between items-center border-b border-gray-700">
        <h2 class="font-bold">Consolidated Flows ({{ results.length }} results)</h2>
        <div class="flex space-x-2">
            <button class="text-xs bg-gray-700 hover:bg-gray-600 px-3 py-1.5 rounded transition text-gray-400 border border-gray-600">Export CSV</button>
            <button class="text-xs bg-gray-700 hover:bg-gray-600 px-3 py-1.5 rounded transition text-gray-400 border border-gray-600">Clear</button>
        </div>
      </div>
      <table class="w-full text-left text-sm">
        <thead class="bg-gray-900 text-gray-400 uppercase text-xs">
          <tr>
            <th class="p-4">IP Source</th>
            <th class="p-4">IP Destination</th>
            <th class="p-4 text-center">Port</th>
            <th class="p-4">Proto</th>
            <th class="p-4">First Seen</th>
            <th class="p-4">Last Seen</th>
            <th class="p-4 text-right">Count</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-700">
          <tr v-for="flow in results" :key="flow.id" class="hover:bg-gray-750 transition group">
            <td class="p-4 font-mono text-blue-300 group-hover:text-blue-200 transition">{{ flow.ip_src }}</td>
            <td class="p-4 font-mono text-gray-300">{{ flow.ip_dst }}</td>
            <td class="p-4 text-center text-green-400 font-bold">{{ flow.port_dst }}</td>
            <td class="p-4 font-semibold text-purple-300">{{ flow.protocol }}</td>
            <td class="p-4 text-gray-500 font-mono text-xs">{{ formatDate(flow.first_seen) }}</td>
            <td class="p-4 text-gray-400 font-mono text-xs">{{ formatDate(flow.last_seen) }}</td>
            <td class="p-4 text-right font-bold text-yellow-500">{{ flow.total_count }}</td>
          </tr>
          <tr v-if="results.length === 0">
            <td colspan="7" class="p-12 text-center text-gray-500 italic">No flows found or no query executed yet</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const query = ref('')
const results = ref([])

async function handleSearch() {
  try {
    const response = await axios.post('/api/v1/flows/search', {
      query_string: query.value
    })
    results.value = response.data.data
  } catch (error) {
    console.error('Search failed:', error)
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

onMounted(() => {
  handleSearch() // Initial load
})
</script>
