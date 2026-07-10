# Database Schema Migration Policy

As BugHunter evolves, the internal SQLite database schema must adapt without breaking existing historical scan data.

## Rules
1. **No Silent Alterations**: Raw SQL statements executing `ALTER TABLE` directly in application code are strictly prohibited.
2. **Formal Migrations**: Schema changes must be tracked sequentially (e.g., `Migration 001`, `Migration 002`).
3. **Additive Only for v1.x**: During the v1.x lifecycle, migrations may only add tables, add columns, or create indexes. Dropping columns or changing constraints on existing columns is not allowed unless a view is provided to maintain backward compatibility.

## Implementation Details
We will utilize a lightweight migration tracking mechanism (e.g., an `alembic` integration or an internal `migrations` table) to track the applied `DATABASE_SCHEMA_VERSION`.

On startup, BugHunter checks the DB version and automatically applies pending migrations before any scan orchestration can begin.
