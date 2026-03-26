import React, { useEffect, useState } from 'react';
import { Container, Typography, List, ListItem, ListItemText, Button, Box, Grid, Paper, Card, CardContent, CardActions, IconButton, ListItemSecondaryAction, Dialog, DialogContent, DialogTitle, DialogActions, TextField, Alert, Skeleton } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from '../api/axiosConfig';
import Navbar from '../components/Navbar';
import Loader from '../components/Loader';
import AddIcon from '@mui/icons-material/Add';
import BusinessIcon from '@mui/icons-material/Business';
import SupervisorAccountIcon from '@mui/icons-material/SupervisorAccount';
import AssignmentIcon from '@mui/icons-material/Assignment';
import { Download, Visibility, Delete, Email } from '@mui/icons-material';

const Dashboard = () => {
  const [visitas, setVisitas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingPDF, setLoadingPDF] = useState(false);
  const [emailDialogOpen, setEmailDialogOpen] = useState(false);
  const [selectedVisita, setSelectedVisita] = useState(null);
  const [emailDestino, setEmailDestino] = useState('');
  const [sendingEmail, setSendingEmail] = useState(false);
  const [solicitudesAcceso, setSolicitudesAcceso] = useState([]);
  const [solicitudesDialogOpen, setSolicitudesDialogOpen] = useState(false);
  const [gestionandoSolicitud, setGestionandoSolicitud] = useState(false);
  const navigate = useNavigate();
  const rol = localStorage.getItem('rol') || 'aseo';
  const [isSyncing, setIsSyncing] = useState(false);
  const [offlineVisitas, setOfflineVisitas] = useState([]);

  const handleDownloadPDF = async (visitaId) => {
    setLoadingPDF(true);
    try {
      const response = await axios.post(`/generar-pdf/${visitaId}`, {}, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `visita-${visitaId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error al descargar PDF:', error);
      alert('Error al descargar el PDF');
    } finally {
      setLoadingPDF(false);
    }
  };

  const handleDeleteVisita = async (visitaId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta visita? Esta acción no se puede deshacer.')) {
      try {
        await axios.delete(`/visita/${visitaId}`);
        alert('Visita eliminada exitosamente');
        // Recargar la lista de visitas
        const res = await axios.get('/visitas');
        setVisitas(res.data);
      } catch (error) {
        console.error('Error al eliminar visita:', error);
        alert('Error al eliminar la visita');
      }
    }
  };

  const handleOpenEmailDialog = (visita) => {
    setSelectedVisita(visita);
    setEmailDestino('');
    setEmailDialogOpen(true);
  };

  const handleCloseEmailDialog = () => {
    setEmailDialogOpen(false);
    setSelectedVisita(null);
    setEmailDestino('');
  };

  const handleSendEmail = async () => {
    if (!emailDestino || !emailDestino.includes('@')) {
      alert('Por favor ingresa un correo electrónico válido');
      return;
    }

    setSendingEmail(true);
    try {
      await axios.post(`/enviar-informe/${selectedVisita.id}`, {
        email_destino: emailDestino
      });
      
      alert('¡Correo enviado exitosamente!');
      handleCloseEmailDialog();
    } catch (error) {
      console.error('Error al enviar correo:', error);
      const errorMsg = error.response?.data?.message || 'Error al enviar el correo. Por favor intenta de nuevo.';
      alert(errorMsg);
    } finally {
      setSendingEmail(false);
    }
  };

  const syncOfflineVisitas = async () => {
    const pending = JSON.parse(localStorage.getItem('pending_visitas') || '[]');
    if (pending.length === 0) return;

    setIsSyncing(true);
    let successCount = 0;
    const stillPending = [];

    for (const visita of pending) {
      try {
        const { id, offline, ...cleanData } = visita;
        await axios.post('/visita', cleanData);
        successCount++;
      } catch (err) {
        console.error('Individual sync error:', err);
        stillPending.push(visita);
      }
    }

    localStorage.setItem('pending_visitas', JSON.stringify(stillPending));
    setOfflineVisitas(stillPending);
    setIsSyncing(false);

    if (successCount > 0) {
      alert(`✅ Se sincronizaron ${successCount} visitas pendientes.`);
      // fetchVisitas se llamará vía visitaUpdated o manualmente
      window.dispatchEvent(new Event('visitaUpdated'));
    }
  };

  const fetchVisitasData = async () => {
    try {
      setLoading(true);
      // Mostrar offline rápido
      setOfflineVisitas(JSON.parse(localStorage.getItem('pending_visitas') || '[]'));

      let url = '/visitas';
      try {
        const emp = await axios.get('/empresa');
        if (emp.data?.exists && emp.data.id) url = `/visitas?empresa_id=${emp.data.id}`;
      } catch {}

      const role = localStorage.getItem('rol');
      if (url === '/visitas' && role === 'admin') url = '/visitas?all=true';
      if (url === '/visitas') {
        const subId = localStorage.getItem('userId');
        if (subId) url = `/visitas?supervisor_id=${subId}`;
      }

      const res = await axios.get(url);
      setVisitas(res.data);
    } catch (err) {
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVisitasData();
    syncOfflineVisitas();

    const handleUpdated = () => fetchVisitasData();
    const handleVisibility = () => { if (document.visibilityState === 'visible') fetchVisitasData(); };
    
    window.addEventListener('visitaUpdated', handleUpdated);
    window.addEventListener('online', syncOfflineVisitas);
    document.addEventListener('visibilitychange', handleVisibility);
    
    return () => {
      window.removeEventListener('visitaUpdated', handleUpdated);
      window.removeEventListener('online', syncOfflineVisitas);
      document.removeEventListener('visibilitychange', handleVisibility);
    };
  }, []);

  useEffect(() => {
    if (rol === 'nomina') return;
    const fetchSolicitudes = async () => {
      try {
        const res = await axios.get('/empresa/solicitudes');
        if (Array.isArray(res.data) && res.data.length > 0) {
          setSolicitudesAcceso(res.data);
          setSolicitudesDialogOpen(true);
        } else {
          setSolicitudesAcceso([]);
        }
      } catch (err) {
        console.error('Error al obtener solicitudes de empresas:', err);
      }
    };
    fetchSolicitudes();
  }, [rol]);

  const handleResolverSolicitud = async (solicitudId, accion) => {
    try {
      setGestionandoSolicitud(true);
      await axios.put(`/empresa/solicitudes/${solicitudId}`, { accion });
      const restantes = solicitudesAcceso.filter((s) => s.id !== solicitudId);
      setSolicitudesAcceso(restantes);
      if (restantes.length === 0) {
        setSolicitudesDialogOpen(false);
      }
    } catch (err) {
      console.error('Error al actualizar la solicitud:', err);
      alert(err.response?.data?.message || 'No se pudo procesar la solicitud.');
    } finally {
      setGestionandoSolicitud(false);
    }
  };

  return (
    <>
      <Navbar />
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 3 }}>
            Panel de Control
          </Typography>
          
          {/* Tarjetas de acciones rápidas */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ height: '100%', '&:hover': { boxShadow: 6 } }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <AssignmentIcon sx={{ fontSize: 40, color: '#1976d2', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Nueva Visita
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Crear un nuevo informe de visita técnica
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                  <Button 
                    variant="contained" 
                    onClick={() => navigate('/visita')}
                    startIcon={<AddIcon />}
                    fullWidth
                  >
                    Crear Visita
                  </Button>
                </CardActions>
              </Card>
            </Grid>

            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ height: '100%', '&:hover': { boxShadow: 6 } }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <BusinessIcon sx={{ fontSize: 40, color: '#1976d2', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Registrar Cliente
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Agregar un nuevo cliente al sistema
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                  <Button 
                    variant="contained" 
                    onClick={() => navigate('/clientes/new')}
                    startIcon={<AddIcon />}
                    fullWidth
                  >
                    Nuevo Cliente
                  </Button>
                </CardActions>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ height: '100%', '&:hover': { boxShadow: 6 } }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <BusinessIcon sx={{ fontSize: 40, color: '#1976d2', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Registrar Proveedor
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Administra tus proveedores para órdenes de compra
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                  <Button
                    variant="contained"
                    onClick={() => navigate('/proveedores/nuevo')}
                    startIcon={<AddIcon />}
                    fullWidth
                  >
                    Nuevo Proveedor
                  </Button>
                </CardActions>
              </Card>
            </Grid>

            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ height: '100%', '&:hover': { boxShadow: 6 } }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <SupervisorAccountIcon sx={{ fontSize: 40, color: '#1976d2', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Registrar Supervisor
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Agregar supervisores y técnicos
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                  <Button 
                    variant="contained" 
                    onClick={() => navigate('/supervisores/new')}
                    startIcon={<AddIcon />}
                    fullWidth
                  >
                    Nuevo Supervisor
                  </Button>
                </CardActions>
              </Card>
            </Grid>

            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ height: '100%', '&:hover': { boxShadow: 6 } }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <BusinessIcon sx={{ fontSize: 40, color: '#1976d2', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Mi Empresa
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Configurar datos de la empresa
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                  <Button 
                    variant="outlined" 
                    onClick={() => navigate('/empresa')}
                    fullWidth
                  >
                    Configurar
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          </Grid>

          {/* Lista de visitas recientes */}
          <Paper elevation={2} sx={{ p: 3 }}>
            {/* Visitas Offline Pendientes */}
            {offlineVisitas.length > 0 && (
              <Box sx={{ mb: 4 }}>
                <Alert 
                  severity="warning" 
                  action={
                    <Button color="inherit" size="small" onClick={syncOfflineVisitas} disabled={isSyncing}>
                      {isSyncing ? 'Sincronizando...' : 'Sincronizar ahora'}
                    </Button>
                  }
                  sx={{ mb: 2, borderRadius: 2 }}
                >
                  Tienes {offlineVisitas.length} visita(s) guardadas localmente esperando conexión.
                </Alert>
                <List>
                  {offlineVisitas.map((v) => (
                    <ListItem 
                      key={v.id} 
                      sx={{ 
                        bgcolor: 'rgba(255, 152, 0, 0.05)',
                        border: '1px dashed #ff9800',
                        borderRadius: 1,
                        mb: 1
                      }}
                    >
                      <ListItemText 
                        primary={`[OFFLINE] Visita - ${v.cliente_nombre || 'Cliente'}`} 
                        secondary={`Pendiente de sincronizar`} 
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
              Visitas Recientes
            </Typography>
            {loading ? (
              <List>
                {[1, 2, 3].map((i) => (
                  <ListItem key={i} sx={{ border: '1px solid #e0e0e0', borderRadius: 1, mb: 1, p: 2 }}>
                    <ListItemText
                      primary={<Skeleton variant="text" width="40%" height={30} />}
                      secondary={<Skeleton variant="text" width="60%" />}
                    />
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Skeleton variant="circular" width={40} height={40} />
                      <Skeleton variant="circular" width={40} height={40} />
                    </Box>
                  </ListItem>
                ))}
              </List>
            ) : visitas.length > 0 ? (
              <List>
        {visitas.map((v) => (
                  <ListItem 
                    key={v.id} 
                    sx={{ 
                      '&:hover': { backgroundColor: '#f5f5f5' },
                      borderRadius: 1,
                      mb: 1,
                      border: '1px solid #e0e0e0'
                    }}
                  >
                    <ListItemText 
                      primary={`Visita ${v.id} - ${v.cliente}`} 
                      secondary={`Fecha: ${v.fecha} | Supervisor: ${v.supervisor}`} 
                    />
                    <ListItemSecondaryAction>
                      <IconButton 
                        edge="end" 
                        onClick={() => navigate(`/visita/${v.id}`)}
                        sx={{ mr: 1 }}
                        title="Ver detalles"
                      >
                        <Visibility />
                      </IconButton>
                      <IconButton 
                        edge="end" 
                        onClick={() => handleDownloadPDF(v.id)}
                        sx={{ mr: 1 }}
                        title="Descargar PDF"
                      >
                        <Download />
                      </IconButton>
                      <IconButton 
                        edge="end" 
                        onClick={() => handleOpenEmailDialog(v)}
                        sx={{ mr: 1, color: '#EA4335' }}
                        title="Enviar por correo"
                      >
                        <Email />
                      </IconButton>
                      <IconButton 
                        edge="end" 
                        onClick={() => handleDeleteVisita(v.id)}
                        title="Eliminar visita"
                        sx={{ color: 'red' }}
                      >
                        <Delete />
                      </IconButton>
                    </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body1" color="text.secondary">
                  No hay visitas registradas aún
                </Typography>
                <Button 
                  variant="contained" 
                  onClick={() => navigate('/visita')} 
                  sx={{ mt: 2 }}
                  startIcon={<AddIcon />}
                >
                  Crear Primera Visita
                </Button>
              </Box>
            )}
          </Paper>
        </Box>
      </Container>
      
      {/* Dialog con Loader para descarga de PDF */}
      <Dialog 
        open={loadingPDF} 
        disableEscapeKeyDown
        disableBackdropClick
        PaperProps={{
          style: {
            backgroundColor: 'transparent',
            boxShadow: 'none',
          },
        }}
      >
        <DialogContent>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" sx={{ mb: 2, color: '#1e3a8a' }}>
              Generando PDF...
            </Typography>
            <Loader />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Dialog para enviar correo */}
      <Dialog 
        open={emailDialogOpen} 
        onClose={handleCloseEmailDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ bgcolor: '#1976d2', color: 'white', display: 'flex', alignItems: 'center' }}>
          <Email sx={{ mr: 1 }} />
          Enviar Informe por Correo
        </DialogTitle>
        <DialogContent sx={{ mt: 3 }}>
          {selectedVisita && (
            <>
              <Typography variant="body1" sx={{ mb: 2 }}>
                <strong>Visita:</strong> {selectedVisita.id}
              </Typography>
              <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
                <strong>Cliente:</strong> {selectedVisita.cliente}
              </Typography>
              <Typography variant="body2" sx={{ mb: 3, color: 'text.secondary' }}>
                <strong>Supervisor:</strong> {selectedVisita.supervisor}
              </Typography>
              <TextField
                autoFocus
                margin="dense"
                label="Correo del Administrador"
                type="email"
                fullWidth
                variant="outlined"
                value={emailDestino}
                onChange={(e) => setEmailDestino(e.target.value)}
                placeholder="ejemplo@empresa.com"
                disabled={sendingEmail}
                helperText="Ingresa el correo del administrador donde se enviará el informe"
              />
            </>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button 
            onClick={handleCloseEmailDialog} 
            disabled={sendingEmail}
          >
            Cancelar
          </Button>
          <Button 
            onClick={handleSendEmail} 
            variant="contained" 
            disabled={sendingEmail || !emailDestino}
            startIcon={sendingEmail ? null : <Email />}
          >
            {sendingEmail ? 'Enviando...' : 'Enviar Correo'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog para solicitudes de acceso a empresas */}
      <Dialog
        open={solicitudesDialogOpen}
        onClose={() => setSolicitudesDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Solicitudes de acceso a empresas</DialogTitle>
        <DialogContent dividers>
          {solicitudesAcceso.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              No tienes solicitudes pendientes.
            </Typography>
          ) : (
            solicitudesAcceso.map((solicitud) => (
              <Box
                key={solicitud.id}
                sx={{
                  border: '1px solid #e0e0e0',
                  borderRadius: 2,
                  p: 2,
                  mb: 2
                }}
              >
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {solicitud.solicitante?.nombre || 'Usuario desconocido'}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {solicitud.solicitante?.email}
                </Typography>
                <Typography variant="body2">
                  Empresa: {solicitud.empresa?.nombre} (NIT: {solicitud.empresa?.nit})
                </Typography>
                {solicitud.mensaje && (
                  <Alert severity="info" sx={{ mt: 1, mb: 1 }}>
                    {solicitud.mensaje}
                  </Alert>
                )}
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2, gap: 1 }}>
                  <Button
                    color="error"
                    onClick={() => handleResolverSolicitud(solicitud.id, 'rechazar')}
                    disabled={gestionandoSolicitud}
                  >
                    Rechazar
                  </Button>
                  <Button
                    variant="contained"
                    onClick={() => handleResolverSolicitud(solicitud.id, 'aprobar')}
                    disabled={gestionandoSolicitud}
                  >
                    Aprobar
                  </Button>
                </Box>
              </Box>
            ))
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSolicitudesDialogOpen(false)} disabled={gestionandoSolicitud}>
            Cerrar
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default Dashboard;