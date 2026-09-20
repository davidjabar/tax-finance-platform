import api from './index'

export const exceptionsApi = {
  getList(params: {
    page?: number
    page_size?: number
    exception_type?: string
    status?: string
    severity?: string
    search?: string
  } = {}) {
    return api.get('/exceptions', { params })
  },

  getById(id: number) {
    return api.get(`/exceptions/${id}`)
  },

  update(id: number, data: { status?: string; assigned_user?: string; notes?: string }) {
    return api.patch(`/exceptions/${id}`, data)
  },

  getStats() {
    return api.get('/exceptions/summary/stats')
  }
}
