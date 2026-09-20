import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/transactions',
    name: 'Transactions',
    component: () => import('@/views/Transactions.vue')
  },
  {
    path: '/transactions/:id',
    name: 'TransactionDetail',
    component: () => import('@/views/TransactionDetail.vue')
  },
  {
    path: '/vendors',
    name: 'Vendors',
    component: () => import('@/views/Vendors.vue')
  },
  {
    path: '/tax-transactions',
    name: 'TaxTransactions',
    component: () => import('@/views/TaxTransactions.vue')
  },
  {
    path: '/reconciliation',
    name: 'Reconciliation',
    component: () => import('@/views/Reconciliation.vue')
  },
  {
    path: '/exceptions',
    name: 'Exceptions',
    component: () => import('@/views/Exceptions.vue')
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('@/views/Analytics.vue')
  },
  {
    path: '/ingestion',
    name: 'Ingestion',
    component: () => import('@/views/Ingestion.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
