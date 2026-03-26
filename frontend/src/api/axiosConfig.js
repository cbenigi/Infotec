import axios from 'axios';

// Configurar axios para enviar cookies en todas las peticiones
axios.defaults.withCredentials = true;

// Configurar la URL base
// Configurar la URL base. En producción usar el proxy de Vercel (/api)
const apiUrl = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : (process.env.REACT_APP_API_URL || `http://${window.location.hostname}:5000`);

axios.defaults.baseURL = apiUrl;

// Interceptor para asegurar que las rutas sean relativas al baseURL
axios.interceptors.request.use((config) => {
  if (config.url && config.url.startsWith('/')) {
    config.url = config.url.substring(1);
  }
  return config;
});

export default axios;
