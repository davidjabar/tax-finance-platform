import api from './index'

export const vendorsApi = {
  getList(params: { page?: number; page_size?: number; search?: string; is_active?: boolean } = {}) {
    return api.get('/vendors', { params })
  },

  getById(id: number) {
    return api.get(`/vendors/${id}`)
  }
}
