# Base de Datos - ClinicCloud

**[🇬🇧 English](README_EN.md)** | **🇪🇸 Español**

---

## Descripción

Este directorio contiene todos los schemas y configuraciones de base de datos para ClinicCloud.

## Estructura de Archivos

### Archivos Principales

- **`consolidated_schema.sql`** - **USAR ESTE PARA NUEVAS INSTALACIONES**
  - Schema completo consolidado
  - Incluye todas las tablas, índices y funciones
  - Recomendado para nuevos despliegues

- **`init.sql`** - Schema inicial de documentos médicos
  - Tabla `documento` y `categoria`
  - Extensión vector para búsqueda semántica

- **`auth_schema.sql`** - Schema de autenticación (obsoleto, ver consolidated_schema.sql)
  - Tabla `auth.users`
  - Sistema de autenticación básico

### Directorio de Migraciones

`migrations/` - Historial de cambios incrementales del schema

- `001_user_preferences_and_history.sql` - Preferencias e historial
- `002_add_location_fields.sql` - Campos de localización
- `003_add_user_preferences.sql` - Tabla de preferencias
- `004_add_password_reset_tokens.sql` - Tokens de recuperación
- `005_add_search_history_and_favorites.sql` - Historial y favoritos
- `apply_migration.py` - Script para aplicar migraciones

## Uso

### Para Nueva Instalación

Si estás configurando ClinicCloud desde cero:

```bash
# 1. Crear la base de datos
createdb cliniccloud

# 2. Aplicar el schema consolidado
psql -U postgres -d cliniccloud -f database/consolidated_schema.sql
```

### Para Base de Datos Existente

Si ya tienes una instalación y necesitas actualizarla:

```bash
# Aplicar migraciones pendientes
cd database/migrations
python apply_migration.py
```

### Con Docker

El schema se aplica automáticamente al iniciar los contenedores:

```bash
docker-compose up -d
```

## Schema de Base de Datos

### Schemas PostgreSQL

1. **`public`** - Documentos médicos y datos generales
   - `categoria` - Especialidades médicas
   - `documento` - Artículos científicos indexados
   - `search_history` - Historial de búsquedas
   - `favorites` - Documentos guardados por usuarios

2. **`auth`** - Sistema de autenticación
   - `users` - Usuarios registrados
   - `user_preferences` - Preferencias personalizadas
   - `password_reset_tokens` - Tokens de recuperación

### Extensiones Requeridas

- **pgvector** - Búsqueda vectorial semántica
  ```sql
  CREATE EXTENSION vector;
  ```

## Mantenimiento

### Limpiar Tokens Expirados

```sql
SELECT auth.cleanup_expired_tokens();
```

### Verificar Integridad

```sql
-- Verificar tablas creadas
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema IN ('public', 'auth')
ORDER BY table_schema, table_name;

-- Verificar índices
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname IN ('public', 'auth')
ORDER BY tablename;
```

### Backup

```bash
# Backup completo
pg_dump -U postgres cliniccloud > backup_$(date +%Y%m%d).sql

# Backup solo del schema
pg_dump -U postgres --schema-only cliniccloud > schema_backup.sql

# Backup solo de datos
pg_dump -U postgres --data-only cliniccloud > data_backup.sql
```

## Historial de Cambios

| Versión | Fecha | Descripción |
|---------|-------|-------------|
| 5.0 | 2025-10-16 | Schema consolidado creado |
| 4.0 | 2025-10-10 | Añadido historial y favoritos |
| 3.0 | 2025-10-09 | Añadidos tokens de reset |
| 2.0 | 2025-10-08 | Añadidas preferencias de usuario |
| 1.0 | 2025-08-02 | Schema inicial de autenticación |
| 0.1 | 2025-05-13 | Schema de documentos médicos |

## Seguridad

- Las contraseñas se almacenan con hash bcrypt
- Los tokens de reset expiran en 1 hora
- Constraint de email único
- Cascade deletes configurados apropiadamente
- Índices en campos sensibles para prevenir timing attacks

## Documentación Adicional

- [Migraciones](migrations/README.md) - Guía detallada de migraciones
- [Modelo de Datos](../docs/database-model.md) - Diagrama ER (si existe)

## Notas Importantes

1. **No editar** `consolidated_schema.sql` directamente
2. **Crear nuevas migraciones** para cambios incrementales
3. **Probar migraciones** en desarrollo antes de producción
4. **Hacer backup** antes de aplicar migraciones en producción
5. Las **migraciones históricas** se mantienen para referencia

---

**Copyright (C) 2025 Rubén García Rodríguez**
Licensed under GPL-3.0
