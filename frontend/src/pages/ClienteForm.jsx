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
  Avatar
} from '@mui/material';
import axios from '../api/axiosConfig';
import { useNavigate } from 'react-router-dom';
import BusinessIcon from '@mui/icons-material/Business';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import BadgeIcon from '@mui/icons-material/Badge';
import Navbar from '../components/Navbar';
import ImageUpload from '../components/ImageUpload';

const ClienteForm = () => {
  const [form, setForm] = useState({
    nit: '',
    nombre: '',
    administrador: '',
    correo: '',
    tipo_codigo: '',
    logo_url: ''
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogoUpload = (url) => {
    setForm({ ...form, logo_url: url });
  };

  const handleSubmit = async () => {
    // Validar campos requeridos
    if (!form.nit || !form.nombre || !form.administrador || !form.correo || !form.tipo_codigo) {
      alert('Por favor completa todos los campos');
      return;
    }

    setLoading(true);
    try {
      await axios.post('/clientes', form);
      alert('Cliente registrado exitosamente');
      navigate('/dashboard');
    } catch (err) {
      console.error('Error al registrar cliente:', err);
      
      if (err.response?.status === 400) {
        const errorMessage = err.response?.data?.message || 'Error en los datos enviados';
        alert(`Error: ${errorMessage}`);
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
          <BusinessIcon sx={{ fontSize: 60, color: '#1976d2', mb: 2 }} />
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600, color: '#1976d2', mb: 1 }}>
            Registrar Cliente
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Completa la información del cliente para crear su perfil
          </Typography>
        </Box>

        <Grid container spacing={3}>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              label="NIT"
              value={form.nit}
              onChange={(e) => setForm({ ...form, nit: e.target.value })}
              fullWidth
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <BadgeIcon color="primary" />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              label="Tipo de Código"
              value={form.tipo_codigo}
              onChange={(e) => setForm({ ...form, tipo_codigo: e.target.value.toUpperCase() })}
              fullWidth
              required
              placeholder="Ej: AL, CO, MX"
              helperText="Código de 2-3 letras para identificar el cliente"
            />
          </Grid>

          <Grid size={{ xs: 12 }}>
            <TextField
              label="Nombre de la Empresa"
              value={form.nombre}
              onChange={(e) => setForm({ ...form, nombre: e.target.value })}
              fullWidth
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <BusinessIcon color="primary" />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              label="Nombre del Administrador"
              value={form.administrador}
              onChange={(e) => setForm({ ...form, administrador: e.target.value })}
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

          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              label="Correo Electrónico"
              type="email"
              value={form.correo}
              onChange={(e) => setForm({ ...form, correo: e.target.value })}
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
        </Grid>

        {/* Campo de logo */}
        <Box sx={{ mt: 3, mb: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            Logo del Cliente
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Este logo aparecerá en los PDFs de los informes de este cliente
          </Typography>
          
          {/* Vista previa del logo */}
          {form.logo_url && (
            <Box sx={{ mb: 3, textAlign: 'center' }}>
              <Typography variant="subtitle2" sx={{ mb: 2 }}>
                Vista previa del logo:
              </Typography>
              <Avatar
                src={`${axios.defaults.baseURL}${form.logo_url}`}
                alt="Logo del cliente"
                sx={{ 
                  width: 120, 
                  height: 120, 
                  mx: 'auto',
                  border: '3px solid #1976d2',
                  boxShadow: 3
                }}
              />
            </Box>
          )}
          
          <ImageUpload
            onUpload={handleLogoUpload}
            images={form.logo_url ? [form.logo_url] : []}
            onRemove={() => setForm({ ...form, logo_url: '' })}
          />
        </Box>

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
            {loading ? 'Registrando...' : 'Registrar Cliente'}
          </Button>
        </Box>
      </Paper>
    </Container>
    </>
  );
};

export default ClienteForm;
