# Tax & Finance Automation Platform

An internal enterprise analytics and automation system for Finance and Tax teams.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vue 3)                        │
│  Dashboard │ Transactions │ Reconciliation │ Exceptions      │
│  Analytics │ Ingestion │ Vendors │ Tax Transactions          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  API Layer │ Services │ Repositories │ Models                │
│  Reconciliation Engine │ Ingestion Pipeline │ Analytics      │
└────────────────────────┬────────────────────────────────────┘
                         │ SQLAlchemy
┌────────────────────────▼────────────────────────────────────┐
│                   PostgreSQL Database                        │
│  Entities │ Vendors │ Transactions │ Tax Transactions       │
│  Exceptions │ Reconciliation Runs │ Audit Logs              │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- Python 3.11
- FastAPI - Web framework
- SQLAlchemy - ORM
- PostgreSQL - Database
- Alembic - Migrations
- Pydantic - Validation
- Pandas - Data processing

### Frontend
- Vue 3 - UI framework
- TypeScript
- Vite - Build tool
- Tailwind CSS - Styling
- Vue Router - Routing
- Pinia - State management
- Chart.js - Charts
- Axios - HTTP client

## Project Structure

```
tax-finance-platform/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routes
│   │   ├── core/             # Config, database
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── repositories/     # Data access
│   │   ├── reconciliation/   # Reconciliation engine
│   │   ├── ingestion/        # Data ingestion pipeline
│   │   └── db/               # Seed data
│   ├── tests/                # Test files
│   ├── alembic/              # Migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # Vue components
│   │   ├── views/            # Page views
│   │   ├── stores/           # Pinia stores
│   │   ├── router/           # Vue Router
│   │   └── types/            # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Database Schema

### Core Tables

- **entities** - Company codes / legal entities
- **vendors** - Supplier/vendor master data
- **transactions** - Financial transactions from ERP
- **tax_transactions** - Tax records for transactions
- **exceptions** - Reconciliation exceptions
- **reconciliation_runs** - Reconciliation execution history
- **audit_logs** - Change history for audit trail

### Key Relationships

```
Entity (1) ──── (N) Transaction
Vendor (1) ──── (N) Transaction
Transaction (1) ──── (1) TaxTransaction
Transaction (1) ──── (N) Exception
```

## API Overview

### Dashboard
- `GET /api/dashboard/summary` - KPI summary
- `GET /api/dashboard/trends` - Transaction trends

### Transactions
- `GET /api/transactions` - List transactions (paginated, filterable)
- `GET /api/transactions/{id}` - Get transaction
- `PATCH /api/transactions/{id}` - Update transaction
- `GET /api/transactions/{id}/audit` - Audit history

### Reconciliation
- `POST /api/reconciliation/run` - Run reconciliation
- `GET /api/reconciliation/runs` - List runs
- `GET /api/reconciliation/runs/{id}/results` - Get results

### Exceptions
- `GET /api/exceptions` - List exceptions
- `PATCH /api/exceptions/{id}` - Update exception

### Analytics
- `GET /api/analytics/transactions` - Transaction analytics
- `GET /api/analytics/tax` - Tax analytics
- `GET /api/analytics/reconciliation` - Reconciliation analytics

### Ingestion
- `POST /api/ingestion/upload` - Upload CSV/Excel

## Local Development Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### Running with Docker

```bash
# Clone and start
cd tax-finance-platform
docker compose up --build

# Services:
# - Frontend: http://localhost
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Database: localhost:5432
```

### Manual Setup

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set environment
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tax_finance

# Run migrations
alembic upgrade head

# Seed data
python -m app.db.seed

# Start server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

## How Reconciliation Works

The reconciliation engine compares transactions across data sources:

1. **Load Transactions** - Fetch transactions for the selected period
2. **Check Duplicates** - Identify duplicate document numbers
3. **Validate Vendors** - Ensure vendor exists and is active
4. **Match Tax Records** - Compare transaction tax amounts with tax records
5. **Check Purchase Orders** - Validate PO references
6. **Detect Missing Data** - Find missing invoices, POs, etc.
7. **Create Exceptions** - Generate exception records for mismatches

### Match Results

- **MATCHED** - All validations passed
- **PARTIAL_MATCH** - Minor issues (missing invoice, etc.)
- **TAX_MISMATCH** - Tax amount/code differs
- **DUPLICATE** - Duplicate document number
- **EXCEPTION** - Significant issues requiring review

## Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## Seed Data

The seed script creates:
- 5 entities (company codes)
- 25 vendors
- 5,000+ transactions
- Tax transaction records
- Intentional exceptions (duplicates, mismatches)

```bash
cd backend
python -m app.db.seed
```

## Future Architecture Considerations

The platform is designed for extensibility:

- **Background Workers** - Celery/Redis for async processing
- **ERP Connectors** - Modular connectors for SAP, Oracle, etc.
- **Object Storage** - S3 for file uploads
- **ML Services** - Anomaly detection, auto-reconciliation
- **RBAC** - Role-based access control
- **SSO** - Single sign-on integration
- **Multi-tenancy** - Support for multiple organizations

## Key Features

### Dashboard
- KPIs: Total transactions, value, tax, exceptions
- Trend charts: Transaction value over time
- Distribution charts: By vendor, entity, exception type

### Data Management
- Filterable, sortable, paginated tables
- Editable data grid with validation
- Audit trail for all changes

### Reconciliation
- Period-based reconciliation runs
- Visual workflow
- Exception detection and management
- Re-run after corrections

### Exception Management
- Filter by type, severity, status
- Assign users, add notes
- Track resolution

### Analytics
- Transaction analytics with trends
- Tax analytics by code, entity, period
- Reconciliation performance metrics

### Data Ingestion
- CSV/Excel upload
- Validation and error reporting
- Pipeline visualization
- Mock ERP extraction

## License

MIT
