<template>
  <div class="min-h-screen bg-gray-50">
    <Sidebar :isOpen="sidebarOpen" @close="sidebarOpen = false" />
    
    <div class="lg:pl-64">
      <TopNav @toggleSidebar="sidebarOpen = !sidebarOpen" />
      
      <main class="py-6 px-4 sm:px-6 lg:px-8">
        <Breadcrumbs />
        <router-view />
      </main>
    </div>
    
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import TopNav from '@/components/layout/TopNav.vue'
import Breadcrumbs from '@/components/layout/Breadcrumbs.vue'
import ToastContainer from '@/components/common/ToastContainer.vue'

const sidebarOpen = ref(false)
</script>
