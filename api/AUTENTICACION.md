# SISTEMA DE AUTENTICACIÓN - CLINIC CLOUD

## Descripción General

Sistema de autenticación modular y reutilizable implementado para ClinicCloud. Incluye registro, login, JWT tokens y gestión de sesiones.

## 🏗️ Arquitectura

### Estructura de Archivos
```
api/
├── app/
│   ├── models/
│   │   ├── user.py           # Modelos Pydantic para usuarios
│   │   └── auth.py           # Utilidades JWT, hashing, seguridad
│   ├── middleware/
│   │   └── auth.py           # Dependencias FastAPI para proteger endpoints
│   └── api/endpoints/auth/
│       └── login.py          # Endpoints de autenticación
├── main.py                   # Configuración de rutas
└── requirements.txt          # Dependencias actualizadas
```

### Base de Datos
```
database/
└── auth_schema.sql           # Schema completo con tablas, índices y triggers
```

## 🔐 Características de Seguridad

### Contraseñas
- **Hashing**: bcrypt con 12 rounds
- **Validación**: Mínimo 6 caracteres, debe contener letras y números
- **Nunca se almacenan en texto plano**

### Tokens JWT
- **Algoritmo**: HS256
- **Expiración**: 24 horas (configurable)
- **Payload mínimo**: Solo user_id y email
- **Secret**: Variable de entorno JWT_SECRET

### Sesiones
- **Tracking**: Cada login crea registro en BD
- **Metadatos**: IP, User-Agent, timestamps
- **Invalidación**: Logout marca sesión como inactiva
- **Limpieza**: Función para eliminar sesiones expiradas

### Auditoría
- **Login attempts**: Registro de todos los intentos (exitosos y fallidos)
- **Rate limiting**: Estructura preparada para implementar
- **Logs**: Emails enmascarados para privacidad

## 📡 API Endpoints

### Registro de Usuario
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "Juan Pérez",
  "email": "juan@ejemplo.com", 
  "password": "mipassword123"
}
```

**Respuesta exitosa (201):**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "uuid-123",
    "name": "Juan Pérez",
    "email": "juan@ejemplo.com",
    "avatar_url": null,
    "is_active": true,
    "email_verified": false,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
}
```

### Login de Usuario
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "juan@ejemplo.com",
  "password": "mipassword123"
}
```

**Respuesta:** Igual que registro

### Verificar Token
```http
GET /api/auth/verify
Authorization: Bearer eyJ...
```

**Respuesta (200):**
```json
{
  "id": "uuid-123",
  "name": "Juan Pérez", 
  "email": "juan@ejemplo.com",
  "avatar_url": null,
  "is_active": true,
  "email_verified": false,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### Logout
```http
POST /api/auth/logout
Authorization: Bearer eyJ...
```

**Respuesta (200):**
```json
{
  "message": "Sesión cerrada correctamente",
  "success": true
}
```

## 🛡️ Proteger Endpoints

### Autenticación Obligatoria
```python
from app.middleware.auth import get_current_user
from app.models.user import UserResponse

@router.get("/perfil")
async def obtener_perfil(
    current_user: UserResponse = Depends(get_current_user)
):
    """Solo usuarios autenticados pueden acceder"""
    return {"mensaje": f"Hola {current_user.name}"}
```

### Autenticación Opcional
```python
from app.middleware.auth import get_current_user_optional

@router.get("/contenido")
async def obtener_contenido(
    current_user: UserResponse = Depends(get_current_user_optional)
):
    """Funciona con y sin autenticación"""
    if current_user:
        return {"mensaje": f"Bienvenido {current_user.name}"}
    else:
        return {"mensaje": "Contenido público"}
```

### Verificación Estricta de Sesión
```python
from app.middleware.auth import get_current_user_with_session_check

@router.delete("/datos-sensibles")
async def eliminar_datos(
    current_user: UserResponse = Depends(get_current_user_with_session_check)
):
    """Verifica que la sesión siga activa en BD"""
    # Operación sensible
    pass
```

## 🔧 Configuración

### Variables de Entorno
```bash
# Requeridas
JWT_SECRET=tu-secreto-muy-seguro-cambiar-en-produccion
DATABASE_URL=postgresql://admin:admin123@db:5432/cliniccloud

# Opcionales (tienen valores por defecto)
JWT_EXPIRE_HOURS=24
BCRYPT_ROUNDS=12
```

### Inicializar Base de Datos
```bash
# 1. Ejecutar el schema de autenticación
psql -h localhost -U admin -d cliniccloud -f database/auth_schema.sql

# 2. Verificar que se crearon las tablas
psql -h localhost -U admin -d cliniccloud -c "\dt auth.*"
```

## 🚀 Integración con Frontend

### Login Modal (Ya implementado)
El frontend ya tiene `LoginModal.js` configurado. Solo cambiar los endpoints:

```javascript
// En LoginModal.js - handleSubmit function
const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
const response = await fetch(`http://localhost:8000${endpoint}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
});
```

### Almacenar Token
```javascript
// Guardar token tras login exitoso
const { access_token, user } = await response.json();
localStorage.setItem('access_token', access_token);
localStorage.setItem('user', JSON.stringify(user));
```

### Usar Token en Requests
```javascript
// Agregar a todas las requests autenticadas
const token = localStorage.getItem('access_token');
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

### Verificar Autenticación
```javascript
// Verificar si el usuario sigue logueado
async function checkAuth() {
  const token = localStorage.getItem('access_token');
  if (!token) return null;
  
  try {
    const response = await fetch('/api/auth/verify', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (response.ok) {
      return await response.json();
    } else {
      // Token inválido, limpiar storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      return null;
    }
  } catch (error) {
    return null;
  }
}
```

## 🔄 Mantenimiento

### Limpiar Sesiones Expiradas
```python
# Ejecutar periódicamente (ej: cron job)
from app.middleware.auth import cleanup_expired_sessions
from app.db.database import get_database_connection

async def limpiar_sesiones():
    conn = await get_database_connection()
    eliminadas = await cleanup_expired_sessions(conn)
    print(f"Sesiones eliminadas: {eliminadas}")
```

### Invalidar Todas las Sesiones de un Usuario
```python
from app.middleware.auth import invalidate_all_user_sessions

# Útil si una cuenta se compromete
async def logout_everywhere(user_id: str):
    conn = await get_database_connection()
    invalidadas = await invalidate_all_user_sessions(conn, user_id)
    print(f"Sesiones invalidadas: {invalidadas}")
```

## 🎯 Próximas Mejoras

### OAuth Social Login
- Google OAuth ya tiene estructura preparada
- Implementar en `OAuthLoginRequest` y `OAuthUserInfo`
- Agregar endpoints `/api/auth/oauth/google`

### Verificación de Email
- Campo `email_verified` ya existe
- Implementar envío de emails de confirmación
- Endpoint `/api/auth/verify-email/{token}`

### Reset de Contraseña
- Implementar tokens temporales
- Endpoint `/api/auth/forgot-password`
- Endpoint `/api/auth/reset-password`

### Rate Limiting
- Usar Redis para contadores
- Implementar en login y registro
- Protección contra ataques de fuerza bruta

## 🐛 Troubleshooting

### Error: "Table 'auth.users' doesn't exist"
```bash
# Ejecutar el schema de autenticación
psql -h localhost -U admin -d cliniccloud -f database/auth_schema.sql
```

### Error: "JWT_SECRET not found"
```bash
# Configurar variable de entorno
export JWT_SECRET="tu-secreto-muy-seguro"
```

### Error: "bcrypt not installed"
```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Login siempre falla
```python
# Verificar que el hash de contraseña sea correcto
from app.models.auth import hash_password, verify_password

password = "test123"
hashed = hash_password(password)
print(f"Hash: {hashed}")
print(f"Verificación: {verify_password(password, hashed)}")  # Debe ser True
```

## 📚 Recursos Adicionales

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc7519)
- [bcrypt Hashing](https://pypi.org/project/bcrypt/)
- [PostgreSQL UUID](https://www.postgresql.org/docs/current/datatype-uuid.html)

---

**Sistema implementado con comentarios en español para facilitar mantenimiento y reutilización en diferentes proyectos.**