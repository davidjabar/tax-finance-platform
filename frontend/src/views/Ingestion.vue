<template>
  <div class="space-y-6">
    <h2 class="text-xl font-semibold">Data Ingestion</h2>

    <!-- Upload Section -->
    <div class="bg-white p-6 rounded-lg border border-gray-200">
      <h3 class="text-lg font-semibold mb-4">Upload File</h3>
      <p class="text-sm text-gray-600 mb-4">
        Upload CSV or Excel files containing transaction data. 
        Required columns: document_number, transaction_date, vendor_code, entity_code, currency, amount
      </p>

      <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <input
          type="file"
          ref="fileInput"
          @change="handleFileSelect"
          accept=".csv,.xlsx,.xls"
          class="hidden"
        />
        <CloudArrowUpIcon class="mx-auto h-12 w-12 text-gray-400" />
        <p class="mt-2 text-sm text-gray-600">
          <button @click="triggerFileInput" class="text-blue-600 hover:underline">
            Click to upload
          </button>
          or drag and drop
        </p>
        <p class="text-xs text-gray-500">CSV, XLSX, XLS up to 10MB</p>
      </div>

      <div v-if="selectedFile" class="mt-4 p-4 bg-gray-50 rounded-lg">
        <p class="text-sm font-medium">{{ selectedFile.name }}</p>
        <p class="text-xs text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
        <div class="mt-2 flex space-x-2">
          <button @click="uploadFile" :disabled="uploading" class="btn btn-primary">
            {{ uploading ? 'Uploading...' : 'Upload & Process' }}
          </button>
          <button @click="selectedFile = null" class="btn btn-secondary">Cancel</button>
        </div>
      </div>

      <div v-if="uploadResult" class="mt-4 p-4 rounded-lg" :class="uploadResult.status === 'COMPLETED' ? 'bg-green-50' : 'bg-red-50'">
        <h4 class="font-medium mb-2">{{ uploadResult.status }}</h4>
        <p class="text-sm text-gray-600">{{ uploadResult.message }}</p>
        <div class="mt-2 grid grid-cols-4 gap-4 text-sm">
          <div>
            <p class="text-gray-500">Total</p>
            <p class="font-medium">{{ uploadResult.total_rows }}</p>
          </div>
          <div>
            <p class="text-gray-500">Valid</p>
            <p class="font-medium text-green-600">{{ uploadResult.valid_rows }}</p>
          </div>
          <div>
            <p class="text-gray-500">Invalid</p>
            <p class="font-medium text-red-600">{{ uploadResult.invalid_rows }}</p>
          </div>
          <div>
            <p class="text-gray-500">Duplicates</p>
            <p class="font-medium text-yellow-600">{{ uploadResult.duplicate_rows }}</p>
          </div>
        </div>
        <div v-if="uploadResult.errors?.length" class="mt-4">
          <p class="text-sm font-medium text-red-600">Errors:</p>
          <ul class="text-xs text-red-500 list-disc list-inside">
            <li v-for="(err, i) in uploadResult.errors.slice(0, 5)" :key="i">{{ err }}</li>
            <li v-if="uploadResult.errors.length > 5">...and {{ uploadResult.errors.length - 5 }} more</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- ERP Extract -->
    <div class="bg-white p-6 rounded-lg border border-gray-200">
      <h3 class="text-lg font-semibold mb-4">Extract from ERP</h3>
      <p class="text-sm text-gray-600 mb-4">
        Simulate data extraction from ERP system. In production, this would connect to actual ERP.
      </p>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
        <div>
          <label class="label">Entity</label>
          <select v-model="erpEntity" class="input">
            <option v-for="e in entities" :key="e.id" :value="e.code">{{ e.code }} - {{ e.name }}</option>
          </select>
        </div>
        <div>
          <label class="label">From</label>
          <input type="date" v-model="erpDateFrom" class="input" />
        </div>
        <div>
          <label class="label">To</label>
          <input type="date" v-model="erpDateTo" class="input" />
        </div>
        <button @click="extractFromErp" :disabled="extracting" class="btn btn-primary">
          {{ extracting ? 'Extracting...' : 'Extract' }}
        </button>
      </div>

      <div v-if="erpResult" class="mt-4 p-4 bg-blue-50 rounded-lg">
        <p class="text-sm">{{ erpResult.message }}</p>
        <p class="text-xs text-gray-500">Records: {{ erpResult.records }}</p>
      </div>
    </div>

    <!-- Pipeline Info -->
    <div class="bg-white p-6 rounded-lg border border-gray-200">
      <h3 class="text-lg font-semibold mb-4">Ingestion Pipeline</h3>
      <div class="flex items-center space-x-4 text-sm">
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-medium">1</div>
          <span>Extract</span>
        </div>
        <ChevronRightIcon class="w-4 h-4 text-gray-400" />
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-medium">2</div>
          <span>Validate</span>
        </div>
        <ChevronRightIcon class="w-4 h-4 text-gray-400" />
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-medium">3</div>
          <span>Transform</span>
        </div>
        <ChevronRightIcon class="w-4 h-4 text-gray-400" />
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-medium">4</div>
          <span>Load</span>
        </div>
        <ChevronRightIcon class="w-4 h-4 text-gray-400" />
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center font-medium">✓</div>
          <span>Complete</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ingestionApi } from '@/api/ingestion'
import { dashboardApi } from '@/api/dashboard'
import { CloudArrowUpIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'
import type { Entity } from '@/types'

const entities = ref<Entity[]>([])
const fileInput = ref()
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const uploadResult = ref<any>(null)

const erpEntity = ref('')
const erpDateFrom = ref('')
const erpDateTo = ref('')
const extracting = ref(false)
const erpResult = ref<any>(null)

onMounted(async () => {
  const res = await dashboardApi.getEntities()
  entities.value = res.data.items
  if (entities.value.length > 0) {
    erpEntity.value = entities.value[0].code
  }
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) return
  uploading.value = true
  uploadResult.value = null
  try {
    const res = await ingestionApi.uploadFile(selectedFile.value)
    uploadResult.value = res.data
    selectedFile.value = null
  } catch (e: any) {
    uploadResult.value = { status: 'FAILED', message: e.response?.data?.detail || 'Upload failed', errors: [] }
  } finally {
    uploading.value = false
  }
}

const extractFromErp = async () => {
  extracting.value = true
  erpResult.value = null
  try {
    const res = await ingestionApi.extractFromErp(erpEntity.value, erpDateFrom.value, erpDateTo.value)
    erpResult.value = res.data
  } catch (e: any) {
    erpResult.value = { status: 'FAILED', message: e.response?.data?.detail || 'Extraction failed' }
  } finally {
    extracting.value = false
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>
