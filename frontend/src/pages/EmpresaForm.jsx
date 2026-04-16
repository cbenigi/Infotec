import React, { useState, useEffect } from 'react';
import { TextField, Button, Container, Typography, Box, Paper, Avatar, Alert } from '@mui/material';
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
  const [esPropietario, setEsPropietario] = useState(true);
  const [uploadedImages, setUploadedImages] = useState([]);
  const [nitLookup, setNitLookup] = useState(null);
  const [searchingNit, setSearchingNit] = useState(false);
  const [requestMessage, setRequestMessage] = useState('');
  const [sendingRequest, setSendingRequest] = useState(false);
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
          setUploadedImages(empresaData.logo_url ? [empresaData.logo_url] : []);
          setIsEditing(true);
          setEsPropietario(empresaData.es_propietario);
        }
      } catch (err) {
        console.log('No hay empresa registrada aún');
      }
    };
    
    loadEmpresaData();
  }, []);

  const handleSubmit = async () => {
    if (!esPropietario) {
      alert('Solo el propietario puede editar los datos de esta empresa.');
      return;
    }

    if (!form.nombre || !form.nit || !form.telefono || !form.correo) {
      alert('Por favor completa todos los campos obligatorios');
      return;
    }

    setLoading(true);
    try {
      if (isEditing) {
        await axios.put('/empresa', form);
        alert('Empresa actualizada exitosamente.');
        window.dispatchEvent(new CustomEvent('empresaUpdated'));
      } else {
        await axios.post('/empresa', form);
        alert('Empresa registrada exitosamente. Ahora puedes crear clientes y visitas técnicas.');
        window.dispatchEvent(new CustomEvent('empresaUpdated'));
      }
      navigate('/dashboard');
    } catch (err) {
      alert('Error al guardar empresa: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleNitSearch = async () => {
    const nit = (form.nit || '').trim();
    if (!nit) {
      alert('Ingresa un NIT para realizar la búsqueda.');
      return;
    }
    setSearchingNit(true);
    try {
      const res = await axios.get('/empresas/buscar', { params: { nit } });
      if (res.data.found && res.data.tiene_acceso) {
        alert('Ya tienes acceso a esta empresa. Cargando sus datos...');
        const empresaData = res.data.empresa;
        setForm({
          nombre: empresaData.nombre || '',
          nit: empresaData.nit || '',
          telefono: empresaData.telefono || '',
          correo: empresaData.correo || '',
          direccion: empresaData.direccion || '',
          logo_url: empresaData.logo_url || ''
        });
        setUploadedImages(empresaData.logo_url ? [empresaData.logo_url] : []);
        setIsEditing(true);
        setEsPropietario(empresaData.es_propietario);
        setNitLookup(null);
        return;
      }
      setNitLookup(res.data);
    } catch (err) {
      console.error('Error buscando empresa:', err);
      alert(err.response?.data?.message || 'No se pudo buscar la empresa.');
    } finally {
      setSearchingNit(false);
    }
  };

  const handleRequestAccess = async () => {
    if (!nitLookup?.found || !nitLookup.empresa) return;
    setSendingRequest(true);
    try {
      await axios.post(`/empresas/${nitLookup.empresa.id}/solicitudes`, {
        mensaje: requestMessage
      });
      alert('Solicitud enviada al propietario. Espera a que sea aprobada para acceder.');
      setRequestMessage('');
      setNitLookup({ ...nitLookup, solicitud_pendiente: true });
    } catch (err) {
      console.error('Error enviando la solicitud:', err);
      alert(err.response?.data?.message || 'No se pudo enviar la solicitud.');
    } finally {
      setSendingRequest(false);
    }
  };

  const handleLogoUpload = (url) => {
    setForm({ ...form, logo_url: url });
    setUploadedImages([url]);
  };

  const handleLogoRemove = () => {
    setForm({ ...form, logo_url: '' });
    setUploadedImages([]);
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

          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 2 }}>
            <TextField
              label="NIT *"
              value={form.nit}
              onChange={(e) => setForm({ ...form, nit: e.target.value })}
              fullWidth
              disabled={isEditing}
            />
            {!isEditing && (
              <Button
                variant="outlined"
                onClick={handleNitSearch}
                disabled={searchingNit || !form.nit}
                sx={{ height: 56, minWidth: 150 }}
              >
                {searchingNit ? 'Buscando...' : 'Buscar Empresa'}
              </Button>
            )}
          </Box>

          {nitLookup && (
            <Box sx={{ mb: 3 }}>
              {nitLookup.found ? (
                <Paper variant="outlined" sx={{ p: 2, bgcolor: '#f8fbff', borderColor: '#1976d2' }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1976d2', mb: 1 }}>
                    Empresa Encontrada: {nitLookup.empresa?.nombre}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Propietario: {nitLookup.owner?.nombre}
                  </Typography>
                  
                  {nitLookup.solicitud_pendiente ? (
                    <Typography variant="body2" color="primary" sx={{ fontWeight: 600 }}>
                      Ya tienes una solicitud pendiente para esta empresa.
                    </Typography>
                  ) : (
                    <Box sx={{ mt: 2 }}>
                      <TextField
                        label="Mensaje para el propietario (opcional)"
                        fullWidth
                        size="small"
                        multiline
                        rows={2}
                        value={requestMessage}
                        onChange={(e) => setRequestMessage(e.target.value)}
                        placeholder="Soy empleado de esta empresa y necesito registrar visitas..."
                        sx={{ mb: 2 }}
                      />
                      <Button
                        variant="contained"
                        onClick={handleRequestAccess}
                        disabled={sendingRequest}
                        fullWidth
                      >
                        {sendingRequest ? 'Enviando...' : 'Solicitar Acceso'}
                      </Button>
                    </Box>
                  )}
                </Paper>
              ) : (
                <Typography variant="body2" sx={{ color: '#2e7d32', fontWeight: 600 }}>
                  ✓ NIT disponible. Puedes registrar esta nueva empresa.
                </Typography>
              )}
            </Box>
          )}

          <TextField
            label="Nombre de la Empresa *"
            value={form.nombre}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })}
            fullWidth
            margin="normal"
            disabled={!esPropietario || (nitLookup?.found && !nitLookup.tiene_acceso)}
          />

          <TextField
            label="Teléfono *"
            value={form.telefono}
            onChange={(e) => setForm({ ...form, telefono: e.target.value })}
            fullWidth
            margin="normal"
            disabled={!esPropietario || (nitLookup?.found && !nitLookup.tiene_acceso)}
          />

          <TextField
            label="Correo Electrónico *"
            type="email"
            value={form.correo}
            onChange={(e) => setForm({ ...form, correo: e.target.value })}
            fullWidth
            margin="normal"
            disabled={!esPropietario || (nitLookup?.found && !nitLookup.tiene_acceso)}
          />

          <TextField
            label="Dirección"
            value={form.direccion}
            onChange={(e) => setForm({ ...form, direccion: e.target.value })}
            fullWidth
            margin="normal"
            multiline
            rows={2}
            disabled={!esPropietario || (nitLookup?.found && !nitLookup.tiene_acceso)}
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
              images={uploadedImages}
              onRemove={handleLogoRemove}
            />
          </Box>

          {!esPropietario && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Al ser colaborador de esta empresa, no puedes modificar su información básica.
            </Alert>
          )}

          <Button
            variant="contained"
            onClick={handleSubmit}
            fullWidth
            size="large"
            disabled={loading || !esPropietario || (nitLookup?.found && !nitLookup.tiene_acceso)}
            sx={{ mt: 3 }}
          >
            {loading ? 'Guardando...' : (isEditing ? 'Actualizar Empresa' : 'Registrar Empresa')}
          </Button>
          
          {(isEditing || (nitLookup?.found && !nitLookup.tiene_acceso)) && (
            <Button
              variant="text"
              onClick={() => navigate('/dashboard')}
              fullWidth
              sx={{ mt: 1 }}
            >
              Volver al Panel
            </Button>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default EmpresaForm;

