<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
      <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-start">
        <div>
          <h3 class="text-lg font-semibold">Exception #{{ exception.id }}</h3>
          <p class="text-sm text-gray-500">{{ exception.exception_type }}</p>
        </div>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">&times;</button>
      </div>

      <div class="p-6 space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-500">Severity</p>
            <p class="font-medium">{{ exception.severity }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Status</p>
            <p class="font-medium">{{ exception.status }}</p>
          </div>
        </div>

        <div>
          <p class="text-sm text-gray-500">Description</p>
          <p class="font-medium">{{ exception.description }}</p>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-500">Amount</p>
            <p class="font-mono">{{ exception.amount ? formatCurrency(exception.amount) : '-' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Tax Amount</p>
            <p class="font-mono">{{ exception.tax_amount ? formatCurrency(exception.tax_amount) : '-' }}</p>
          </div>
        </div>

        <div>
          <p class="text-sm text-gray-500">Transaction ID</p>
          <router-link :to="`/transactions/${exception.transaction_id}`" class="text-blue-600 hover:underline">
            View Transaction #{{ exception.transaction_id }}
          </router-link>
        </div>

        <hr />

        <div>
          <label class="label">Update Status</label>
          <select v-model="form.status" class="input">
            <option value="OPEN">Open</option>
            <option value="IN_REVIEW">In Review</option>
            <option value="RESOLVED">Resolved</option>
            <option value="IGNORED">Ignored</option>
          </select>
        </div>

        <div>
          <label class="label">Assign To</label>
          <input type="text" v-model="form.assigned_user" class="input" placeholder="User name" />
        </div>

        <div>
          <label class="label">Notes</label>
          <textarea v-model="form.notes" class="input" rows="3"></textarea>
        </div>
      </div>

      <div class="px-6 py-4 border-t border-gray-200 flex justify-end space-x-2">
        <button @click="$emit('close')" class="btn btn-secondary">Cancel</button>
        <button @click="updateException" :disabled="saving" class="btn btn-primary">
          {{ saving ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useExceptionStore } from '@/stores/exceptions'
import type { Exception } from '@/types'

const props = defineProps<{ exception: Exception }>()
const emit = defineEmits(['close', 'updated'])

const store = useExceptionStore()
const saving = ref(false)

const form = reactive({
  status: props.exception.status,
  assigned_user: props.exception.assigned_user || '',
  notes: props.exception.notes || ''
})

const updateException = async () => {
  saving.value = true
  try {
    await store.updateException(props.exception.id, { ...form })
    emit('updated')
  } catch (e) {
    console.error(e)
  } finally {
    saving.value = false
  }
}

const formatCurrency = (value: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'IDR' }).format(value)
</script>
