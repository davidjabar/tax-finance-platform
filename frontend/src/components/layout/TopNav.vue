<template>
  <header class="sticky top-0 z-40 bg-white border-b border-gray-200">
    <div class="flex items-center justify-between h-16 px-4">
      <button @click="$emit('toggleSidebar')" class="lg:hidden text-gray-500 hover:text-gray-700">
        <Bars3Icon class="w-6 h-6" />
      </button>
      
      <div class="flex-1 px-4 lg:px-0">
        <h1 class="text-lg font-semibold text-gray-900">{{ pageTitle }}</h1>
      </div>
      
      <div class="flex items-center space-x-4">
        <span class="text-sm text-gray-500">{{ currentDate }}</span>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Bars3Icon } from '@heroicons/vue/24/outline'

const emit = defineEmits(['toggleSidebar'])
const route = useRoute()

const pageTitle = computed(() => {
  return (route.name as string) || 'Dashboard'
})

const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
})
</script>
