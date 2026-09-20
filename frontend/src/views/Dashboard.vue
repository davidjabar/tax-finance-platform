<template>
  <div class="space-y-6">
    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <KpiCard
        title="Total Transactions"
        :value="summary?.total_transactions || 0"
        :format="'number'"
        icon="DocumentTextIcon"
        color="blue"
      />
      <KpiCard
        title="Total Value"
        :value="summary?.total_transaction_value || 0"
        :format="'currency'"
        icon="CurrencyDollarIcon"
        color="green"
      />
      <KpiCard
        title="Total Tax Amount"
        :value="summary?.total_tax_amount || 0"
        :format="'currency'"
        icon="CalculatorIcon"
        color="purple"
      />
      <KpiCard
        title="Open Exceptions"
        :value="summary?.exceptions || 0"
        :format="'number'"
        icon="ExclamationTriangleIcon"
        color="red"
      />
    </div>

    <!-- Secondary KPIs -->
    <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <p class="text-sm text-gray-500">Reconciled</p>
        <p class="text-2xl font-semibold text-green-600">{{ summary?.reconciled_transactions || 0 }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <p class="text-sm text-gray-500">Unreconciled</p>
        <p class="text-2xl font-semibold text-yellow-600">{{ summary?.unreconciled_transactions || 0 }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <p class="text-sm text-gray-500">Pending Review</p>
        <p class="text-2xl font-semibold text-orange-600">{{ summary?.pending_review || 0 }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <p class="text-sm text-gray-500">Duplicates</p>
        <p class="text-2xl font-semibold text-red-600">{{ summary?.duplicate_transactions || 0 }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <p class="text-sm text-gray-500">Missing Data</p>
        <p class="text-2xl font-semibold text-gray-600">{{ summary?.missing_data || 0 }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <p class="text-sm text-gray-500">Recon Rate</p>
        <p class="text-2xl font-semibold text-blue-600">{{ reconRate }}%</p>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <h3 class="text-lg font-semibold mb-4">Transaction Value Trend</h3>
        <LineChart
          v-if="trends.length"
          :data="trendChartData"
          :options="trendChartOptions"
        />
        <p v-else class="text-gray-500 text-center py-8">Loading chart...</p>
      </div>

      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <h3 class="text-lg font-semibold mb-4">Top Vendors by Value</h3>
        <BarChart
          v-if="vendorDistribution.length"
          :data="vendorChartData"
          :options="vendorChartOptions"
        />
        <p v-else class="text-gray-500 text-center py-8">Loading chart...</p>
      </div>
    </div>

    <!-- More Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <h3 class="text-lg font-semibold mb-4">By Entity</h3>
        <DoughnutChart
          v-if="entityDistribution.length"
          :data="entityChartData"
          :options="{ responsive: true, plugins: { legend: { position: 'bottom' } } }"
        />
      </div>

      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <h3 class="text-lg font-semibold mb-4">Exception Types</h3>
        <DoughnutChart
          v-if="exceptionDistribution.length"
          :data="exceptionChartData"
          :options="{ responsive: true, plugins: { legend: { position: 'bottom' } } }"
        />
      </div>

      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <h3 class="text-lg font-semibold mb-4">Quick Actions</h3>
        <div class="space-y-3">
          <router-link
            to="/reconciliation"
            class="block w-full px-4 py-3 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 text-center"
          >
            Run Reconciliation
          </router-link>
          <router-link
            to="/exceptions"
            class="block w-full px-4 py-3 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 text-center"
          >
            View Exceptions ({{ summary?.exceptions || 0 }})
          </router-link>
          <router-link
            to="/ingestion"
            class="block w-full px-4 py-3 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 text-center"
          >
            Upload Data
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import KpiCard from '@/components/common/KpiCard.vue'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import DoughnutChart from '@/components/charts/DoughnutChart.vue'

const store = useDashboardStore()

onMounted(() => {
  store.fetchAll()
})

const summary = computed(() => store.summary)
const trends = computed(() => store.trends)
const vendorDistribution = computed(() => store.vendorDistribution)
const entityDistribution = computed(() => store.entityDistribution)
const exceptionDistribution = computed(() => store.exceptionDistribution)

const reconRate = computed(() => {
  if (!summary.value) return 0
  const total = summary.value.total_transactions
  const reconciled = summary.value.reconciled_transactions
  return total > 0 ? ((reconciled / total) * 100).toFixed(1) : 0
})

const trendChartData = computed(() => ({
  labels: trends.value.map((t: any) => t.date?.substring(0, 7) || ''),
  datasets: [{
    label: 'Transaction Value',
    data: trends.value.map((t: any) => t.transaction_value || 0),
    borderColor: '#3b82f6',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    fill: true
  }]
}))

const trendChartOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: { y: { beginAtZero: true } }
}

const vendorChartData = computed(() => ({
  labels: vendorDistribution.value.slice(0, 10).map((v: any) => v.vendor?.substring(0, 20) || ''),
  datasets: [{
    label: 'Value',
    data: vendorDistribution.value.slice(0, 10).map((v: any) => v.value || 0),
    backgroundColor: '#3b82f6'
  }]
}))

const vendorChartOptions = {
  responsive: true,
  indexAxis: 'y' as const,
  plugins: { legend: { display: false } }
}

const entityChartData = computed(() => ({
  labels: entityDistribution.value.map((e: any) => e.entity),
  datasets: [{
    data: entityDistribution.value.map((e: any) => e.value),
    backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
  }]
}))

const exceptionChartData = computed(() => ({
  labels: exceptionDistribution.value.map((e: any) => e.type),
  datasets: [{
    data: exceptionDistribution.value.map((e: any) => e.count),
    backgroundColor: ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6']
  }]
}))
</script>
