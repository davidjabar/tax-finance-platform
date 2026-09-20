import api from './index'

export const analyticsApi = {
  getTransactions(params: { date_from?: string; date_to?: string; entity_id?: number; vendor_id?: number } = {}) {
    return api.get('/analytics/transactions', { params })
  },

  getTax(params: { date_from?: string; date_to?: string; entity_id?: number } = {}) {
    return api.get('/analytics/tax', { params })
  },

  getReconciliation(params: { date_from?: string; date_to?: string } = {}) {
    return api.get('/analytics/reconciliation', { params })
  }
}
