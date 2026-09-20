<template>
  <div class="space-y-6">
    <h2 class="text-xl font-semibold">Tax Transactions</h2>

    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tx ID</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tax Code</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tax Base</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tax Amount</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-if="loading"><td colspan="7" class="px-4 py-8 text-center">Loading...</td></tr>
          <tr v-else-if="taxTransactions.length === 0"><td colspan="7" class="px-4 py-8 text-center text-gray-500">No tax transactions</td></tr>
          <tr v-else v-for="t in taxTransactions" :key="t.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-mono text-sm">{{ t.id }}</td>
            <td class="px-4 py-3 font-mono text-sm">{{ t.transaction_id }}</td>
            <td class="px-4 py-3 text-sm">{{ t.tax_code }}</td>
            <td class="px-4 py-3 text-right font-mono text-sm">{{ formatCurrency(t.tax_base) }}</td>
            <td class="px-4 py-3 text-right font-mono text-sm">{{ formatCurrency(t.tax_amount) }}</td>
            <td class="px-4 py-3 text-sm">{{ t.tax_period }}</td>
            <td class="px-4 py-3">
              <span :class="statusClass(t.tax_status)">{{ t.tax_status }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { taxTransactionsApi } from '@/api/taxTransactions'

const taxTransactions = ref<any[]>([])
const loading = ref(false)

onMounted(() => fetchTaxTransactions())

const fetchTaxTransactions = async () => {
  loading.value = true
  try {
    const res = await taxTransactionsApi.getList({ page_size: 100 })
    taxTransactions.value = res.data.items
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const statusClass = (status: string) => {
  const classes: Record<string, string> = {
    PENDING: 'px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800',
    FILED: 'px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800',
    PAID: 'px-2 py-1 text-xs rounded-full bg-green-100 text-green-800',
    ADJUSTED: 'px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800'
  }
  return classes[status] || classes.PENDING
}

const formatCurrency = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'IDR' }).format(n)
</script>
