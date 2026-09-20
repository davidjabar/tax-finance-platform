export interface Transaction {
  id: number
  document_number: string
  transaction_date: string
  vendor_id: number
  vendor_name?: string
  entity_id: number
  entity_code?: string
  currency: string
  amount: number
  tax_amount?: number
  tax_code?: string
  purchase_order?: string
  purchase_order_line?: number
  invoice_number?: string
  payment_status: string
  reconciliation_status: string
  exception_status: string
  created_at: string
  updated_at?: string
}

export interface TransactionFilters {
  page?: number
  page_size?: number
  date_from?: string
  date_to?: string
  vendor_id?: number
  entity_id?: number
  tax_code?: string
  currency?: string
  reconciliation_status?: string
  exception_status?: string
  search?: string
  sort_by?: string
  sort_order?: string
}

export interface Vendor {
  id: number
  vendor_code: string
  name: string
  tax_id?: string
  country: string
  vendor_type?: string
  is_active: boolean
}

export interface Exception {
  id: number
  transaction_id: number
  exception_type: string
  severity: string
  description: string
  amount?: number
  tax_amount?: number
  status: string
  assigned_user?: string
  notes?: string
  created_at: string
  resolved_at?: string
}

export interface ReconciliationRun {
  id: number
  period_start: string
  period_end: string
  status: string
  total_records: number
  matched: number
  partial_match: number
  mismatch: number
  exceptions: number
  created_at: string
  completed_at?: string
}

export interface DashboardSummary {
  total_transactions: number
  total_transaction_value: number
  total_tax_amount: number
  reconciled_transactions: number
  unreconciled_transactions: number
  exceptions: number
  missing_data: number
  duplicate_transactions: number
  pending_review: number
}

export interface Entity {
  id: number
  code: string
  name: string
  country: string
}
