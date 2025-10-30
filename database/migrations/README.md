# Migraciones de Base de Datos

**[🇬🇧 English](README_EN.md)** | **🇪🇸 Español**

---

Este directorio contiene las migraciones SQL para ClinicCloud.

## Aplicar migraciones

### Opción 1: Con Python (Recomendado)

```bash
# Aplicar una migración específica
python apply_migration.py 001_user_preferences_and_history.sql

# Aplicar todas las migraciones
python apply_migration.py
```

### Opción 2: Manualmente con psql

```bash
# Conectar a la base de datos
psql postgresql://admin:admin123@localhost:5432/cliniccloud

# Ejecutar el archivo SQL
\i 001_user_preferences_and_history.sql
```

### Opción 3: Con Docker

```bash
# Si la base de datos está en Docker
docker exec -i cliniccloud-db psql -U admin -d cliniccloud < 001_user_preferences_and_history.sql
```

## Lista de migraciones

- **001_user_preferences_and_history.sql**:
  - Extiende `auth.users` con preferencias (avatar, idioma, institución, especialidad)
  - Crea tabla `search_history` para historial de búsquedas
  - Crea tabla `favorite_documents` para documentos favoritos
  - Prepara tablas para conversaciones RAG futuras
  - Crea tabla `document_interactions` para analytics

## Verificar estado de la base de datos

```sql
-- Ver columnas de auth.users
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'auth' AND table_name = 'users';

-- Ver todas las tablas creadas
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema IN ('auth', 'public')
ORDER BY table_schema, table_name;

-- Contar búsquedas registradas
SELECT COUNT(*) FROM search_history;

-- Contar favoritos
SELECT COUNT(*) FROM favorite_documents;
```

## Rollback (en caso necesario)

Si necesitas revertir una migración, puedes ejecutar:

```sql
-- Revertir 001_user_preferences_and_history.sql
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

## Notas importantes

- **Backups**: Siempre haz un backup antes de aplicar migraciones en producción
- **Orden**: Las migraciones deben aplicarse en orden numérico
- **Idempotencia**: Las migraciones usan `IF NOT EXISTS` para ser seguras de re-ejecutar
- **Testing**: Prueba las migraciones en desarrollo antes de producción
