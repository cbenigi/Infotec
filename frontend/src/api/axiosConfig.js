import axios from 'axios';

// Configurar axios para enviar cookies en todas las peticiones
axios.defaults.withCredentials = true;

// Configurar la URL base
const apiUrl = process.env.REACT_APP_API_URL || `http://${window.location.hostname}:5000`;
axios.defaults.baseURL = apiUrl;

export default axios;
