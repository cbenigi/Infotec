import React, { useState } from 'react';
import { TextField, Button, Typography, Box, Link, Paper, Grid, InputAdornment, IconButton } from '@mui/material';
import axios from 'axios';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import EmailIcon from '@mui/icons-material/Email';
import LockIcon from '@mui/icons-material/Lock';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import BusinessIcon from '@mui/icons-material/Business';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const res = await axios.post('http://localhost:5000/login', { email, password });
      localStorage.setItem('token', 'basic'); // Simular token
      localStorage.setItem('rol', res.data.rol);
      
      // Obtener información del usuario
      const usersRes = await axios.get('http://localhost:5000/usuarios');
      const currentUser = usersRes.data.find(u => u.email === email);
      if (currentUser) {
        localStorage.setItem('userName', currentUser.nombre);
      }
      
      // Verificar si el usuario tiene empresa registrada
      const empresaRes = await axios.get('http://localhost:5000/empresa');
      
      if (empresaRes.data.exists) {
        navigate('/dashboard');
      } else {
        alert('Por favor registra tu empresa para continuar');
        navigate('/empresa');
      }
    } catch (err) {
      alert('Credenciales inválidas');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  return (
    <Grid container sx={{ minHeight: '100vh' }}>
      {/* Columna Izquierda - Imagen/Branding */}
      <Grid item xs={12} md={6} sx={{
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
          Sistema profesional de informes de visitas técnicas para empresas de aseo y mantenimiento
        </Typography>
        <Box sx={{ mt: 4, opacity: 0.8 }}>
          <Typography variant="body2">✓ Genera PDFs profesionales</Typography>
          <Typography variant="body2">✓ Gestiona clientes fácilmente</Typography>
          <Typography variant="body2">✓ Registros con fotografías</Typography>
        </Box>
      </Grid>

      {/* Columna Derecha - Formulario */}
      <Grid item xs={12} md={6} sx={{
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
          >
            Iniciar Sesión
          </Button>

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
  );
};

export default Login;