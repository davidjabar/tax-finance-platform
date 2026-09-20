import api from './index'

export const taxTransactionsApi = {
  getList(params: { page?: number; page_size?: number; tax_code?: string; tax_period?: string } = {}) {
    return api.get('/tax-transactions', { params })
  }
}
