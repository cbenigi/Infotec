import React, { useState } from 'react';
import { TextField, Button, Typography, Box, Paper, Grid, InputAdornment, IconButton, Link } from '@mui/material';
import axios from '../api/axiosConfig';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import LockIcon from '@mui/icons-material/Lock';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import BusinessIcon from '@mui/icons-material/Business';

const Register = () => {
  const [form, setForm] = useState({ nombre: '', email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async () => {
    try {
      await axios.post('/usuarios', { ...form, rol: 'user' });
      
      // Guardar nombre del usuario
      localStorage.setItem('userName', form.nombre);
      
      // Verificar si el usuario tiene empresa registrada
      const empresaRes = await axios.get('/empresa');
      
      if (empresaRes.data.exists) {
        // Ya tiene empresa, ir al dashboard
        alert('Registro exitoso. Bienvenido de nuevo!');
        navigate('/dashboard');
      } else {
        // No tiene empresa, debe registrarla primero
        alert('Registro exitoso! Ahora registra tu empresa para empezar a crear informes.');
        navigate('/empresa');
      }
    } catch (err) {
      console.error('Error al registrar usuario:', err);
      
      // Manejar diferentes tipos de errores
      if (err.response?.status === 400) {
        const errorMessage = err.response?.data?.message || 'Error en los datos enviados';
        if (errorMessage.includes('email ya está registrado')) {
          alert('Este correo electrónico ya está siendo usado. Por favor, usa otro correo.');
        } else {
          alert(`Error: ${errorMessage}`);
        }
      } else if (err.response?.status === 500) {
        alert('Error interno del servidor. Por favor, intenta nuevamente.');
      } else {
        alert('Error de conexión. Verifica tu conexión a internet.');
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleRegister();
    }
  };

  return (
    <Grid container sx={{ minHeight: '100vh' }}>
      {/* Columna Izquierda - Imagen/Branding */}
      <Grid size={{ xs: 12, md: 6 }} sx={{
        background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        color: 'white',
        padding: 4
      }}>
        <BusinessIcon sx={{ fontSize: 120, mb: 3, opacity: 0.9 }} />
        <Typography variant="h3" sx={{ fontWeight: 700, mb: 2, textAlign: 'center' }}>
          Informetec
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, textAlign: 'center', maxWidth: 400 }}>
          Únete y comienza a profesionalizar tus informes de visitas técnicas
        </Typography>
        <Box sx={{ mt: 4, opacity: 0.8 }}>
          <Typography variant="body2">✓ Configuración rápida</Typography>
          <Typography variant="body2">✓ Interfaz intuitiva</Typography>
          <Typography variant="body2">✓ Sin costos ocultos</Typography>
        </Box>
      </Grid>

      {/* Columna Derecha - Formulario */}
      <Grid size={{ xs: 12, md: 6 }} sx={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 4,
        backgroundColor: '#f5f5f5'
      }}>
        <Paper elevation={6} sx={{ p: 5, maxWidth: 450, width: '100%', borderRadius: 3 }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography component="h1" variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 1 }}>
              Crear Cuenta
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Completa los datos para registrarte
            </Typography>
          </Box>

          <TextField
            label="Nombre Completo"
            value={form.nombre}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })}
            onKeyPress={handleKeyPress}
            fullWidth
            margin="normal"
            variant="outlined"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <PersonIcon color="primary" />
                </InputAdornment>
              ),
            }}
          />

          <TextField
            label="Correo Electrónico"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
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
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
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
            onClick={handleRegister}
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
          >
            Registrarse
          </Button>

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              ¿Ya tienes cuenta?
            </Typography>
            <Link component={RouterLink} to="/login" variant="body1" sx={{ fontWeight: 600 }}>
              Inicia sesión aquí
            </Link>
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default Register;