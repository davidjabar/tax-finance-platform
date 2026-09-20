import { defineStore } from 'pinia'
import { transactionsApi } from '@/api/transactions'
import type { Transaction, TransactionFilters } from '@/types'

export const useTransactionStore = defineStore('transactions', {
  state: () => ({
    transactions: [] as Transaction[],
    currentTransaction: null as Transaction | null,
    auditHistory: [] as any[],
    total: 0,
    page: 1,
    pageSize: 50,
    totalPages: 0,
    loading: false,
    error: null as string | null
  }),

  actions: {
    async fetchTransactions(filters: TransactionFilters = {}) {
      try {
        this.loading = true
        const params = {
          page: filters.page || this.page,
          page_size: filters.page_size || this.pageSize,
          ...filters
        }
        const response = await transactionsApi.getList(params)
        this.transactions = response.data.items
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

    async fetchTransaction(id: number) {
      try {
        this.loading = true
        const response = await transactionsApi.getById(id)
        this.currentTransaction = response.data
      } catch (error: any) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async updateTransaction(id: number, data: Record<string, any>) {
      try {
        this.loading = true
        const response = await transactionsApi.update(id, data)
        this.currentTransaction = response.data
        return response.data
      } catch (error: any) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchAuditHistory(id: number) {
      try {
        const response = await transactionsApi.getAuditHistory(id)
        this.auditHistory = response.data
      } catch (error: any) {
        this.error = error.message
      }
    }
  }
})
