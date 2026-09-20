import api from './index'

export const dashboardApi = {
  getSummary() {
    return api.get('/dashboard/summary')
  },

  getTrends(months: number = 12) {
    return api.get('/dashboard/trends', { params: { months } })
  },

  getVendorDistribution(limit: number = 10) {
    return api.get('/dashboard/vendor-distribution', { params: { limit } })
  },

  getEntityDistribution() {
    return api.get('/dashboard/entity-distribution')
  },

  getExceptionDistribution() {
    return api.get('/dashboard/exception-distribution')
  },

  getEntities() {
    return api.get('/entities')
  }
}
