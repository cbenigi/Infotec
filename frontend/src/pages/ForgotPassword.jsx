import React, { useState } from 'react';
import {
  TextField,
  Button,
  Typography,
  Box,
  Paper,
  InputAdornment,
  IconButton,
  Link,
  Alert
} from '@mui/material';
import axios from '../api/axiosConfig';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import EmailIcon from '@mui/icons-material/Email';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import BusinessIcon from '@mui/icons-material/Business';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';

const ForgotPassword = () => {
  const [form, setForm] = useState({ email: '', nit: '', new_password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleReset = async () => {
    setError('');
    setSuccess('');
    
    if (!form.email || !form.nit || !form.new_password) {
      setError('Por favor completa todos los campos.');
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post('/reset-password', form);
      setSuccess(res.data.message);
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      console.error('Error al restablecer contraseña:', err);
      setError(err.response?.data?.message || 'Error al procesar la solicitud. Verifica tus datos.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleReset();
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
          radial-gradient(circle at 82% 78%, rgba(0, 122, 204, 0.25), transparent 45%)`,
        backgroundSize: 'cover',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 3
      }}
    >
      <Paper elevation={6} sx={{ p: 5, maxWidth: 500, width: '100%', borderRadius: 3 }}>
        <Box sx={{ mb: 4 }}>
          <Button
            component={RouterLink}
            to="/login"
            startIcon={<ArrowBackIcon />}
            sx={{ mb: 2, textTransform: 'none' }}
          >
            Volver al Inicio
          </Button>
          <Typography component="h1" variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 1 }}>
            Recuperar Contraseña
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Ingresa tus datos para restablecer tu acceso.
          </Typography>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 3 }}>{success} Redirigiendo al login...</Alert>}

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
          label="NIT de la Empresa"
          value={form.nit}
          onChange={(e) => setForm({ ...form, nit: e.target.value })}
          onKeyPress={handleKeyPress}
          fullWidth
          margin="normal"
          variant="outlined"
          helperText="Identificación registrada de tu empresa vinculada"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <BusinessIcon color="primary" />
              </InputAdornment>
            ),
          }}
        />

        <TextField
          label="Nueva Contraseña"
          type={showPassword ? 'text' : 'password'}
          value={form.new_password}
          onChange={(e) => setForm({ ...form, new_password: e.target.value })}
          onKeyPress={handleKeyPress}
          fullWidth
          margin="normal"
          variant="outlined"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <VpnKeyIcon color="primary" />
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
          onClick={handleReset}
          fullWidth
          size="large"
          disabled={loading || !!success}
          sx={{
            mt: 4,
            mb: 2,
            py: 1.5,
            textTransform: 'none',
            fontSize: '1.1rem',
            fontWeight: 600,
            borderRadius: 2,
            boxShadow: 3
          }}
        >
          {loading ? 'Procesando...' : 'Cambiar Contraseña'}
        </Button>

        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            ¿Recordaste tu contraseña?{' '}
            <Link component={RouterLink} to="/login" variant="body1" sx={{ fontWeight: 600 }}>
              Inicia sesión
            </Link>
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default ForgotPassword;
