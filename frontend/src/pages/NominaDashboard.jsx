import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Avatar,
  Chip,
  Stack,
  Alert,
  CircularProgress
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import BusinessIcon from '@mui/icons-material/Business';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import Navbar from '../components/Navbar';
import axios from '../api/axiosConfig';
import ImageUpload from '../components/ImageUpload';

const emptyForm = {
  nombre: '',
  nit: '',
  telefono: '',
  correo: '',
  direccion: '',
  logo_url: ''
};

const NominaDashboard = () => {
  const [empresas, setEmpresas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [uploadedImages, setUploadedImages] = useState([]);
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [nitLookup, setNitLookup] = useState(null);
  const [searchingNit, setSearchingNit] = useState(false);
  const [requestMessage, setRequestMessage] = useState('');

  const loadEmpresas = async () => {
    try {
      setLoading(true);
      const res = await axios.get('/empresas');
      setEmpresas(res.data || []);
    } catch (err) {
      console.error('Error al cargar empresas:', err);
      alert('No se pudieron cargar las empresas de nómina.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEmpresas();
  }, []);

  const handleOpenDialog = (empresa = null) => {
    setNitLookup(null);
    setRequestMessage('');
    if (empresa) {
      setEditingId(empresa.id);
      setForm({
        nombre: empresa.nombre || '',
        nit: empresa.nit || '',
        telefono: empresa.telefono || '',
        correo: empresa.correo || '',
        direccion: empresa.direccion || '',
        logo_url: empresa.logo_url || ''
      });
      setUploadedImages(empresa.logo_url ? [empresa.logo_url] : []);
    } else {
      setEditingId(null);
      setForm(emptyForm);
      setUploadedImages([]);
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    if (saving) return;
    setDialogOpen(false);
    setNitLookup(null);
  };

  const handleSave = async () => {
    if (!form.nombre || !form.nit || !form.telefono || !form.correo) {
      alert('Por favor completa todos los campos obligatorios.');
      return;
    }
    if (!editingId && nitLookup?.found && !nitLookup?.tiene_acceso) {
      alert('Esta empresa ya existe. Solicita acceso al propietario en lugar de crear un duplicado.');
      return;
    }
    if (editingId) {
      const empresa = empresas.find((e) => e.id === editingId);
      if (empresa && !empresa.es_propietario) {
        alert('Solo el propietario puede editar esta empresa.');
        return;
      }
    }
    setSaving(true);
    try {
      if (editingId) {
        await axios.put(`/empresas/${editingId}`, form);
        alert('Empresa actualizada correctamente.');
      } else {
        await axios.post('/empresas', form);
        alert('Empresa creada correctamente.');
      }
      setDialogOpen(false);
      await loadEmpresas();
    } catch (err) {
      console.error('Error guardando la empresa:', err);
      alert(err.response?.data?.message || 'Error al guardar la empresa.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (empresaId) => {
    if (!window.confirm('¿Seguro que quieres eliminar esta empresa?')) return;
    const empresa = empresas.find((e) => e.id === empresaId);
    if (empresa && !empresa.es_propietario) {
      alert('Solo el propietario puede eliminar esta empresa.');
      return;
    }
    try {
      await axios.delete(`/empresas/${empresaId}`);
      alert('Empresa eliminada.');
      await loadEmpresas();
    } catch (err) {
      console.error('Error eliminando la empresa:', err);
      alert(err.response?.data?.message || 'No se pudo eliminar la empresa.');
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
        alert('Ya tienes acceso a esta empresa. Se mostrará en tu listado.');
        setDialogOpen(false);
        await loadEmpresas();
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
    try {
      await axios.post(`/empresas/${nitLookup.empresa.id}/solicitudes`, {
        mensaje: requestMessage
      });
      alert('Solicitud enviada al propietario.');
      setRequestMessage('');
      setNitLookup({ ...nitLookup, solicitud_pendiente: true });
    } catch (err) {
      console.error('Error enviando la solicitud:', err);
      alert(err.response?.data?.message || 'No se pudo enviar la solicitud.');
    }
  };

  return (
    <>
      <Navbar />
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, mb: 4 }}>
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2' }}>
                Panel de Nómina
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Gestiona las empresas para las cuales emitirás nómina y soportes.
              </Typography>
            </Box>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenDialog()}>
              Nueva empresa
            </Button>
          </Stack>

          {loading ? (
            <Typography variant="body1">Cargando empresas...</Typography>
          ) : empresas.length === 0 ? (
            <Card sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Aún no tienes empresas
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Crea la primera empresa para comenzar a gestionar nóminas.
              </Typography>
              <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenDialog()}>
                Crear empresa
              </Button>
            </Card>
          ) : (
            <Grid container spacing={3}>
              {empresas.map((empresa) => (
                <Grid size={{ xs: 12, sm: 6, md: 4 }} key={empresa.id}>
                  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                        <Avatar
                          src={empresa.logo_url ? `${axios.defaults.baseURL}${empresa.logo_url}` : undefined}
                          alt={empresa.nombre}
                          sx={{ width: 56, height: 56, bgcolor: '#e3f2fd' }}
                        >
                          {!empresa.logo_url && <BusinessIcon color="primary" />}
                        </Avatar>
                        <Box>
                          <Typography variant="h6">{empresa.nombre}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            NIT: {empresa.nit}
                          </Typography>
                        </Box>
                      </Stack>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        Tel: {empresa.telefono}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        Correo: {empresa.correo}
                      </Typography>
                      {!empresa.es_propietario && (
                        <Typography variant="body2" color="text.secondary">
                          Propietario: {empresa.owner_nombre || 'No disponible'}
                        </Typography>
                      )}
                      {empresa.direccion && (
                        <Typography variant="body2" color="text.secondary">
                          {empresa.direccion}
                        </Typography>
                      )}
                    </CardContent>
                    <CardActions sx={{ justifyContent: 'space-between' }}>
                      <Chip
                        label={empresa.es_propietario ? 'Propietario' : 'Compartida'}
                        size="small"
                        color={empresa.es_propietario ? 'primary' : 'default'}
                        variant={empresa.es_propietario ? 'filled' : 'outlined'}
                      />
                      <Box>
                        {empresa.es_propietario && (
                          <>
                            <IconButton color="primary" onClick={() => handleOpenDialog(empresa)}>
                              <EditIcon />
                            </IconButton>
                            <IconButton color="error" onClick={() => handleDelete(empresa.id)}>
                              <DeleteIcon />
                            </IconButton>
                          </>
                        )}
                      </Box>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </Container>

      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{editingId ? 'Editar empresa de nómina' : 'Nueva empresa de nómina'}</DialogTitle>
        <DialogContent>
          <TextField
            label="Nombre de la Empresa *"
            value={form.nombre}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })}
            fullWidth
            margin="normal"
            disabled={!editingId && nitLookup?.found && !nitLookup?.tiene_acceso}
          />
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems={{ sm: 'flex-end' }}>
            <TextField
              label="NIT *"
              value={form.nit}
              onChange={(e) => setForm({ ...form, nit: e.target.value })}
              fullWidth
              margin="normal"
              disabled={!!editingId}
            />
            {!editingId && (
              <Button
                variant="outlined"
                onClick={handleNitSearch}
                sx={{ minWidth: 180, mb: { xs: 2, sm: 0 } }}
                disabled={searchingNit}
              >
                {searchingNit ? <CircularProgress size={18} /> : 'Buscar por NIT'}
              </Button>
            )}
          </Stack>
          {!editingId && nitLookup && (
            nitLookup.found ? (
              <Alert severity={nitLookup.solicitud_pendiente ? 'info' : nitLookup.tiene_acceso ? 'success' : 'warning'} sx={{ mt: 1 }}>
                {nitLookup.tiene_acceso
                  ? 'Ya tienes acceso a esta empresa.'
                  : nitLookup.solicitud_pendiente
                    ? 'Solicitud pendiente. El propietario debe aprobar el acceso.'
                    : `La empresa ${nitLookup.empresa?.nombre || ''} ya existe. Solicita acceso al propietario.`}
              </Alert>
            ) : (
              <Alert severity="success" sx={{ mt: 1 }}>
                No se encontró una empresa con ese NIT. Puedes registrarla.
              </Alert>
            )
          )}
          {!editingId && nitLookup?.found && (
            <Box sx={{ mt: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                {nitLookup.empresa?.nombre}
              </Typography>
              <Typography variant="body2">Tel: {nitLookup.empresa?.telefono}</Typography>
              <Typography variant="body2">Correo: {nitLookup.empresa?.correo}</Typography>
              <Typography variant="body2" color="text.secondary">
                Propietario: {nitLookup.owner?.nombre} ({nitLookup.owner?.email})
              </Typography>
            </Box>
          )}
          <TextField
            label="Teléfono *"
            value={form.telefono}
            onChange={(e) => setForm({ ...form, telefono: e.target.value })}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Correo *"
            type="email"
            value={form.correo}
            onChange={(e) => setForm({ ...form, correo: e.target.value })}
            fullWidth
            margin="normal"
            disabled={!editingId && nitLookup?.found && !nitLookup?.tiene_acceso}
          />
          <TextField
            label="Dirección"
            value={form.direccion}
            onChange={(e) => setForm({ ...form, direccion: e.target.value })}
            fullWidth
            margin="normal"
            multiline
            rows={2}
            disabled={!editingId && nitLookup?.found && !nitLookup?.tiene_acceso}
          />
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              Logo (opcional)
            </Typography>
            <ImageUpload onUpload={handleLogoUpload} images={uploadedImages} onRemove={handleLogoRemove} />
          </Box>
          {!editingId && nitLookup?.found && !nitLookup.tiene_acceso && !nitLookup.solicitud_pendiente && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle1" sx={{ mb: 1 }}>
                Solicitar acceso al propietario
              </Typography>
              <TextField
                label="Mensaje para el propietario (opcional)"
                value={requestMessage}
                onChange={(e) => setRequestMessage(e.target.value)}
                fullWidth
                margin="normal"
                multiline
                rows={2}
              />
              <Button variant="contained" onClick={handleRequestAccess}>
                Enviar solicitud
              </Button>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={saving}>
            Cancelar
          </Button>
          <Button
            variant="contained"
            onClick={handleSave}
            disabled={saving || (!editingId && nitLookup?.found && !nitLookup?.tiene_acceso)}
          >
            {saving ? 'Guardando...' : 'Guardar'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default NominaDashboard;

