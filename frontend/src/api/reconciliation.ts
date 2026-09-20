import api from './index'

export const reconciliationApi = {
  run(data: { period_start: string; period_end: string }) {
    return api.post('/reconciliation/run', data)
  },

  getRuns(params: { page?: number; page_size?: number } = {}) {
    return api.get('/reconciliation/runs', { params })
  },

  getRunById(id: number) {
    return api.get(`/reconciliation/runs/${id}`)
  },

  getResults(id: number, params: { page?: number; page_size?: number; match_result?: string } = {}) {
    return api.get(`/reconciliation/runs/${id}/results`, { params })
  }
}
