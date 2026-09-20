<template>
  <div class="space-y-6">
    <h2 class="text-xl font-semibold">Analytics</h2>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg border border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
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
        <div class="flex items-end">
          <button @click="fetchAnalytics" class="btn btn-primary">Apply Filters</button>
        </div>
      </div>
    </div>

    <!-- Transaction Analytics -->
    <div class="bg-white p-6 rounded-lg border border-gray-200">
      <h3 class="text-lg font-semibold mb-4">Transaction Analytics</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="p-4 bg-blue-50 rounded-lg">
          <p class="text-sm text-gray-600">Total Volume</p>
          <p class="text-2xl font-bold text-blue-600">{{ formatNumber(txAnalytics.total_volume) }}</p>
        </div>
        <div class="p-4 bg-green-50 rounded-lg">
          <p class="text-sm text-gray-600">Total Value</p>
          <p class="text-2xl font-bold text-green-600">{{ formatCurrency(txAnalytics.total_value) }}</p>
        </div>
        <div class="p-4 bg-purple-50 rounded-lg">
          <p class="text-sm text-gray-600">Average Value</p>
          <p class="text-2xl font-bold text-purple-600">{{ formatCurrency(txAnalytics.average_value) }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h4 class="font-medium mb-2">Monthly Trend</h4>
          <LineChart v-if="txAnalytics.monthly_trend?.length" :data="monthlyTrendData" :options="{ responsive: true }" />
        </div>
        <div>
          <h4 class="font-medium mb-2">Top Vendors</h4>
          <BarChart v-if="txAnalytics.vendor_concentration?.length" :data="vendorConcentrationData" :options="{ responsive: true, indexAxis: 'y' }" />
        </div>
      </div>
    </div>

    <!-- Tax Analytics -->
    <div class="bg-white p-6 rounded-lg border border-gray-200">
      <h3 class="text-lg font-semibold mb-4">Tax Analytics</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 class="font-medium mb-2">Tax by Code</h4>
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Code</th>
                <th class="px-4 py-2 text-right text-xs font-medium text-gray-500">Base</th>
                <th class="px-4 py-2 text-right text-xs font-medium text-gray-500">Tax</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="t in taxAnalytics.tax_by_code" :key="t.tax_code">
                <td class="px-4 py-2 text-sm font-medium">{{ t.tax_code }}</td>
                <td class="px-4 py-2 text-right font-mono text-sm">{{ formatCurrency(t.tax_base) }}</td>
                <td class="px-4 py-2 text-right font-mono text-sm">{{ formatCurrency(t.tax_amount) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div>
          <h4 class="font-medium mb-2">Effective Tax Rate</h4>
          <p class="text-4xl font-bold text-blue-600 mb-4">{{ taxAnalytics.effective_tax_rate?.toFixed(2) || 0 }}%</p>
          <h4 class="font-medium mb-2">Tax by Period</h4>
          <BarChart v-if="taxAnalytics.tax_by_period?.length" :data="taxByPeriodData" :options="{ responsive: true }" />
        </div>
      </div>
    </div>

    <!-- Reconciliation Analytics -->
    <div class="bg-white p-6 rounded-lg border border-gray-200">
      <h3 class="text-lg font-semibold mb-4">Reconciliation Analytics</h3>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="p-4 bg-green-50 rounded-lg">
          <p class="text-sm text-gray-600">Reconciliation Rate</p>
          <p class="text-2xl font-bold text-green-600">{{ reconAnalytics.reconciliation_rate?.toFixed(1) || 0 }}%</p>
        </div>
        <div class="p-4 bg-red-50 rounded-lg">
          <p class="text-sm text-gray-600">Exception Rate</p>
          <p class="text-2xl font-bold text-red-600">{{ reconAnalytics.exception_rate?.toFixed(1) || 0 }}%</p>
        </div>
        <div class="p-4 bg-orange-50 rounded-lg">
          <p class="text-sm text-gray-600">Mismatch Rate</p>
          <p class="text-2xl font-bold text-orange-600">{{ reconAnalytics.mismatch_rate?.toFixed(1) || 0 }}%</p>
        </div>
        <div class="p-4 bg-yellow-50 rounded-lg">
          <p class="text-sm text-gray-600">Unresolved Exceptions</p>
          <p class="text-2xl font-bold text-yellow-600">{{ reconAnalytics.unresolved_exceptions || 0 }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { analyticsApi } from '@/api/analytics'
import { dashboardApi } from '@/api/dashboard'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import type { Entity } from '@/types'

const entities = ref<Entity[]>([])
const filters = reactive({
  date_from: '',
  date_to: '',
  entity_id: undefined as number | undefined
})

const txAnalytics = ref<any>({})
const taxAnalytics = ref<any>({})
const reconAnalytics = ref<any>({})

onMounted(async () => {
  const res = await dashboardApi.getEntities()
  entities.value = res.data.items
  fetchAnalytics()
})

const fetchAnalytics = async () => {
  const params: any = { ...filters }
  Object.keys(params).forEach(k => { if (!params[k]) delete params[k] })

  const [tx, tax, recon] = await Promise.all([
    analyticsApi.getTransactions(params),
    analyticsApi.getTax(params),
    analyticsApi.getReconciliation(params)
  ])

  txAnalytics.value = tx.data
  taxAnalytics.value = tax.data
  reconAnalytics.value = recon.data
}

const monthlyTrendData = computed(() => ({
  labels: txAnalytics.value.monthly_trend?.map((t: any) => t.month) || [],
  datasets: [{
    label: 'Value',
    data: txAnalytics.value.monthly_trend?.map((t: any) => t.value) || [],
    borderColor: '#3b82f6',
    fill: false
  }]
}))

const vendorConcentrationData = computed(() => ({
  labels: txAnalytics.value.vendor_concentration?.slice(0, 5).map((v: any) => v.vendor?.substring(0, 15)) || [],
  datasets: [{
    label: 'Value',
    data: txAnalytics.value.vendor_concentration?.slice(0, 5).map((v: any) => v.value) || [],
    backgroundColor: '#10b981'
  }]
}))

const taxByPeriodData = computed(() => ({
  labels: taxAnalytics.value.tax_by_period?.map((t: any) => t.period) || [],
  datasets: [{
    label: 'Tax Amount',
    data: taxAnalytics.value.tax_by_period?.map((t: any) => t.tax_amount) || [],
    backgroundColor: '#8b5cf6'
  }]
}))

const formatNumber = (n: number) => new Intl.NumberFormat('en-US').format(n)
const formatCurrency = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'IDR' }).format(n)
</script>
