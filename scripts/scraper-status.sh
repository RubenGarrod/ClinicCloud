#!/bin/bash
# =============================================================================
# SCRAPER STATUS - Ver estado del scraper continuo
# =============================================================================
# Este script muestra el estado actual del scraper y estadísticas.
# =============================================================================

set -e

# Directorio del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "================================================================================"
echo "📊 ESTADO DEL SCRAPER CONTINUO - $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================================"

# Verificar que docker-compose existe
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose no está instalado"
    exit 1
fi

# Estado del contenedor
echo ""
echo "🐋 Estado del contenedor:"
echo "--------------------------------------------------------------------------------"
docker-compose ps scraper || echo "⚠️  Contenedor no encontrado"

# Verificar si está corriendo
if docker-compose ps scraper | grep -q "Up"; then
    echo ""
    echo "✅ Scraper en ejecución"

    # Mostrar recursos
    echo ""
    echo "💾 Recursos utilizados:"
    echo "--------------------------------------------------------------------------------"
    docker stats cliniccloud_scraper --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" || true

    # Últimas 20 líneas de logs
    echo ""
    echo "📝 Últimas líneas de logs:"
    echo "--------------------------------------------------------------------------------"
    docker-compose logs --tail=20 scraper

else
    echo ""
    echo "❌ Scraper detenido"
fi

# Estadísticas de la base de datos
echo ""
echo "📚 Estadísticas de documentos:"
echo "--------------------------------------------------------------------------------"
docker-compose exec -T db psql -U admin -d cliniccloud -c "
SELECT
    COUNT(*) as total_documentos,
    COUNT(CASE WHEN contenido_vectorizado IS NOT NULL THEN 1 END) as con_embeddings,
    COUNT(DISTINCT id_categoria) as categorias_unicas,
    MAX(fecha_creacion) as ultimo_documento
FROM documento;
" || echo "⚠️  No se pudo conectar a la base de datos"

echo ""
echo "🏷️  Documentos por categoría (top 10):"
echo "--------------------------------------------------------------------------------"
docker-compose exec -T db psql -U admin -d cliniccloud -c "
SELECT
    c.nombre as categoria,
    COUNT(d.id) as cantidad
FROM documento d
LEFT JOIN categoria c ON d.id_categoria = c.id
GROUP BY c.nombre
ORDER BY cantidad DESC
LIMIT 10;
" || echo "⚠️  No se pudo conectar a la base de datos"

echo ""
echo "================================================================================"
echo "💡 Comandos útiles:"
echo "   - Ver logs en vivo:  docker-compose logs -f scraper"
echo "   - Detener scraper:   docker-compose down scraper"
echo "   - Reiniciar scraper: ./scripts/scraper-start.sh"
echo "================================================================================"
