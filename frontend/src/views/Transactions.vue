<template>
  <div class="space-y-6">
    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg border border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div>
          <label class="label">Date From</label>
          <input type="date" v-model="filters.date_from" class="input" />
        </div>
        <div>
          <label class="label">Date To</label>
          <input type="date" v-model="filters.date_to" class="input" />
        </div>
        <div>
          <label class="label">Entity</label>
          <select v-model="filters.entity_id" class="input">
            <option :value="undefined">All</option>
            <option v-for="e in entities" :key="e.id" :value="e.id">{{ e.code }}</option>
          </select>
        </div>
        <div>
          <label class="label">Recon Status</label>
          <select v-model="filters.reconciliation_status" class="input">
            <option :value="undefined">All</option>
            <option value="MATCHED">Matched</option>
            <option value="PARTIAL_MATCH">Partial Match</option>
            <option value="MISMATCH">Mismatch</option>
            <option value="UNRECONCILED">Unreconciled</option>
            <option value="EXCEPTION">Exception</option>
          </select>
        </div>
        <div>
          <label class="label">Tax Code</label>
          <select v-model="filters.tax_code" class="input">
            <option :value="undefined">All</option>
            <option v-for="code in taxCodes" :key="code" :value="code">{{ code }}</option>
          </select>
        </div>
        <div>
          <label class="label">Search</label>
          <input type="text" v-model="filters.search" placeholder="Document, PO, Invoice..." class="input" />
        </div>
      </div>
      <div class="mt-4 flex justify-end space-x-2">
        <button @click="resetFilters" class="btn btn-secondary">Reset</button>
        <button @click="applyFilters" class="btn btn-primary">Apply Filters</button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Document</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendor</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Entity</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Tax</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tax Code</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recon Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="loading">
              <td colspan="9" class="px-4 py-8 text-center text-gray-500">Loading...</td>
            </tr>
            <tr v-else-if="transactions.length === 0">
              <td colspan="9" class="px-4 py-8 text-center text-gray-500">No transactions found</td>
            </tr>
            <tr v-else v-for="tx in transactions" :key="tx.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 whitespace-nowrap">
                <router-link :to="`/transactions/${tx.id}`" class="text-blue-600 hover:underline font-medium">
                  {{ tx.document_number }}
                </router-link>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{{ tx.transaction_date }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{{ tx.vendor_name }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{{ tx.entity_code }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 text-right font-mono">
                {{ formatCurrency(tx.amount, tx.currency) }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 text-right font-mono">
                {{ tx.tax_amount ? formatCurrency(tx.tax_amount, tx.currency) : '-' }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span class="px-2 py-1 text-xs rounded-full bg-gray-100">{{ tx.tax_code || '-' }}</span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span :class="reconStatusClass(tx.reconciliation_status)">
                  {{ tx.reconciliation_status }}
                </span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <button @click="openEditModal(tx)" class="text-blue-600 hover:text-blue-800 text-sm">
                  Edit
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-4 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
        <p class="text-sm text-gray-700">
          Showing {{ transactions.length }} of {{ total }} results
        </p>
        <div class="flex space-x-2">
          <button
            @click="prevPage"
            :disabled="page === 1"
            class="px-3 py-1 border rounded text-sm disabled:opacity-50"
          >
            Previous
          </button>
          <span class="px-3 py-1 text-sm">Page {{ page }} of {{ totalPages }}</span>
          <button
            @click="nextPage"
            :disabled="page >= totalPages"
            class="px-3 py-1 border rounded text-sm disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <EditTransactionModal
      v-if="editTransaction"
      :transaction="editTransaction"
      @close="editTransaction = null"
      @saved="onTransactionSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useTransactionStore } from '@/stores/transactions'
import { useDashboardStore } from '@/stores/dashboard'
import EditTransactionModal from '@/components/forms/EditTransactionModal.vue'
import type { Transaction } from '@/types'

const txStore = useTransactionStore()
const dashboardStore = useDashboardStore()

const filters = ref({
  date_from: '',
  date_to: '',
  entity_id: undefined as number | undefined,
  reconciliation_status: undefined as string | undefined,
  tax_code: undefined as string | undefined,
  search: ''
})

const taxCodes = ['PPN11', 'PPN12', 'PPN10', 'PPN0', 'PPNBM', 'EXEMPT']
const editTransaction = ref<Transaction | null>(null)

const transactions = computed(() => txStore.transactions)
const total = computed(() => txStore.total)
const page = computed(() => txStore.page)
const totalPages = computed(() => txStore.totalPages)
const loading = computed(() => txStore.loading)
const entities = computed(() => dashboardStore.entities)

onMounted(() => {
  dashboardStore.fetchEntities()
  txStore.fetchTransactions()
})

const applyFilters = () => {
  const params: any = { ...filters.value, page: 1 }
  // Remove empty filters
  Object.keys(params).forEach(key => {
    if (!params[key]) delete params[key]
  })
  txStore.fetchTransactions(params)
}

const resetFilters = () => {
  filters.value = {
    date_from: '',
    date_to: '',
    entity_id: undefined,
    reconciliation_status: undefined,
    tax_code: undefined,
    search: ''
  }
  txStore.fetchTransactions({ page: 1 })
}

const prevPage = () => {
  if (page.value > 1) {
    txStore.fetchTransactions({ page: page.value - 1 })
  }
}

const nextPage = () => {
  if (page.value < totalPages.value) {
    txStore.fetchTransactions({ page: page.value + 1 })
  }
}

const formatCurrency = (value: number, currency: string = 'IDR') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0
  }).format(value)
}

const reconStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    MATCHED: 'px-2 py-1 text-xs rounded-full bg-green-100 text-green-800',
    PARTIAL_MATCH: 'px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800',
    MISMATCH: 'px-2 py-1 text-xs rounded-full bg-red-100 text-red-800',
    UNRECONCILED: 'px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800',
    EXCEPTION: 'px-2 py-1 text-xs rounded-full bg-red-100 text-red-800'
  }
  return classes[status] || classes.UNRECONCILED
}

const openEditModal = (tx: Transaction) => {
  editTransaction.value = tx
}

const onTransactionSaved = () => {
  editTransaction.value = null
  applyFilters()
}
</script>
