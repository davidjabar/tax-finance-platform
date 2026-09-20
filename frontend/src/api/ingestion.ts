import api from './index'

export const ingestionApi = {
  uploadFile(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/ingestion/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  extractFromErp(entityCode: string, dateFrom: string, dateTo: string) {
    return api.post('/ingestion/extract-erp', null, {
      params: {
        entity_code: entityCode,
        date_from: dateFrom,
        date_to: dateTo
      }
    })
  }
}
