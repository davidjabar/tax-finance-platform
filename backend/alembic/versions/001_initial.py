"""${message}

Revision ID: initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Entities
    op.create_table(
        'entities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('country', sa.String(2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_entities_code', 'entities', ['code'])
    op.create_index('ix_entities_id', 'entities', ['id'])

    # Vendors
    op.create_table(
        'vendors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vendor_code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('tax_id', sa.String(100)),
        sa.Column('country', sa.String(2), nullable=False),
        sa.Column('vendor_type', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vendor_code')
    )
    op.create_index('ix_vendors_code', 'vendors', ['vendor_code'])
    op.create_index('ix_vendors_name', 'vendors', ['name'])
    op.create_index('ix_vendors_id', 'vendors', ['id'])

    # Transactions
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_number', sa.String(100), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(18, 2)),
        sa.Column('tax_code', sa.String(20)),
        sa.Column('purchase_order', sa.String(100)),
        sa.Column('purchase_order_line', sa.Integer()),
        sa.Column('invoice_number', sa.String(100)),
        sa.Column('payment_status', sa.Enum('PENDING', 'PAID', 'PARTIAL', 'CANCELLED', name='paymentstatus')),
        sa.Column('reconciliation_status', sa.Enum('UNRECONCILED', 'MATCHED', 'PARTIAL_MATCH', 'MISMATCH', 'EXCEPTION', name='reconciliationstatus')),
        sa.Column('exception_status', sa.Enum('NONE', 'OPEN', 'IN_REVIEW', 'RESOLVED', name='exceptionstatus')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_number'),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.id'])
    )
    op.create_index('ix_transactions_id', 'transactions', ['id'])
    op.create_index('ix_transactions_document', 'transactions', ['document_number'])
    op.create_index('ix_transactions_date', 'transactions', ['transaction_date'])
    op.create_index('ix_transactions_vendor', 'transactions', ['vendor_id'])
    op.create_index('ix_transactions_entity', 'transactions', ['entity_id'])
    op.create_index('ix_transactions_tax_code', 'transactions', ['tax_code'])
    op.create_index('ix_transactions_po', 'transactions', ['purchase_order'])
    op.create_index('ix_transactions_invoice', 'transactions', ['invoice_number'])

    # Tax Transactions
    op.create_table(
        'tax_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('tax_code', sa.String(20), nullable=False),
        sa.Column('tax_base', sa.Numeric(18, 2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('tax_period', sa.String(7), nullable=False),
        sa.Column('tax_status', sa.Enum('PENDING', 'FILED', 'PAID', 'ADJUSTED', name='taxstatus')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'])
    )
    op.create_index('ix_tax_transactions_id', 'tax_transactions', ['id'])
    op.create_index('ix_tax_transactions_transaction', 'tax_transactions', ['transaction_id'])
    op.create_index('ix_tax_transactions_code', 'tax_transactions', ['tax_code'])
    op.create_index('ix_tax_transactions_period', 'tax_transactions', ['tax_period'])

    # Exceptions
    op.create_table(
        'exceptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('exception_type', sa.Enum('AMOUNT_MISMATCH', 'TAX_MISMATCH', 'MISSING_INVOICE', 'MISSING_PO', 'DUPLICATE', 'VENDOR_MISMATCH', 'TAX_CODE_MISMATCH', 'MISSING_TAX_RECORD', 'INVALID_DATA', name='exceptiontype')),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='exceptionseverity')),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2)),
        sa.Column('tax_amount', sa.Numeric(18, 2)),
        sa.Column('status', sa.Enum('OPEN', 'IN_REVIEW', 'RESOLVED', 'IGNORED', name='exceptionstatus_enum')),
        sa.Column('assigned_user', sa.String(100)),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('resolved_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'])
    )
    op.create_index('ix_exceptions_id', 'exceptions', ['id'])
    op.create_index('ix_exceptions_transaction', 'exceptions', ['transaction_id'])
    op.create_index('ix_exceptions_type', 'exceptions', ['exception_type'])
    op.create_index('ix_exceptions_status', 'exceptions', ['status'])

    # Reconciliation Runs
    op.create_table(
        'reconciliation_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', name='runstatus')),
        sa.Column('total_records', sa.Integer(), default=0),
        sa.Column('matched', sa.Integer(), default=0),
        sa.Column('partial_match', sa.Integer(), default=0),
        sa.Column('mismatch', sa.Integer(), default=0),
        sa.Column('exceptions', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reconciliation_runs_id', 'reconciliation_runs', ['id'])
    op.create_index('ix_reconciliation_runs_period_start', 'reconciliation_runs', ['period_start'])
    op.create_index('ix_reconciliation_runs_status', 'reconciliation_runs', ['status'])

    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user', sa.String(100), nullable=False),
        sa.Column('table_name', sa.String(50), nullable=False),
        sa.Column('record_id', sa.Integer(), nullable=False),
        sa.Column('field_name', sa.String(50), nullable=False),
        sa.Column('old_value', sa.Text()),
        sa.Column('new_value', sa.Text()),
        sa.Column('action', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])
    op.create_index('ix_audit_logs_user', 'audit_logs', ['user'])
    op.create_index('ix_audit_logs_table', 'audit_logs', ['table_name'])
    op.create_index('ix_audit_logs_record', 'audit_logs', ['record_id'])
    op.create_index('ix_audit_logs_created', 'audit_logs', ['created_at'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('reconciliation_runs')
    op.drop_table('exceptions')
    op.drop_table('tax_transactions')
    op.drop_table('transactions')
    op.drop_table('vendors')
    op.drop_table('entities')
