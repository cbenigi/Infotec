import React, { useState } from 'react';
import { 
  TextField, 
  Button, 
  Container, 
  Typography, 
  Box, 
  Paper,
  Grid,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton
} from '@mui/material';
import axios from '../api/axiosConfig';
import { useNavigate } from 'react-router-dom';
import SupervisorAccountIcon from '@mui/icons-material/SupervisorAccount';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import LockIcon from '@mui/icons-material/Lock';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import Navbar from '../components/Navbar';

const SupervisorForm = () => {
  const [form, setForm] = useState({
    nombre: '',
    email: '',
    password: '',
    rol: 'supervisor'
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async () => {
    // Validar campos requeridos
    if (!form.nombre || !form.email || !form.password) {
      alert('Por favor completa todos los campos');
      return;
    }

    // Validar email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(form.email)) {
      alert('Por favor ingresa un email válido');
      return;
    }

    // Validar contraseña
    if (form.password.length < 6) {
      alert('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    setLoading(true);
    try {
      await axios.post('/usuarios', form);
      alert('Supervisor registrado exitosamente');
      navigate('/dashboard');
    } catch (err) {
      console.error('Error al registrar supervisor:', err);
      
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
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
    <Navbar />
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <SupervisorAccountIcon sx={{ fontSize: 60, color: '#1976d2', mb: 2 }} />
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600, color: '#1976d2', mb: 1 }}>
            Registrar Supervisor
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Crea una cuenta para un nuevo supervisor del sistema
          </Typography>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              label="Nombre Completo"
              value={form.nombre}
              onChange={(e) => setForm({ ...form, nombre: e.target.value })}
              fullWidth
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <PersonIcon color="primary" />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              label="Correo Electrónico"
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              fullWidth
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <EmailIcon color="primary" />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              label="Contraseña"
              type={showPassword ? 'text' : 'password'}
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              fullWidth
              required
              helperText="Mínimo 6 caracteres"
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
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Rol</InputLabel>
              <Select
                value={form.rol}
                label="Rol"
                onChange={(e) => setForm({ ...form, rol: e.target.value })}
              >
                <MenuItem value="supervisor">Supervisor</MenuItem>
                <MenuItem value="tecnico">Técnico</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="outlined"
            onClick={() => navigate('/dashboard')}
            size="large"
            sx={{ px: 4 }}
          >
            Cancelar
          </Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={loading}
            size="large"
            sx={{ px: 4 }}
          >
            {loading ? 'Registrando...' : 'Registrar Supervisor'}
          </Button>
        </Box>
      </Paper>
    </Container>
    </>
  );
};

export default SupervisorForm;
