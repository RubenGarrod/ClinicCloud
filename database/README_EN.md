# Database - ClinicCloud

**[🇬🇧 English](README_EN.md)** | **[🇪🇸 Español](README.md)**

---

## Description

This directory contains all database schemas and configurations for ClinicCloud.

## File Structure

### Main Files

- **`consolidated_schema.sql`** - **USE THIS FOR NEW INSTALLATIONS**
  - Complete consolidated schema
  - Includes all tables, indexes, and functions
  - Recommended for new deployments

- **`init.sql`** - Initial medical documents schema
  - `documento` and `categoria` tables
  - Vector extension for semantic search

- **`auth_schema.sql`** - Authentication schema (obsolete, see consolidated_schema.sql)
  - `auth.users` table
  - Basic authentication system

### Migrations Directory

`migrations/` - History of incremental schema changes

- `001_user_preferences_and_history.sql` - Preferences and history
- `002_add_location_fields.sql` - Location fields
- `003_add_user_preferences.sql` - Preferences table
- `004_add_password_reset_tokens.sql` - Recovery tokens
- `005_add_search_history_and_favorites.sql` - History and favorites
- `apply_migration.py` - Script to apply migrations

## Usage

### For New Installation

If you're setting up ClinicCloud from scratch:

```bash
# 1. Create the database
createdb cliniccloud

# 2. Apply the consolidated schema
psql -U postgres -d cliniccloud -f database/consolidated_schema.sql
```

### For Existing Database

If you already have an installation and need to update it:

```bash
# Apply pending migrations
cd database/migrations
python apply_migration.py
```

### With Docker

The schema is automatically applied when starting containers:

```bash
docker-compose up -d
```

## Database Schema

### PostgreSQL Schemas

1. **`public`** - Medical documents and general data
   - `categoria` - Medical specialties
   - `documento` - Indexed scientific articles
   - `search_history` - Search history
   - `favorites` - Documents saved by users

2. **`auth`** - Authentication system
   - `users` - Registered users
   - `user_preferences` - Custom preferences
   - `password_reset_tokens` - Recovery tokens

### Required Extensions

- **pgvector** - Semantic vector search
  ```sql
  CREATE EXTENSION vector;
  ```

## Maintenance

### Clean Expired Tokens

```sql
SELECT auth.cleanup_expired_tokens();
```

### Verify Integrity

```sql
-- Verify created tables
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema IN ('public', 'auth')
ORDER BY table_schema, table_name;

-- Verify indexes
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname IN ('public', 'auth')
ORDER BY tablename;
```

### Backup

```bash
# Complete backup
pg_dump -U postgres cliniccloud > backup_$(date +%Y%m%d).sql

# Schema-only backup
pg_dump -U postgres --schema-only cliniccloud > schema_backup.sql

# Data-only backup
pg_dump -U postgres --data-only cliniccloud > data_backup.sql
```

## Change History

| Version | Date | Description |
|---------|------|-------------|
| 5.0 | 2025-10-16 | Consolidated schema created |
| 4.0 | 2025-10-10 | Added history and favorites |
| 3.0 | 2025-10-09 | Added reset tokens |
| 2.0 | 2025-10-08 | Added user preferences |
| 1.0 | 2025-08-02 | Initial authentication schema |
| 0.1 | 2025-05-13 | Medical documents schema |

## Security

- Passwords are stored with bcrypt hash
- Reset tokens expire in 1 hour
- Unique email constraint
- Cascade deletes configured appropriately
- Indexes on sensitive fields to prevent timing attacks

## Additional Documentation

- [Migrations](migrations/README.md) - Detailed migration guide
- [Data Model](../docs/database-model.md) - ER Diagram (if exists)

## Important Notes

1. **Do not edit** `consolidated_schema.sql` directly
2. **Create new migrations** for incremental changes
3. **Test migrations** in development before production
4. **Make backup** before applying migrations in production
5. **Historical migrations** are kept for reference

---

**Copyright (C) 2025 Rubén García Rodríguez**
Licensed under GPL-3.0
