import { defineStore } from 'pinia'
import { exceptionsApi } from '@/api/exceptions'
import type { Exception } from '@/types'

export const useExceptionStore = defineStore('exceptions', {
  state: () => ({
    exceptions: [] as Exception[],
    currentException: null as Exception | null,
    stats: null as any,
    total: 0,
    page: 1,
    pageSize: 50,
    totalPages: 0,
    loading: false,
    error: null as string | null
  }),

  actions: {
    async fetchExceptions(params: any = {}) {
      try {
        this.loading = true
        const response = await exceptionsApi.getList({
          page: params.page || this.page,
          page_size: params.page_size || this.pageSize,
          ...params
        })
        this.exceptions = response.data.items
        this.total = response.data.total
        this.page = response.data.page
        this.pageSize = response.data.page_size
        this.totalPages = response.data.total_pages
      } catch (error: any) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async fetchException(id: number) {
      try {
        this.loading = true
        const response = await exceptionsApi.getById(id)
        this.currentException = response.data
      } catch (error: any) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async updateException(id: number, data: { status?: string; assigned_user?: string; notes?: string }) {
      try {
        this.loading = true
        const response = await exceptionsApi.update(id, data)
        return response.data
      } catch (error: any) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchStats() {
      try {
        const response = await exceptionsApi.getStats()
        this.stats = response.data
      } catch (error: any) {
        this.error = error.message
      }
    }
  }
})
