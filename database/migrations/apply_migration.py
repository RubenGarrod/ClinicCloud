#!/usr/bin/env python3
"""
Script para aplicar migraciones SQL a la base de datos PostgreSQL
"""
import psycopg2
import sys
import os
from pathlib import Path

# Obtener la URL de la base de datos desde variables de entorno o usar la por defecto
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cliniccloud:changeme@localhost:5432/cliniccloud")

def apply_migration(migration_file):
    """Aplica un archivo SQL de migración a la base de datos"""
    print(f"\n{'='*60}")
    print(f"Aplicando migración: {migration_file.name}")
    print(f"{'='*60}\n")

    try:
        # Conectar a la base de datos
        print(f"Conectando a: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'base de datos'}")
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        cursor = conn.cursor()

        # Leer el archivo SQL
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print("Ejecutando SQL...")

        # Ejecutar el SQL
        cursor.execute(sql_content)

        # Commit
        conn.commit()

        print("\n✓ Migración aplicada exitosamente")

        # Cerrar conexión
        cursor.close()
        conn.close()

        return True

    except psycopg2.Error as e:
        print(f"\n✗ Error de PostgreSQL:")
        print(f"  Código: {e.pgcode}")
        print(f"  Mensaje: {e.pgerror}")
        if conn:
            conn.rollback()
            conn.close()
        return False

    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def main():
    """Función principal"""
    # Obtener el directorio de migraciones
    migrations_dir = Path(__file__).parent

    # Si se especifica un archivo, usar ese
    if len(sys.argv) > 1:
        migration_file = migrations_dir / sys.argv[1]
        if not migration_file.exists():
            print(f"✗ Error: No se encontró el archivo {migration_file}")
            sys.exit(1)

        success = apply_migration(migration_file)
        sys.exit(0 if success else 1)

    # Si no, aplicar todas las migraciones en orden
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("No se encontraron archivos de migración (.sql)")
        sys.exit(1)

    print(f"Encontradas {len(migration_files)} migraciones:")
    for mf in migration_files:
        print(f"  - {mf.name}")

    print("\n¿Deseas aplicar todas las migraciones? (s/n): ", end='')
    response = input().lower()

    if response != 's':
        print("Operación cancelada")
        sys.exit(0)

    # Aplicar cada migración
    failed = []
    for migration_file in migration_files:
        success = apply_migration(migration_file)
        if not success:
            failed.append(migration_file.name)

    # Resumen
    print(f"\n{'='*60}")
    print("RESUMEN")
    print(f"{'='*60}")
    print(f"Total: {len(migration_files)} migraciones")
    print(f"Exitosas: {len(migration_files) - len(failed)}")
    print(f"Fallidas: {len(failed)}")

    if failed:
        print("\nMigraciones fallidas:")
        for name in failed:
            print(f"  ✗ {name}")
        sys.exit(1)
    else:
        print("\n✓ Todas las migraciones se aplicaron exitosamente")
        sys.exit(0)

if __name__ == "__main__":
    main()
