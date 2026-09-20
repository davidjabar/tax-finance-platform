import { defineStore } from 'pinia'
import { dashboardApi } from '@/api/dashboard'
import type { DashboardSummary, Entity } from '@/types'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    summary: null as DashboardSummary | null,
    trends: [] as any[],
    vendorDistribution: [] as any[],
    entityDistribution: [] as any[],
    exceptionDistribution: [] as any[],
    entities: [] as Entity[],
    loading: false,
    error: null as string | null
  }),

  actions: {
    async fetchSummary() {
      try {
        this.loading = true
        const response = await dashboardApi.getSummary()
        this.summary = response.data
      } catch (error: any) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async fetchTrends(months: number = 12) {
      try {
        const response = await dashboardApi.getTrends(months)
        this.trends = response.data.trends
      } catch (error: any) {
        this.error = error.message
      }
    },

    async fetchVendorDistribution(limit: number = 10) {
      try {
        const response = await dashboardApi.getVendorDistribution(limit)
        this.vendorDistribution = response.data
      } catch (error: any) {
        this.error = error.message
      }
    },

    async fetchEntityDistribution() {
      try {
        const response = await dashboardApi.getEntityDistribution()
        this.entityDistribution = response.data
      } catch (error: any) {
        this.error = error.message
      }
    },

    async fetchExceptionDistribution() {
      try {
        const response = await dashboardApi.getExceptionDistribution()
        this.exceptionDistribution = response.data
      } catch (error: any) {
        this.error = error.message
      }
    },

    async fetchEntities() {
      try {
        const response = await dashboardApi.getEntities()
        this.entities = response.data.items
      } catch (error: any) {
        this.error = error.message
      }
    },

    async fetchAll() {
      await Promise.all([
        this.fetchSummary(),
        this.fetchTrends(),
        this.fetchVendorDistribution(),
        this.fetchEntityDistribution(),
        this.fetchExceptionDistribution(),
        this.fetchEntities()
      ])
    }
  }
})
