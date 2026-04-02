<template>
  <div class="min-h-screen bg-gray-900 text-gray-100 font-sans">
    <nav class="bg-gray-800 border-b border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <h1 class="text-2xl font-bold text-blue-400">NetVis <span class="text-gray-400 text-sm font-normal">V1</span></h1>
            </div>
            <div class="hidden md:block">
              <div class="ml-10 flex items-baseline space-x-4">
                <router-link to="/" class="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 transition" :class="[$route.name === 'dashboard' ? 'bg-gray-900 text-blue-400 border-b-2 border-blue-400' : 'text-gray-300']">Dashboard</router-link>
                <router-link to="/explorer" class="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 transition" :class="[$route.name === 'explorer' ? 'bg-gray-900 text-blue-400 border-b-2 border-blue-400' : 'text-gray-300']">Explorer</router-link>
                <router-link to="/topology" class="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 transition" :class="[$route.name === 'topology' ? 'bg-gray-900 text-blue-400 border-b-2 border-blue-400' : 'text-gray-300']">Topology</router-link>
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-2 text-xs text-gray-500 italic">
            <span class="inline-block w-2 h-2 bg-green-500 rounded-full"></span>
            <span>API Online</span>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
</script>
