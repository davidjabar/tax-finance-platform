<template>
  <aside
    class="fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 transform transition-transform duration-300 lg:translate-x-0"
    :class="{ '-translate-x-full': !isOpen }"
  >
    <div class="flex items-center justify-between h-16 px-4 bg-gray-800">
      <span class="text-white font-bold text-lg">Tax & Finance</span>
      <button @click="$emit('close')" class="lg:hidden text-gray-400 hover:text-white">
        <XMarkIcon class="w-6 h-6" />
      </button>
    </div>
    
    <nav class="px-2 py-4">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white rounded-md mb-1"
        :class="{ 'bg-gray-800 text-white': $route.path === item.path }"
      >
        <component :is="item.icon" class="w-5 h-5 mr-3" />
        {{ item.name }}
      </router-link>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { XMarkIcon, HomeIcon, DocumentTextIcon, UserGroupIcon, CalculatorIcon, ArrowsRightLeftIcon, ExclamationTriangleIcon, ChartBarIcon, CloudArrowUpIcon } from '@heroicons/vue/24/outline'

defineProps<{ isOpen: boolean }>()
defineEmits(['close'])

const menuItems = [
  { name: 'Dashboard', path: '/', icon: HomeIcon },
  { name: 'Transactions', path: '/transactions', icon: DocumentTextIcon },
  { name: 'Vendors', path: '/vendors', icon: UserGroupIcon },
  { name: 'Tax Transactions', path: '/tax-transactions', icon: CalculatorIcon },
  { name: 'Reconciliation', path: '/reconciliation', icon: ArrowsRightLeftIcon },
  { name: 'Exceptions', path: '/exceptions', icon: ExclamationTriangleIcon },
  { name: 'Analytics', path: '/analytics', icon: ChartBarIcon },
  { name: 'Data Ingestion', path: '/ingestion', icon: CloudArrowUpIcon }
]
</script>
