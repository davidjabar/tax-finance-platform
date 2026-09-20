<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-semibold">Vendors</h2>
      <input
        type="text"
        v-model="search"
        @input="debounceSearch"
        placeholder="Search vendors..."
        class="input w-64"
      />
    </div>

    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tax ID</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Country</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-if="loading"><td colspan="6" class="px-4 py-8 text-center">Loading...</td></tr>
          <tr v-else-if="vendors.length === 0"><td colspan="6" class="px-4 py-8 text-center text-gray-500">No vendors found</td></tr>
          <tr v-else v-for="v in vendors" :key="v.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-mono text-sm">{{ v.vendor_code }}</td>
            <td class="px-4 py-3 text-sm font-medium">{{ v.name }}</td>
            <td class="px-4 py-3 text-sm text-gray-500">{{ v.tax_id || '-' }}</td>
            <td class="px-4 py-3 text-sm">{{ v.country }}</td>
            <td class="px-4 py-3 text-sm">{{ v.vendor_type || '-' }}</td>
            <td class="px-4 py-3">
              <span :class="v.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'" class="px-2 py-1 text-xs rounded-full">
                {{ v.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { vendorsApi } from '@/api/vendors'

const vendors = ref<any[]>([])
const loading = ref(false)
const search = ref('')
let searchTimeout: any = null

onMounted(() => fetchVendors())

const fetchVendors = async () => {
  loading.value = true
  try {
    const res = await vendorsApi.getList({ search: search.value || undefined, page_size: 100 })
    vendors.value = res.data.items
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(fetchVendors, 300)
}
</script>
