<template>
  <div class="bg-white p-6 rounded-lg border border-gray-200">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm text-gray-500 mb-1">{{ title }}</p>
        <p class="text-3xl font-bold" :class="colorClass">{{ formattedValue }}</p>
      </div>
      <div class="p-3 rounded-full" :class="bgColorClass">
        <component :is="iconComponent" class="w-6 h-6" :class="colorClass" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  DocumentTextIcon, 
  CurrencyDollarIcon, 
  CalculatorIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/vue/24/outline'

const props = defineProps<{
  title: string
  value: number
  format: 'number' | 'currency' | 'percent'
  icon: string
  color: 'blue' | 'green' | 'red' | 'purple' | 'orange' | 'yellow'
}>()

const iconMap: Record<string, any> = {
  DocumentTextIcon,
  CurrencyDollarIcon,
  CalculatorIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon
}

const colorMap: Record<string, { text: string; bg: string }> = {
  blue: { text: 'text-blue-600', bg: 'bg-blue-50' },
  green: { text: 'text-green-600', bg: 'bg-green-50' },
  red: { text: 'text-red-600', bg: 'bg-red-50' },
  purple: { text: 'text-purple-600', bg: 'bg-purple-50' },
  orange: { text: 'text-orange-600', bg: 'bg-orange-50' },
  yellow: { text: 'text-yellow-600', bg: 'bg-yellow-50' }
}

const iconComponent = computed(() => iconMap[props.icon] || DocumentTextIcon)
const colorClass = computed(() => colorMap[props.color]?.text || 'text-gray-600')
const bgColorClass = computed(() => colorMap[props.color]?.bg || 'bg-gray-50')

const formattedValue = computed(() => {
  if (props.format === 'currency') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(props.value)
  }
  if (props.format === 'percent') {
    return `${props.value.toFixed(1)}%`
  }
  return new Intl.NumberFormat('en-US').format(props.value)
})
</script>
