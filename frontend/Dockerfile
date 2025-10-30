FROM node:19-alpine as build

WORKDIR /app

# Copiar archivos de dependencias primero
COPY package.json package-lock.json ./

# Usar --legacy-peer-deps para ignorar los conflictos de dependencias
RUN npm install --legacy-peer-deps

# ARG para URL de API (por defecto localhost para desarrollo)
# Estos deben estar ANTES del COPY para tener prioridad
ARG REACT_APP_API_URL=http://localhost:8000
ARG REACT_APP_SEARCH_ENGINE_URL=http://localhost:8001

# Exportar ARGs como variables de entorno ANTES de copiar archivos
# Esto asegura que tengan prioridad sobre cualquier .env.*
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_SEARCH_ENGINE_URL=$REACT_APP_SEARCH_ENGINE_URL

# Copiar el resto de los archivos
COPY . .

# Eliminar .env.production para que no interfiera
# ENV ya está configurado, así que React lo usará
RUN rm -f .env.production .env.local && \
    echo "REACT_APP_API_URL=$REACT_APP_API_URL" && \
    echo "REACT_APP_SEARCH_ENGINE_URL=$REACT_APP_SEARCH_ENGINE_URL"

# Construir la aplicación (también con --legacy-peer-deps)
# React usará las ENV que definimos arriba
RUN npm run build --legacy-peer-deps

# Configuración de producción con Nginx
FROM nginx:alpine

# Copiar archivos de build
COPY --from=build /app/build /usr/share/nginx/html

# Configuración de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]