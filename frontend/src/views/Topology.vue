<template>
  <div class="h-[calc(100vh-12rem)] flex flex-col">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Network Topology</h1>
      <div class="flex space-x-2">
        <button class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-bold transition shadow-md">Refresh</button>
        <button class="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-sm font-bold transition border border-gray-600">Export Graph</button>
      </div>
    </div>

    <div class="flex-1 bg-gray-950 rounded-xl shadow-2xl border border-gray-800 relative overflow-hidden">
      <div id="cy" class="absolute inset-0"></div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import cytoscape from 'cytoscape'
import axios from 'axios'

const cyRef = ref(null)

onMounted(async () => {
  try {
    const response = await axios.get('/api/v1/graphs/dependency')
    const graphData = response.data

    cyRef.value = cytoscape({
      container: document.getElementById('cy'),
      elements: graphData,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#3b82f6',
            'label': 'data(id)',
            'color': '#fff',
            'font-size': '12px',
            'text-valign': 'center',
            'text-halign': 'center',
            'width': '40px',
            'height': '40px',
            'border-width': '2px',
            'border-color': '#1e40af'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#4b5563',
            'target-arrow-color': '#4b5563',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(port)',
            'font-size': '10px',
            'color': '#9ca3af',
            'text-rotation': 'autorotate',
            'text-margin-y': '-10px'
          }
        }
      ],
      layout: {
        name: 'cose',
        padding: 50,
        animate: true
      }
    })
  } catch (error) {
    console.error('Failed to fetch graph data:', error)
  }
})
</script>

<style scoped>
#cy {
  width: 100%;
  height: 100%;
}
</style>
