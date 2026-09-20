<template>
  <nav v-if="breadcrumbs.length > 1" class="mb-4">
    <ol class="flex items-center space-x-2 text-sm">
      <li v-for="(crumb, index) in breadcrumbs" :key="crumb.path">
        <router-link
          v-if="index < breadcrumbs.length - 1"
          :to="crumb.path"
          class="text-gray-500 hover:text-gray-700"
        >
          {{ crumb.name }}
        </router-link>
        <span v-else class="text-gray-900 font-medium">{{ crumb.name }}</span>
        <span v-if="index < breadcrumbs.length - 1" class="mx-2 text-gray-400">/</span>
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const breadcrumbs = computed(() => {
  const crumbs: { name: string; path: string }[] = [{ name: 'Dashboard', path: '/' }]
  
  if (route.path !== '/') {
    crumbs.push({ name: route.name as string, path: route.path })
  }
  
  return crumbs
})
</script>
