# Clinic Cloud

![Clinic Cloud Logo](frontend/src/assets/clinic-cloud-logo.png)

Clinic Cloud es un sistema de búsqueda de información médica basado en procesamiento de lenguaje natural, diseñado para facilitar el acceso a documentos médicos y científicos. El proyecto está construido con una arquitectura de microservicios, utilizando tecnologías modernas como Python, FastAPI, React, PostgreSQL y Docker.

## Características principales

- Recopilación automática de estudios médicos desde fuentes públicas como PubMed
- Motor de búsqueda basado en procesamiento de lenguaje natural
- Generación automática de resúmenes de artículos científicos
- Clasificación automática de documentos por categorías médicas
- Interfaz web intuitiva y accesible
- Arquitectura de microservicios desplegada en contenedores Docker

## Requisitos previos

Para ejecutar Clinic Cloud localmente, necesitarás:

- [Docker](https://www.docker.com/products/docker-desktop/) y Docker Compose
- [Git](https://git-scm.com/downloads)
- Al menos 4GB de RAM disponible para los contenedores
- Aproximadamente 2GB de espacio en disco

## Instalación

Sigue estos pasos para configurar y ejecutar Clinic Cloud en tu máquina local:

### 1. Clonar el repositorio

```bash
git clone https://github.com/RubenGarrod/cliniccloud.git
cd cliniccloud
```

### 2. Configurar variables de entorno (opcional)

El proyecto viene configurado con valores predeterminados, pero puedes personalizar la configuración creando un archivo `.env` en el directorio raíz:

```bash
# Configuración de la base de datos
PG_HOST=db
PG_PORT=5432
PG_DATABASE=cliniccloud
PG_USER=admin
PG_PASSWORD=admin123

# Configuración del motor de búsqueda
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIMENSION=768
SIMILARITY_THRESHOLD=0.5
MAX_SEARCH_RESULTS=20
```

### 3. Iniciar los servicios con Docker Compose

```bash
docker-compose up -d
```

Este comando construirá e iniciará todos los microservicios:
- **db**: Base de datos PostgreSQL con la extensión pgvector
- **adminer**: Interfaz web para gestionar la base de datos
- **scraper**: Microservicio para la extracción de documentos médicos
- **api**: API REST para la comunicación con la interfaz web
- **motor_busqueda**: Motor de búsqueda vectorial
- **frontend**: Interfaz web de la aplicación

> **Nota**: La primera vez que ejecutes este comando, Docker descargará las imágenes necesarias y construirá los contenedores, lo que puede tardar varios minutos dependiendo de tu conexión a Internet.

### 4. Verificar que todos los servicios están funcionando

```bash
docker-compose ps
```

Todos los servicios deberían mostrarse como "running".

### 5. Acceso a la aplicación

Una vez que todos los servicios estén en funcionamiento, puedes acceder a:

- **Interfaz web**: http://localhost:80
- **Adminer** (gestión de la base de datos): http://localhost:8080
  - Sistema: PostgreSQL
  - Servidor: db
  - Usuario: admin
  - Contraseña: admin123
  - Base de datos: cliniccloud
- **API REST**: http://localhost:8000
- **Motor de búsqueda**: http://localhost:8001

## Uso básico

### Realizar una búsqueda

1. Abre la interfaz web en http://localhost:80
2. Introduce términos médicos en el campo de búsqueda (por ejemplo, "diabetes treatment")
3. Haz clic en el botón de búsqueda
4. Explora los resultados y accede a las fuentes originales mediante los enlaces

### Carga inicial de datos

Los datos se cargan automáticamente a través del servicio de scraper. Puedes comprobar el estado de la recopilación de datos accediendo a los logs del contenedor:

```bash
docker-compose logs -f scraper
```

## Estructura del proyecto

El proyecto está organizado en varios microservicios:

- **scraper**: Extrae datos de fuentes médicas como PubMed
- **db**: Almacena los documentos y sus embeddings vectoriales
- **api**: Proporciona endpoints para la comunicación con el frontend
- **motor_busqueda**: Implementa la búsqueda vectorial
- **frontend**: Interfaz de usuario en React

Cada microservicio tiene su propio directorio con código y configuraciones específicas.

## Troubleshooting

### Posibles problemas y soluciones

#### El servicio de base de datos no se inicia
```bash
docker-compose down
docker volume rm clinic-cloud_pgdata
docker-compose up -d
```

#### El scraper no extrae datos
```bash
docker-compose restart scraper
docker-compose logs -f scraper
```

#### La búsqueda no devuelve resultados
```bash
# Comprueba que hay documentos en la base de datos
docker-compose exec db psql -U admin -d cliniccloud -c "SELECT COUNT(*) FROM documento;"
```

#### Reinicar todos los servicios
```bash
docker-compose down
docker-compose up -d
```

## Desarrollo

### Estructura de archivos principal

```
clinic-cloud/
├── api/                 # API REST
├── database/            # Scripts de inicialización de la DB
├── frontend/            # Interfaz web en React
├── motor_busqueda/      # Motor de búsqueda vectorial
├── scraper/             # Sistema de extracción de datos
│   ├── clinic_scraper/
│   │   ├── spiders/
│   │   │   └── pubmed_spider.py
│   │   ├── pipelines.py
│   │   └── settings.py
│   ├── inferencia/
│   │   ├── categorizador.py
│   │   └── motor_inferencia.py
│   └── main.py
├── docker-compose.yml   # Configuración de Docker Compose
└── README.md            # Este archivo
```

### Ejecución de un microservicio específico

```bash
# Por ejemplo, para reiniciar solo el servicio de API
docker-compose restart api
```

## Contribuir

Si deseas contribuir al proyecto, por favor:

1. Haz un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la GNU General Public License v3.0 (GPL-3.0) - consulta el archivo LICENSE para más detalles.

## Contacto

Rubén García Rodríguez - ruben.garrod@educa.jcyl.es

Enlace del proyecto: [https://github.com/RubenGarrod/cliniccloud](https://github.com/RubenGarrod/cliniccloud)