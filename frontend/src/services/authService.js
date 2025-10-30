/**
 * Servicio de Autenticación
 * Maneja todas las llamadas a la API de autenticación
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class AuthService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/api/auth`;
  }

  /**
   * Realiza login de usuario
   * @param {string} email 
   * @param {string} password 
   * @returns {Promise<Object>} Respuesta con token y datos de usuario
   */
  async login(email, password) {
    try {
      const response = await fetch(`${this.baseURL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error en el login');
      }

      // Almacenar token en localStorage
      if (data.access_token) {
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('user_data', JSON.stringify(data.user));
      }

      return data;
    } catch (error) {
      console.error('Error en login:', error);
      throw error;
    }
  }

  /**
   * Registra un nuevo usuario
   * @param {string} name 
   * @param {string} email 
   * @param {string} password 
   * @returns {Promise<Object>} Respuesta con token y datos de usuario
   */
  async register(name, email, password) {
    try {
      const response = await fetch(`${this.baseURL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error en el registro');
      }

      // Almacenar token en localStorage
      if (data.access_token) {
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('user_data', JSON.stringify(data.user));
      }

      return data;
    } catch (error) {
      console.error('Error en registro:', error);
      throw error;
    }
  }

  /**
   * Cierra sesión del usuario
   * @returns {Promise<void>}
   */
  async logout() {
    try {
      const token = this.getToken();
      
      if (token) {
        // Llamar al endpoint de logout del backend
        await fetch(`${this.baseURL}/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      console.error('Error en logout:', error);
    } finally {
      // Limpiar datos locales independientemente del resultado
      this.clearLocalStorage();
    }
  }

  /**
   * Verifica el token actual y obtiene datos del usuario
   * @returns {Promise<Object>} Datos del usuario actual
   */
  async verifyToken() {
    try {
      const token = this.getToken();
      
      if (!token) {
        throw new Error('No token found');
      }

      const response = await fetch(`${this.baseURL}/verify`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Token inválido');
      }

      const userData = await response.json();
      
      // Actualizar datos de usuario en localStorage
      localStorage.setItem('user_data', JSON.stringify(userData));
      
      return userData;
    } catch (error) {
      console.error('Error verificando token:', error);
      this.clearLocalStorage();
      throw error;
    }
  }

  /**
   * Obtiene el token almacenado
   * @returns {string|null} Token JWT o null si no existe
   */
  getToken() {
    return localStorage.getItem('auth_token');
  }

  /**
   * Obtiene los datos del usuario almacenados
   * @returns {Object|null} Datos del usuario o null si no existen
   */
  getUserData() {
    try {
      const userData = localStorage.getItem('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error parsing user data:', error);
      return null;
    }
  }

  /**
   * Verifica si el usuario está logueado
   * @returns {boolean} True si está logueado
   */
  isAuthenticated() {
    const token = this.getToken();
    const userData = this.getUserData();
    return !!(token && userData);
  }

  /**
   * Limpia el localStorage de datos de autenticación
   */
  clearLocalStorage() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  }

  /**
   * Obtiene headers de autorización para requests autenticados
   * @returns {Object} Headers con Authorization
   */
  getAuthHeaders() {
    const token = this.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
}

// Exportar instancia singleton
const authService = new AuthService();
export default authService;