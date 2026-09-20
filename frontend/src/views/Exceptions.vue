<template>
  <div class="space-y-6">
    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <p class="text-sm text-gray-500">Total Exceptions</p>
        <p class="text-2xl font-bold text-red-600">{{ stats?.total || 0 }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <p class="text-sm text-gray-500">Open</p>
        <p class="text-2xl font-bold text-orange-600">{{ stats?.by_status?.OPEN || 0 }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <p class="text-sm text-gray-500">In Review</p>
        <p class="text-2xl font-bold text-yellow-600">{{ stats?.by_status?.IN_REVIEW || 0 }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <p class="text-sm text-gray-500">Resolved</p>
        <p class="text-2xl font-bold text-green-600">{{ stats?.by_status?.RESOLVED || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg border border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="label">Exception Type</label>
          <select v-model="filters.exception_type" class="input">
            <option :value="undefined">All</option>
            <option v-for="type in exceptionTypes" :key="type" :value="type">{{ type }}</option>
          </select>
        </div>
        <div>
          <label class="label">Status</label>
          <select v-model="filters.status" class="input">
            <option :value="undefined">All</option>
            <option value="OPEN">Open</option>
            <option value="IN_REVIEW">In Review</option>
            <option value="RESOLVED">Resolved</option>
            <option value="IGNORED">Ignored</option>
          </select>
        </div>
        <div>
          <label class="label">Severity</label>
          <select v-model="filters.severity" class="input">
            <option :value="undefined">All</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
        <div>
          <label class="label">Search</label>
          <input type="text" v-model="filters.search" class="input" placeholder="Search..." />
        </div>
        <div class="flex items-end space-x-2">
          <button @click="resetFilters" class="btn btn-secondary">Reset</button>
          <button @click="applyFilters" class="btn btn-primary">Apply</button>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-if="loading"><td colspan="8" class="px-4 py-8 text-center">Loading...</td></tr>
          <tr v-else-if="exceptions.length === 0"><td colspan="8" class="px-4 py-8 text-center text-gray-500">No exceptions found</td></tr>
          <tr v-else v-for="ex in exceptions" :key="ex.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-mono text-sm">{{ ex.id }}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">{{ ex.exception_type }}</span>
            </td>
            <td class="px-4 py-3">
              <span :class="severityClass(ex.severity)">{{ ex.severity }}</span>
            </td>
            <td class="px-4 py-3 text-sm text-gray-900 max-w-xs truncate">{{ ex.description }}</td>
            <td class="px-4 py-3 text-right font-mono text-sm">{{ ex.amount ? formatCurrency(ex.amount) : '-' }}</td>
            <td class="px-4 py-3">
              <span :class="statusClass(ex.status)">{{ ex.status }}</span>
            </td>
            <td class="px-4 py-3 text-sm text-gray-500">{{ formatDate(ex.created_at) }}</td>
            <td class="px-4 py-3">
              <button @click="openDetail(ex)" class="text-blue-600 hover:text-blue-800 text-sm">View</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="px-4 py-3 bg-gray-50 border-t flex items-center justify-between">
        <p class="text-sm text-gray-700">Showing {{ exceptions.length }} of {{ total }}</p>
        <div class="flex space-x-2">
          <button @click="prevPage" :disabled="page === 1" class="px-3 py-1 border rounded text-sm disabled:opacity-50">Previous</button>
          <span class="px-3 py-1 text-sm">Page {{ page }} of {{ totalPages }}</span>
          <button @click="nextPage" :disabled="page >= totalPages" class="px-3 py-1 border rounded text-sm disabled:opacity-50">Next</button>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <ExceptionDetailModal
      v-if="selectedException"
      :exception="selectedException"
      @close="selectedException = null"
      @updated="onExceptionUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useExceptionStore } from '@/stores/exceptions'
import ExceptionDetailModal from '@/components/forms/ExceptionDetailModal.vue'
import type { Exception } from '@/types'

const store = useExceptionStore()
const selectedException = ref<Exception | null>(null)

const filters = ref({
  exception_type: undefined as string | undefined,
  status: undefined as string | undefined,
  severity: undefined as string | undefined,
  search: ''
})

const exceptionTypes = [
  'AMOUNT_MISMATCH', 'TAX_MISMATCH', 'MISSING_INVOICE', 'MISSING_PO',
  'DUPLICATE', 'VENDOR_MISMATCH', 'TAX_CODE_MISMATCH', 'MISSING_TAX_RECORD', 'INVALID_DATA'
]

onMounted(() => {
  store.fetchExceptions()
  store.fetchStats()
})

const exceptions = computed(() => store.exceptions)
const stats = computed(() => store.stats)
const total = computed(() => store.total)
const page = computed(() => store.page)
const totalPages = computed(() => store.totalPages)
const loading = computed(() => store.loading)

const applyFilters = () => store.fetchExceptions({ ...filters.value, page: 1 })
const resetFilters = () => {
  filters.value = { exception_type: undefined, status: undefined, severity: undefined, search: '' }
  store.fetchExceptions({ page: 1 })
}
const prevPage = () => page.value > 1 && store.fetchExceptions({ page: page.value - 1 })
const nextPage = () => page.value < totalPages.value && store.fetchExceptions({ page: page.value + 1 })

const openDetail = (ex: Exception) => { selectedException.value = ex }
const onExceptionUpdated = () => { selectedException.value = null; applyFilters(); store.fetchStats() }

const severityClass = (severity: string) => {
  const classes: Record<string, string> = {
    LOW: 'px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800',
    MEDIUM: 'px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800',
    HIGH: 'px-2 py-1 text-xs rounded-full bg-orange-100 text-orange-800',
    CRITICAL: 'px-2 py-1 text-xs rounded-full bg-red-100 text-red-800'
  }
  return classes[severity] || classes.LOW
}

const statusClass = (status: string) => {
  const classes: Record<string, string> = {
    OPEN: 'px-2 py-1 text-xs rounded-full bg-red-100 text-red-800',
    IN_REVIEW: 'px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800',
    RESOLVED: 'px-2 py-1 text-xs rounded-full bg-green-100 text-green-800',
    IGNORED: 'px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800'
  }
  return classes[status] || classes.OPEN
}

const formatCurrency = (value: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'IDR' }).format(value)
const formatDate = (date: string) => new Date(date).toLocaleDateString()
</script>
