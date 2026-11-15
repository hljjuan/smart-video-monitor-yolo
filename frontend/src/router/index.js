import { createRouter, createWebHistory } from 'vue-router'
import Overview from '../views/Overview.vue'
import Detect from '../views/Detect.vue'
import Alarms from '../views/Alarms.vue'
import Report from '../views/Report.vue'
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/overview' },
    { path: '/overview', component: Overview },
    { path: '/detect', component: Detect },
    { path: '/alarms', component: Alarms },
    { path: '/report', component: Report }
  ]
})
export default router