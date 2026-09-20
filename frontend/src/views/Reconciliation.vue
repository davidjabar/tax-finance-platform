<template>
  <div class="space-y-6">
    <!-- Run Reconciliation -->
    <div class="bg-white p-6 rounded-lg border border-gray-200">
      <h3 class="text-lg font-semibold mb-4">Run Reconciliation</h3>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
        <div>
          <label class="label">Period Start</label>
          <input type="date" v-model="periodStart" class="input" />
        </div>
        <div>
          <label class="label">Period End</label>
          <input type="date" v-model="periodEnd" class="input" />
        </div>
        <button
          @click="runReconciliation"
          :disabled="running"
          class="btn btn-primary h-10"
        >
          {{ running ? 'Running...' : 'Run Reconciliation' }}
        </button>
        <div v-if="runResult" class="text-sm">
          <span :class="runResult.status === 'COMPLETED' ? 'text-green-600' : 'text-red-600'">
            {{ runResult.status }}: {{ runResult.matched }} matched, {{ runResult.exceptions }} exceptions
          </span>
        </div>
      </div>
    </div>

    <!-- Recent Runs -->
    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-200">
        <h3 class="font-semibold">Reconciliation History</h3>
      </div>
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Matched</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Exceptions</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-if="loading"><td colspan="8" class="px-4 py-8 text-center">Loading...</td></tr>
          <tr v-else-if="runs.length === 0"><td colspan="8" class="px-4 py-8 text-center text-gray-500">No reconciliation runs</td></tr>
          <tr v-else v-for="run in runs" :key="run.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-mono text-sm">{{ run.id }}</td>
            <td class="px-4 py-3 text-sm">{{ run.period_start }} - {{ run.period_end }}</td>
            <td class="px-4 py-3">
              <span :class="statusClass(run.status)">{{ run.status }}</span>
            </td>
            <td class="px-4 py-3 text-right font-mono text-sm">{{ run.total_records }}</td>
            <td class="px-4 py-3 text-right font-mono text-sm text-green-600">{{ run.matched }}</td>
            <td class="px-4 py-3 text-right font-mono text-sm text-red-600">{{ run.exceptions }}</td>
            <td class="px-4 py-3 text-sm text-gray-500">{{ formatDate(run.created_at) }}</td>
            <td class="px-4 py-3">
              <button @click="viewResults(run)" class="text-blue-600 hover:text-blue-800 text-sm">View Results</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Results Modal -->
    <div v-if="selectedRun" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-start">
          <div>
            <h3 class="text-lg font-semibold">Reconciliation Results #{{ selectedRun.id }}</h3>
            <p class="text-sm text-gray-500">{{ selectedRun.period_start }} - {{ selectedRun.period_end }}</p>
          </div>
          <button @click="selectedRun = null" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
        </div>

        <div class="p-4 border-b border-gray-200 flex space-x-4">
          <select v-model="resultFilter" class="input w-48">
            <option :value="undefined">All Results</option>
            <option value="MATCHED">Matched</option>
            <option value="PARTIAL_MATCH">Partial Match</option>
            <option value="MISMATCH">Mismatch</option>
            <option value="EXCEPTION">Exception</option>
          </select>
        </div>

        <div class="overflow-auto flex-1">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50 sticky top-0">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Document</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vendor</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Exception</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-if="resultsLoading"><td colspan="5" class="px-4 py-8 text-center">Loading...</td></tr>
              <tr v-else-if="results.length === 0"><td colspan="5" class="px-4 py-8 text-center text-gray-500">No results</td></tr>
              <tr v-else v-for="r in results" :key="r.transaction_id" class="hover:bg-gray-50">
                <td class="px-4 py-3 font-mono text-sm">{{ r.document_number }}</td>
                <td class="px-4 py-3 text-sm">{{ r.vendor_name }}</td>
                <td class="px-4 py-3 text-right font-mono text-sm">{{ formatCurrency(r.amount) }}</td>
                <td class="px-4 py-3">
                  <span :class="reconStatusClass(r.reconciliation_status)">{{ r.reconciliation_status }}</span>
                </td>
                <td class="px-4 py-3 text-sm text-gray-500">{{ r.exception_type || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="px-4 py-3 border-t border-gray-200 flex justify-between items-center">
          <p class="text-sm text-gray-700">Total: {{ resultsTotal }} results</p>
          <div class="flex space-x-2">
            <button @click="prevResultsPage" :disabled="resultsPage === 1" class="px-3 py-1 border rounded text-sm disabled:opacity-50">Previous</button>
            <span class="px-3 py-1 text-sm">Page {{ resultsPage }}</span>
            <button @click="nextResultsPage" :disabled="results.length < 50" class="px-3 py-1 border rounded text-sm disabled:opacity-50">Next</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { reconciliationApi } from '@/api/reconciliation'
import type { ReconciliationRun } from '@/types'

const runs = ref<ReconciliationRun[]>([])
const loading = ref(false)
const running = ref(false)
const runResult = ref<any>(null)

const periodStart = ref('')
const periodEnd = ref('')

const selectedRun = ref<ReconciliationRun | null>(null)
const results = ref<any[]>([])
const resultsLoading = ref(false)
const resultsPage = ref(1)
const resultsTotal = ref(0)
const resultFilter = ref<string | undefined>(undefined)

onMounted(() => {
  fetchRuns()
  // Set default period
  const today = new Date()
  periodEnd.value = today.toISOString().split('T')[0]
  periodStart.value = new Date(today.getFullYear(), today.getMonth() - 1, 1).toISOString().split('T')[0]
})

const fetchRuns = async () => {
  loading.value = true
  try {
    const res = await reconciliationApi.getRuns({ page: 1, page_size: 20 })
    runs.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const runReconciliation = async () => {
  running.value = true
  try {
    const res = await reconciliationApi.run({
      period_start: periodStart.value,
      period_end: periodEnd.value
    })
    runResult.value = res.data
    fetchRuns()
  } catch (e) {
    console.error(e)
  } finally {
    running.value = false
  }
}

const viewResults = async (run: ReconciliationRun) => {
  selectedRun.value = run
  resultsPage.value = 1
  fetchResults()
}

const fetchResults = async () => {
  if (!selectedRun.value) return
  resultsLoading.value = true
  try {
    const res = await reconciliationApi.getResults(selectedRun.value.id, {
      page: resultsPage.value,
      page_size: 50,
      match_result: resultFilter.value
    })
    results.value = res.data.items
    resultsTotal.value = res.data.total
  } catch (e) {
    console.error(e)
  } finally {
    resultsLoading.value = false
  }
}

watch(resultFilter, () => { resultsPage.value = 1; fetchResults() })

const prevResultsPage = () => { if (resultsPage.value > 1) { resultsPage.value--; fetchResults() } }
const nextResultsPage = () => { resultsPage.value++; fetchResults() }

const statusClass = (status: string) => {
  const classes: Record<string, string> = {
    COMPLETED: 'px-2 py-1 text-xs rounded-full bg-green-100 text-green-800',
    RUNNING: 'px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800',
    FAILED: 'px-2 py-1 text-xs rounded-full bg-red-100 text-red-800',
    PENDING: 'px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800'
  }
  return classes[status] || classes.PENDING
}

const reconStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    MATCHED: 'px-2 py-1 text-xs rounded-full bg-green-100 text-green-800',
    PARTIAL_MATCH: 'px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800',
    MISMATCH: 'px-2 py-1 text-xs rounded-full bg-red-100 text-red-800',
    EXCEPTION: 'px-2 py-1 text-xs rounded-full bg-red-100 text-red-800'
  }
  return classes[status] || 'px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800'
}

const formatDate = (date: string) => new Date(date).toLocaleDateString()
const formatCurrency = (value: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'IDR' }).format(value)
</script>
