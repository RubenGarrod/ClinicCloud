# Database Migrations

**[🇬🇧 English](README_EN.md)** | **[🇪🇸 Español](README.md)**

---

This directory contains SQL migrations for ClinicCloud.

## Applying migrations

### Option 1: With Python (Recommended)

```bash
# Apply a specific migration
python apply_migration.py 001_user_preferences_and_history.sql

# Apply all migrations
python apply_migration.py
```

### Option 2: Manually with psql

```bash
# Connect to the database
psql postgresql://admin:admin123@localhost:5432/cliniccloud

# Execute the SQL file
\i 001_user_preferences_and_history.sql
```

### Option 3: With Docker

```bash
# If database is in Docker
docker exec -i cliniccloud-db psql -U admin -d cliniccloud < 001_user_preferences_and_history.sql
```

## Migration list

- **001_user_preferences_and_history.sql**:
  - Extends `auth.users` with preferences (avatar, language, institution, specialty)
  - Creates `search_history` table for search history
  - Creates `favorite_documents` table for favorite documents
  - Prepares tables for future RAG conversations
  - Creates `document_interactions` table for analytics

## Verify database status

```sql
-- View auth.users columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'auth' AND table_name = 'users';

-- View all created tables
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema IN ('auth', 'public')
ORDER BY table_schema, table_name;

-- Count registered searches
SELECT COUNT(*) FROM search_history;

-- Count favorites
SELECT COUNT(*) FROM favorite_documents;
```

## Rollback (if necessary)

If you need to revert a migration, you can execute:

```sql
-- Revert 001_user_preferences_and_history.sql
DROP TABLE IF EXISTS document_interactions CASCADE;
DROP TABLE IF EXISTS conversation_documents CASCADE;
DROP TABLE IF EXISTS conversation_messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS favorite_documents CASCADE;
DROP TABLE IF EXISTS search_history CASCADE;

ALTER TABLE auth.users
  DROP COLUMN IF EXISTS institution,
  DROP COLUMN IF EXISTS specialty,
  DROP COLUMN IF EXISTS avatar_icon,
  DROP COLUMN IF EXISTS avatar_color,
  DROP COLUMN IF EXISTS language,
  DROP COLUMN IF EXISTS last_login;
```

## Important notes

- **Backups**: Always make a backup before applying migrations in production
- **Order**: Migrations must be applied in numerical order
- **Idempotency**: Migrations use `IF NOT EXISTS` to be safe to re-run
- **Testing**: Test migrations in development before production
