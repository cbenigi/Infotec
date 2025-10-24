import React, { useState, useEffect } from 'react';
import { TextField, Button, Container, Typography, Box, Paper, Avatar } from '@mui/material';
import axios from '../api/axiosConfig';
import { useNavigate } from 'react-router-dom';
import ImageUpload from '../components/ImageUpload';
import BusinessIcon from '@mui/icons-material/Business';

const EmpresaForm = () => {
  const [form, setForm] = useState({
    nombre: '',
    nit: '',
    telefono: '',
    correo: '',
    direccion: '',
    logo_url: ''
  });
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const navigate = useNavigate();

  // Cargar datos existentes de la empresa
  useEffect(() => {
    const loadEmpresaData = async () => {
      try {
        const response = await axios.get('/empresa');
        if (response.data.exists) {
          const empresaData = response.data;
          setForm({
            nombre: empresaData.nombre || '',
            nit: empresaData.nit || '',
            telefono: empresaData.telefono || '',
            correo: empresaData.correo || '',
            direccion: empresaData.direccion || '',
            logo_url: empresaData.logo_url || ''
          });
          setIsEditing(true);
        }
      } catch (err) {
        console.log('No hay empresa registrada aún');
      }
    };
    
    loadEmpresaData();
  }, []);

  const handleSubmit = async () => {
    if (!form.nombre || !form.nit || !form.telefono || !form.correo) {
      alert('Por favor completa todos los campos obligatorios');
      return;
    }

    setLoading(true);
    try {
      if (isEditing) {
        await axios.put('/empresa', form);
        alert('Empresa actualizada exitosamente.');
      } else {
        await axios.post('/empresa', form);
        alert('Empresa registrada exitosamente. Ahora puedes crear clientes y visitas técnicas.');
      }
      navigate('/dashboard');
    } catch (err) {
      alert('Error al guardar empresa: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleLogoUpload = (url) => {
    setForm({ ...form, logo_url: url });
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <BusinessIcon sx={{ fontSize: 60, color: '#1976d2', mb: 2 }} />
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, color: '#1976d2' }}>
              {isEditing ? 'Configurar Empresa' : 'Registra tu Empresa'}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {isEditing 
                ? 'Actualiza la información de tu empresa. Los cambios se reflejarán en los informes.'
                : 'Esta es la empresa que emitirá los informes de visitas técnicas. Solo puedes registrar una empresa.'
              }
            </Typography>
          </Box>

          <TextField
            label="Nombre de la Empresa *"
            value={form.nombre}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })}
            fullWidth
            margin="normal"
          />

          <TextField
            label="NIT *"
            value={form.nit}
            onChange={(e) => setForm({ ...form, nit: e.target.value })}
            fullWidth
            margin="normal"
          />

          <TextField
            label="Teléfono *"
            value={form.telefono}
            onChange={(e) => setForm({ ...form, telefono: e.target.value })}
            fullWidth
            margin="normal"
          />

          <TextField
            label="Correo Electrónico *"
            type="email"
            value={form.correo}
            onChange={(e) => setForm({ ...form, correo: e.target.value })}
            fullWidth
            margin="normal"
          />

          <TextField
            label="Dirección"
            value={form.direccion}
            onChange={(e) => setForm({ ...form, direccion: e.target.value })}
            fullWidth
            margin="normal"
            multiline
            rows={2}
          />

          <Box sx={{ mt: 3, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Logo de la Empresa
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Este logo aparecerá en los PDFs de los informes
            </Typography>
            
            {/* Vista previa del logo */}
            {form.logo_url && (
              <Box sx={{ mb: 3, textAlign: 'center' }}>
                <Typography variant="subtitle2" sx={{ mb: 2 }}>
                  Vista previa del logo:
                </Typography>
                <Avatar
                  src={`${axios.defaults.baseURL}${form.logo_url}`}
                  alt="Logo de la empresa"
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

          <Button
            variant="contained"
            onClick={handleSubmit}
            fullWidth
            size="large"
            disabled={loading}
            sx={{ mt: 3 }}
          >
            {loading ? 'Guardando...' : (isEditing ? 'Actualizar Empresa' : 'Registrar Empresa')}
          </Button>
        </Paper>
      </Box>
    </Container>
  );
};

export default EmpresaForm;

