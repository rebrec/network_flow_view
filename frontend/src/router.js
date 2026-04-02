import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from './views/Dashboard.vue'
import Explorer from './views/Explorer.vue'
import Topology from './views/Topology.vue'

const routes = [
  { path: '/', component: Dashboard, name: 'dashboard' },
  { path: '/explorer', component: Explorer, name: 'explorer' },
  { path: '/topology', component: Topology, name: 'topology' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
