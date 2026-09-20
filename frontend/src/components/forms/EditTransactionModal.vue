<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold">Edit Transaction</h3>
        <p class="text-sm text-gray-500">{{ transaction.document_number }}</p>
      </div>

      <form @submit.prevent="saveTransaction" class="p-6 space-y-4">
        <div>
          <label class="label">Tax Code</label>
          <select v-model="form.tax_code" class="input">
            <option v-for="code in taxCodes" :key="code" :value="code">{{ code }}</option>
          </select>
        </div>

        <div>
          <label class="label">Invoice Number</label>
          <input type="text" v-model="form.invoice_number" class="input" />
        </div>

        <div>
          <label class="label">Purchase Order</label>
          <input type="text" v-model="form.purchase_order" class="input" />
        </div>

        <div>
          <label class="label">Reconciliation Status</label>
          <select v-model="form.reconciliation_status" class="input">
            <option value="UNRECONCILED">Unreconciled</option>
            <option value="MATCHED">Matched</option>
            <option value="PARTIAL_MATCH">Partial Match</option>
            <option value="MISMATCH">Mismatch</option>
            <option value="EXCEPTION">Exception</option>
          </select>
        </div>

        <div>
          <label class="label">Exception Status</label>
          <select v-model="form.exception_status" class="input">
            <option value="NONE">None</option>
            <option value="OPEN">Open</option>
            <option value="IN_REVIEW">In Review</option>
            <option value="RESOLVED">Resolved</option>
          </select>
        </div>

        <div v-if="error" class="text-red-600 text-sm">{{ error }}</div>
        <div v-if="success" class="text-green-600 text-sm">Transaction updated successfully!</div>
      </form>

      <div class="px-6 py-4 border-t border-gray-200 flex justify-end space-x-2">
        <button type="button" @click="$emit('close')" class="btn btn-secondary">Cancel</button>
        <button type="button" @click="saveTransaction" :disabled="saving" class="btn btn-primary">
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useTransactionStore } from '@/stores/transactions'
import type { Transaction } from '@/types'

const props = defineProps<{ transaction: Transaction }>()
const emit = defineEmits(['close', 'saved'])

const txStore = useTransactionStore()

const taxCodes = ['PPN11', 'PPN12', 'PPN10', 'PPN0', 'PPNBM', 'EXEMPT']

const form = reactive({
  tax_code: props.transaction.tax_code || '',
  invoice_number: props.transaction.invoice_number || '',
  purchase_order: props.transaction.purchase_order || '',
  reconciliation_status: props.transaction.reconciliation_status,
  exception_status: props.transaction.exception_status
})

const saving = ref(false)
const error = ref('')
const success = ref(false)

const saveTransaction = async () => {
  saving.value = true
  error.value = ''
  success.value = false

  try {
    await txStore.updateTransaction(props.transaction.id, { ...form })
    success.value = true
    setTimeout(() => {
      emit('saved')
    }, 1000)
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to save transaction'
  } finally {
    saving.value = false
  }
}
</script>
