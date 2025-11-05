# 🎯 Mejoras al Sistema de Scraping - Tracking de PMIDs

## 📋 Problema Detectado

El scraper estaba procesando correctamente los documentos pero **NO insertaba ninguno** porque:

1. ❌ Las búsquedas eran siempre las mismas ("oncology", "cardiology", etc.)
2. ❌ PubMed devolvía los mismos artículos ordenados por relevancia
3. ❌ Todos los artículos ya estaban en la base de datos (duplicados)
4. ❌ Resultado: **"Insertados: 0, Saltados: 23"** en cada ejecución

### Log del Problema
```
📝 Documentos procesados: 948
✅ Batch completado - Insertados: 0, Saltados: 23
```

---

## ✅ Solución Implementada

### 1. **Filtro de Fechas Recientes**
- ✅ Busca solo artículos de los **últimos 30 días** (configurable)
- ✅ Usa el filtro `[dp]` (date of publication) de PubMed
- ✅ Ordena por fecha de publicación (más recientes primero)

```python
# Antes
pmids = fetcher.search_ids("cardiology", max_results=500)

# Ahora
pmids = fetcher.search_ids("cardiology", max_results=500, days_back=30)
```

### 2. **Sistema de Tracking de PMIDs**
- ✅ Nueva tabla `pmid_procesado` para registrar PMIDs ya procesados
- ✅ Evita reprocesar artículos ya obtenidos de PubMed
- ✅ Registra qué query originó cada PMID y si fue insertado

**Estructura de la tabla:**
```sql
CREATE TABLE pmid_procesado (
    id SERIAL PRIMARY KEY,
    pmid VARCHAR(20) NOT NULL UNIQUE,
    fecha_procesado TIMESTAMP NOT NULL DEFAULT NOW(),
    query_origen VARCHAR(500),
    insertado BOOLEAN DEFAULT FALSE
);
```

### 3. **Paginación con Offsets**
- ✅ Soporte para `retstart` (offset) en búsquedas
- ✅ Permite obtener resultados más allá de los primeros 500
- ✅ Preparado para paginación futura

### 4. **Limpieza Automática**
- ✅ Elimina registros de tracking antiguos (>90 días)
- ✅ Se ejecuta automáticamente en cada ejecución
- ✅ Evita crecimiento infinito de la tabla de tracking

---

## 🔧 Configuración

### Variables de Entorno (Opcional)

```bash
# Días hacia atrás para buscar artículos (default: 30)
SCRAPER_DAYS_BACK=30

# Otras configuraciones existentes
SCRAPER_MAX_DOCS=1000
SCRAPER_BATCH_SIZE=25
SCRAPER_LOOP_DELAY=1800
```

---

## 🚀 Cómo Usar

### 1. Aplicar la migración de BD (primera vez)

```bash
# Conectarse al contenedor de base de datos
docker exec -it cliniccloud-db-1 psql -U cliniccloud -d cliniccloud

# Ejecutar la migración
\i /app/scraper/migrations/add_pmid_tracking.sql
```

**Nota:** Si la tabla ya existe, no es necesario (se crea automáticamente).

### 2. Probar el sistema de tracking

```bash
# Entrar al contenedor del scraper
docker exec -it cliniccloud-scraper-1 bash

# Ejecutar test
cd /app
python test_tracking.py
```

### 3. Ejecutar el scraper normalmente

```bash
# El scraper continuo ya está ejecutándose
docker-compose logs -f scraper

# O ejecutar manualmente
docker exec -it cliniccloud-scraper-1 python scraper_masivo.py --max-docs 100
```

---

## 📊 Flujo Mejorado

### Antes (Problema)
```
1. Buscar "cardiology" → PubMed devuelve PMIDs [1,2,3,4,5]
2. Procesar artículos → Todos duplicados
3. Insertar: 0, Saltados: 5
4. ⏰ Esperar 30 minutos
5. Buscar "cardiology" → PubMed devuelve PMIDs [1,2,3,4,5]  ❌ MISMOS
6. Procesar artículos → Todos duplicados
7. Insertar: 0, Saltados: 5  ❌ REPETIDO
```

### Ahora (Solucionado)
```
1. Buscar "cardiology últimos 30 días" → PubMed devuelve PMIDs [1,2,3,4,5]
2. Filtrar PMIDs ya procesados → [1,2,3,4,5] son nuevos
3. Procesar artículos → 5 insertados
4. Marcar PMIDs [1,2,3,4,5] como procesados ✅
5. ⏰ Esperar 30 minutos
6. Buscar "cardiology últimos 30 días" → PubMed devuelve PMIDs [1,2,3,4,5,6]
7. Filtrar PMIDs ya procesados → Solo [6] es nuevo ✅
8. Procesar artículos → 1 insertado ✅
```

---

## 🎯 Ventajas

1. **✅ Evita reprocesar artículos**: No gasta recursos en documentos ya procesados
2. **✅ Busca contenido fresco**: Filtra por fecha (últimos 30 días)
3. **✅ Escalable**: Sistema de tracking con índices optimizados
4. **✅ Configurable**: Días hacia atrás ajustables vía variable de entorno
5. **✅ Auto-limpieza**: No requiere mantenimiento manual
6. **✅ Preparado para paginación**: Soporte de offsets para búsquedas grandes

---

## 📈 Métricas Esperadas

### Logs Mejorados
```
📊 PMIDs únicos obtenidos: 487
🔍 PMIDs: 487 total, 452 ya procesados, 35 nuevos
📊 PMIDs a procesar: 35
✅ Batch completado - Insertados: 28, Saltados: 7
```

### Antes vs Ahora
| Métrica | Antes | Ahora |
|---------|-------|-------|
| Duplicados procesados | 100% | ~5-10% |
| Documentos nuevos insertados | 0 | 20-50 por ejecución* |
| Uso de recursos | Desperdiciado | Optimizado |
| Tiempo de procesamiento | Igual | Reducido (menos docs) |

*Depende de la actividad de PubMed en las últimas 24-48 horas

---

## 🔍 Monitoreo

### Consultas Útiles

```sql
-- Ver total de PMIDs procesados
SELECT COUNT(*) FROM pmid_procesado;

-- Ver PMIDs insertados vs saltados
SELECT
    insertado,
    COUNT(*) as total
FROM pmid_procesado
GROUP BY insertado;

-- Ver PMIDs procesados recientemente
SELECT * FROM pmid_procesado
ORDER BY fecha_procesado DESC
LIMIT 10;

-- Ver distribución por query
SELECT
    query_origen,
    COUNT(*) as total,
    SUM(CASE WHEN insertado THEN 1 ELSE 0 END) as insertados
FROM pmid_procesado
GROUP BY query_origen
ORDER BY total DESC;
```

---

## 🐛 Troubleshooting

### Problema: "No hay PMIDs nuevos para procesar"
**Solución**: Aumentar `SCRAPER_DAYS_BACK` a 60 o 90 días.

```bash
# En docker-compose.yml o .env
SCRAPER_DAYS_BACK=60
```

### Problema: Tabla pmid_procesado creciendo mucho
**Solución**: Ajustar días de limpieza automática.

```python
# En scraper_masivo.py, línea ~711
self.db.cleanup_old_tracking(days=30)  # Cambiar de 90 a 30
```

### Problema: Aún se procesan duplicados
**Verificar**:
1. ¿La tabla `pmid_procesado` existe?
2. ¿Hay registros en la tabla?
3. ¿Los logs muestran el filtrado?

```bash
# Verificar en BD
docker exec -it cliniccloud-db-1 psql -U cliniccloud -d cliniccloud -c "SELECT COUNT(*) FROM pmid_procesado;"
```

---

## 📝 Archivos Modificados

1. ✅ `scraper_masivo.py` - Lógica principal mejorada
2. ✅ `migrations/add_pmid_tracking.sql` - Migración de BD
3. ✅ `test_tracking.py` - Script de pruebas
4. ✅ `MEJORAS_TRACKING.md` - Esta documentación

---

## 🎉 Conclusión

El scraper ahora es **inteligente** y no reprocesa documentos ya vistos. Esto mejora:
- ⚡ **Performance**: Solo procesa lo nuevo
- 💰 **Costos**: Menos llamadas a APIs de ML
- 📊 **Eficiencia**: Mejor uso de recursos del servidor
- 🎯 **Resultados**: Inserta documentos realmente nuevos

---

**Implementado**: 2025-11-05
**Autor**: Claude (Anthropic)
**Proyecto**: ClinicCloud
