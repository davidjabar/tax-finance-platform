import api from './index'
import type { TransactionFilters } from '@/types'

export const transactionsApi = {
  getList(params: TransactionFilters) {
    return api.get('/transactions', { params })
  },

  getById(id: number) {
    return api.get(`/transactions/${id}`)
  },

  update(id: number, data: Record<string, any>) {
    return api.patch(`/transactions/${id}`, data)
  },

  getAuditHistory(id: number) {
    return api.get(`/transactions/${id}/audit`)
  }
}
