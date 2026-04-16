import React, { useState, useEffect } from 'react';
import {
  TextField,
  Button,
  Typography,
  Box,
  Link,
  Paper,
  Grid,
  InputAdornment,
  IconButton,
  Avatar
} from '@mui/material';
import axios from '../api/axiosConfig';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import EmailIcon from '@mui/icons-material/Email';
import LockIcon from '@mui/icons-material/Lock';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Verificar si ya hay una sesión activa al cargar
  useEffect(() => {
    const verifySession = async () => {
      try {
        const isPWA = window.matchMedia('(display-mode: standalone)').matches;
        const res = await axios.get('check-session');
        
        // Solo auto-login si es PWA. En PC siempre pedir login.
        if (res.data.logged_in && isPWA) {
          localStorage.setItem('rol', res.data.rol);
          localStorage.setItem('userName', res.data.nombre);
          localStorage.setItem('userId', String(res.data.user_id));
          
          const targetRoute = res.data.rol === 'nomina' ? '/dashboard/nomina' : '/dashboard';
          navigate(targetRoute);
        }
      } catch (err) {
        console.error('Error al verificar sesión:', err);
      }
    };
    verifySession();
  }, [navigate]);

  const handleLogin = async () => {
    setLoading(true);
    try {
      // Detectar si es PWA (modo standalone)
      const isPWA = window.matchMedia('(display-mode: standalone)').matches;
      
      const res = await axios.post('login', { 
        email, 
        password,
        remember: isPWA // Activar sesión persistente solo en PWA
      });
      
      localStorage.setItem('token', 'basic'); 
      localStorage.setItem('rol', res.data.rol);
      localStorage.setItem('userName', res.data.nombre);
      localStorage.setItem('userId', String(res.data.user_id));
      
      console.log('Login exitoso:', res.data);
      
      const targetRoute = res.data.rol === 'nomina' ? '/dashboard/nomina' : '/dashboard';
      navigate(targetRoute);
    } catch (err) {
      console.error('Error al iniciar sesión:', err);
      
      if (err.response?.status === 401) {
        alert('Credenciales inválidas. Verifica tu email y contraseña.');
      } else if (err.response?.status === 500) {
        alert('Error interno del servidor. Por favor, intenta nuevamente.');
      } else {
        alert('Error de conexión. Verifica tu conexión a internet.');
      }
    } finally {
      setLoading(false);
    }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: '#f8fbff',
        backgroundImage: `
          radial-gradient(circle at 22% 18%, rgba(113, 135, 255, 0.4), transparent 38%),
          radial-gradient(circle at 78% 12%, rgba(173, 219, 255, 0.45), transparent 40%),
          radial-gradient(circle at 12% 85%, rgba(71, 163, 253, 0.35), transparent 45%),
          radial-gradient(circle at 82% 78%, rgba(0, 122, 204, 0.25), transparent 45%),
          linear-gradient(90deg, rgba(255, 255, 255, 0.65) 0%, rgba(255, 255, 255, 0) 18%),
          linear-gradient(90deg, rgba(39, 122, 255, 0.08) 0%, rgba(39, 122, 255, 0) 40%),
          linear-gradient(90deg, rgba(0, 173, 181, 0.08) 0%, rgba(0, 173, 181, 0) 28%)`,
        backgroundSize: 'cover, cover, cover, cover, 150px, 220px, 260px',
        backgroundRepeat: 'no-repeat'
      }}
    >
    <Grid container sx={{ minHeight: '100vh', backgroundColor: 'transparent' }}>
      {/* Columna Izquierda - Imagen/Branding */}
      <Grid
        size={{ xs: 12, md: 6 }}
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          color: '#0f1f47',
          padding: 4
        }}
      >
        <Avatar
          src="/ChatGPT_Image_14_nov_2025__15_45_43-removebg-preview.png"
          alt="Logo PROCLYM"
          sx={{ width: 240, height: 240, mb: 3, backgroundColor: 'transparent' }}
          variant="square"
        />
        <Typography variant="h6" sx={{ opacity: 0.85, textAlign: 'center', maxWidth: 420 }}>
          Plataforma integral para coordinar visitas técnicas, compras y documentación de servicios de mantenimiento.
        </Typography>
        <Box sx={{ mt: 4, opacity: 0.8 }}>
          <Typography variant="body2">✓ Genera PDFs profesionales</Typography>
          <Typography variant="body2">✓ Gestiona clientes fácilmente</Typography>
          <Typography variant="body2">✓ Registros con fotografías</Typography>
        </Box>
      </Grid>
      {/* Columna Derecha - Formulario */}
      <Grid size={{ xs: 12, md: 6 }} sx={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 4,
        backgroundColor: 'transparent'
      }}>
        <Paper elevation={6} sx={{ p: 5, maxWidth: 450, width: '100%', borderRadius: 3 }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography component="h1" variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 1 }}>
              Iniciar Sesión
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Ingresa tus credenciales para continuar
            </Typography>
          </Box>

          <TextField
            label="Correo Electrónico"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyPress={handleKeyPress}
            fullWidth
            margin="normal"
            variant="outlined"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <EmailIcon color="primary" />
                </InputAdornment>
              ),
            }}
          />

          <TextField
            label="Contraseña"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyPress={handleKeyPress}
            fullWidth
            margin="normal"
            variant="outlined"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <LockIcon color="primary" />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowPassword(!showPassword)}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <Button
            variant="contained"
            onClick={handleLogin}
            fullWidth
            size="large"
            sx={{
              mt: 3,
              mb: 2,
              py: 1.5,
              textTransform: 'none',
              fontSize: '1.1rem',
              fontWeight: 600,
              borderRadius: 2,
              boxShadow: 3
            }}
            disabled={loading}
          >
            {loading ? 'Iniciando...' : 'Iniciar Sesión'}
          </Button>

          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Link component={RouterLink} to="/forgot-password" variant="body2" sx={{ fontWeight: 600 }}>
              ¿Olvidaste tu contraseña?
            </Link>
          </Box>

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              ¿No tienes cuenta?
            </Typography>
            <Link component={RouterLink} to="/register" variant="body1" sx={{ fontWeight: 600 }}>
              Regístrate aquí
            </Link>
          </Box>
          </Paper>
      </Grid>
    </Grid>
    </Box>
  );
};

export default Login;