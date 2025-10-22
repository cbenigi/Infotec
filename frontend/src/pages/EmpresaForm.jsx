import React, { useState } from 'react';
import { TextField, Button, Container, Typography, Box, Paper } from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import ImageUpload from '../components/ImageUpload';

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
  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (!form.nombre || !form.nit || !form.telefono || !form.correo) {
      alert('Por favor completa todos los campos obligatorios');
      return;
    }

    setLoading(true);
    try {
      await axios.post('http://localhost:5000/empresa', form);
      alert('Empresa registrada exitosamente. Ahora puedes crear clientes y visitas técnicas.');
      navigate('/dashboard');
    } catch (err) {
      alert('Error al registrar empresa: ' + (err.response?.data?.message || err.message));
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
          <Typography variant="h4" gutterBottom>
            Registra tu Empresa
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Esta es la empresa que emitirá los informes de visitas técnicas. Solo puedes registrar una empresa.
          </Typography>

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
            {loading ? 'Guardando...' : 'Registrar Empresa'}
          </Button>
        </Paper>
      </Box>
    </Container>
  );
};

export default EmpresaForm;

