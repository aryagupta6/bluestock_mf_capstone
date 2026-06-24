# SQL Schema Directory

This folder contains the DDL schema file defining the SQLite relational database structure.

## File Description

- **`schema.sql`**:
  - Implements a relational star schema structure.
  - Declares primary keys, foreign key constraints (with cascade deletions/set null policies), and column data types.
  - Defines the core tables: `dim_fund` (dimension table), and fact tables `fact_nav`, `fact_transactions`, `fact_performance`, `fact_portfolio_holdings`, and `fact_benchmark`.
  - Creates indexes on `nav_date`, `amfi_code`, and `transaction_date` to accelerate analytical filters and joins.
