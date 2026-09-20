<template>
  <div class="space-y-6">
    <div v-if="loading" class="text-center py-8">Loading...</div>
    
    <template v-else-if="transaction">
      <div class="flex items-center space-x-4">
        <router-link to="/transactions" class="text-gray-500 hover:text-gray-700">&larr; Back</router-link>
        <h2 class="text-xl font-semibold">Transaction {{ transaction.document_number }}</h2>
      </div>

      <!-- Details -->
      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p class="text-sm text-gray-500">Document Number</p>
            <p class="font-medium">{{ transaction.document_number }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Transaction Date</p>
            <p class="font-medium">{{ transaction.transaction_date }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Vendor</p>
            <p class="font-medium">{{ transaction.vendor_name }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Entity</p>
            <p class="font-medium">{{ transaction.entity_code }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Amount</p>
            <p class="font-mono font-medium">{{ formatCurrency(transaction.amount, transaction.currency) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Tax Amount</p>
            <p class="font-mono font-medium">{{ transaction.tax_amount ? formatCurrency(transaction.tax_amount, transaction.currency) : '-' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Tax Code</p>
            <p class="font-medium">{{ transaction.tax_code || '-' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Invoice Number</p>
            <p class="font-medium">{{ transaction.invoice_number || '-' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Purchase Order</p>
            <p class="font-medium">{{ transaction.purchase_order || '-' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Payment Status</p>
            <span class="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">{{ transaction.payment_status }}</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Reconciliation Status</p>
            <span :class="reconStatusClass(transaction.reconciliation_status)">{{ transaction.reconciliation_status }}</span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Exception Status</p>
            <span :class="exceptionStatusClass(transaction.exception_status)">{{ transaction.exception_status }}</span>
          </div>
        </div>
      </div>

      <!-- Audit History -->
      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <h3 class="font-semibold mb-4">Audit History</h3>
        <div v-if="auditLoading" class="text-sm text-gray-500">Loading...</div>
        <div v-else-if="auditHistory.length === 0" class="text-sm text-gray-500">No changes recorded</div>
        <div v-else class="space-y-3">
          <div v-for="log in auditHistory" :key="log.id" class="p-3 bg-gray-50 rounded-lg">
            <div class="flex justify-between text-sm">
              <span class="font-medium">{{ log.field_name }}</span>
              <span class="text-gray-500">{{ formatDate(log.created_at) }}</span>
            </div>
            <p class="text-sm text-gray-600">
              Changed from <span class="font-mono">{{ log.old_value || '(empty)' }}</span> 
              to <span class="font-mono">{{ log.new_value || '(empty)' }}</span>
            </p>
            <p class="text-xs text-gray-400">by {{ log.user }}</p>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-8 text-red-600">Transaction not found</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useTransactionStore } from '@/stores/transactions'


const route = useRoute()
const store = useTransactionStore()

const transaction = computed(() => store.currentTransaction)
const loading = computed(() => store.loading)
const auditHistory = computed(() => store.auditHistory)
const auditLoading = ref(false)

onMounted(async () => {
  const id = parseInt(route.params.id as string)
  await store.fetchTransaction(id)
  await store.fetchAuditHistory(id)
})

const formatCurrency = (value: number, currency: string = 'IDR') => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(value)
}

const formatDate = (date: string) => new Date(date).toLocaleString()

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

const exceptionStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    NONE: 'px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800',
    OPEN: 'px-2 py-1 text-xs rounded-full bg-red-100 text-red-800',
    IN_REVIEW: 'px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800',
    RESOLVED: 'px-2 py-1 text-xs rounded-full bg-green-100 text-green-800'
  }
  return classes[status] || classes.NONE
}
</script>
