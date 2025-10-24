import axios from 'axios';

// Configurar axios para enviar cookies en todas las peticiones
axios.defaults.withCredentials = true;

// Configurar la URL base
axios.defaults.baseURL = 'http://localhost:5000';

export default axios;
