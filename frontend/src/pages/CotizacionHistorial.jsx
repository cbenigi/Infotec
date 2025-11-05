import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Divider
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from '../api/axiosConfig';
import Navbar from '../components/Navbar';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import RequestQuoteIcon from '@mui/icons-material/RequestQuote';
import VisibilityIcon from '@mui/icons-material/Visibility';
import FilterListIcon from '@mui/icons-material/FilterList';

const CotizacionHistorial = () => {
  const navigate = useNavigate();
  const [cotizaciones, setCotizaciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [cotizacionToDelete, setCotizacionToDelete] = useState(null);
  const [generatingPdfId, setGeneratingPdfId] = useState(null);
  
  // Filtros
  const [filtroEstado, setFiltroEstado] = useState('todos');
  const [filtroFecha, setFiltroFecha] = useState('');

  useEffect(() => {
    loadCotizaciones();
  }, []);

  const loadCotizaciones = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/cotizaciones');
      setCotizaciones(response.data);
    } catch (err) {
      console.error('Error cargando cotizaciones:', err);
      alert('Error al cargar cotizaciones: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!cotizacionToDelete) return;

    try {
      await axios.delete(`/cotizacion/${cotizacionToDelete.id}`);
      alert('Cotización eliminada exitosamente');
      setDeleteDialogOpen(false);
      setCotizacionToDelete(null);
      loadCotizaciones();
    } catch (err) {
      alert('Error al eliminar cotización: ' + (err.response?.data?.message || err.message));
    }
  };

  const handleGeneratePdf = async (cotizacionId) => {
    setGeneratingPdfId(cotizacionId);
    try {
      const response = await axios.post(`/generar-pdf-cotizacion/${cotizacionId}`, {}, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `cotizacion-${cotizacionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      // Recargar para actualizar estado si cambió
      loadCotizaciones();
    } catch (err) {
      console.error('Error generando PDF:', err);
      alert('Error al generar PDF: ' + (err.response?.data?.message || err.message));
    } finally {
      setGeneratingPdfId(null);
    }
  };

  const getEstadoColor = (estado) => {
    switch (estado) {
      case 'pendiente':
        return 'warning';
      case 'enviada':
        return 'info';
      case 'aprobada':
        return 'success';
      case 'rechazada':
        return 'error';
      default:
        return 'default';
    }
  };

  const getEstadoLabel = (estado) => {
    switch (estado) {
      case 'pendiente':
        return 'Pendiente';
      case 'enviada':
        return 'Enviada';
      case 'aprobada':
        return 'Aprobada';
      case 'rechazada':
        return 'Rechazada';
      default:
        return estado;
    }
  };

  // Filtrar cotizaciones
  const cotizacionesFiltradas = cotizaciones.filter(cotizacion => {
    if (filtroEstado !== 'todos' && cotizacion.estado !== filtroEstado) {
      return false;
    }
    if (filtroFecha && !cotizacion.fecha_creacion.startsWith(filtroFecha)) {
      return false;
    }
    return true;
  });

  return (
    <>
      <Navbar />
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, mb: 4 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <RequestQuoteIcon sx={{ fontSize: 40, color: '#1976d2', mr: 2 }} />
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2' }}>
                  Historial de Cotizaciones
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Gestione sus solicitudes de cotización
                </Typography>
              </Box>
            </Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/cotizacion/nueva')}
              size="large"
              sx={{ 
                backgroundColor: '#1976d2',
                '&:hover': { backgroundColor: '#1565c0' }
              }}
            >
              Nueva Cotización
            </Button>
          </Box>

          {/* Filtros */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
              <FilterListIcon sx={{ color: '#1976d2' }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                Filtros:
              </Typography>
              <TextField
                select
                label="Estado"
                value={filtroEstado}
                onChange={(e) => setFiltroEstado(e.target.value)}
                size="small"
                sx={{ minWidth: 150 }}
              >
                <MenuItem value="todos">Todos</MenuItem>
                <MenuItem value="pendiente">Pendiente</MenuItem>
                <MenuItem value="enviada">Enviada</MenuItem>
                <MenuItem value="aprobada">Aprobada</MenuItem>
                <MenuItem value="rechazada">Rechazada</MenuItem>
              </TextField>
              <TextField
                label="Fecha"
                type="date"
                value={filtroFecha}
                onChange={(e) => setFiltroFecha(e.target.value)}
                size="small"
                InputLabelProps={{ shrink: true }}
                sx={{ minWidth: 180 }}
              />
              {(filtroEstado !== 'todos' || filtroFecha) && (
                <Button
                  size="small"
                  onClick={() => {
                    setFiltroEstado('todos');
                    setFiltroFecha('');
                  }}
                >
                  Limpiar Filtros
                </Button>
              )}
            </Box>
          </Paper>

          {/* Lista de Cotizaciones */}
          {loading ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography>Cargando cotizaciones...</Typography>
            </Box>
          ) : cotizacionesFiltradas.length === 0 ? (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <RequestQuoteIcon sx={{ fontSize: 64, color: '#ccc', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No hay cotizaciones
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                {cotizaciones.length === 0 
                  ? 'Comience creando su primera solicitud de cotización'
                  : 'No se encontraron cotizaciones con los filtros aplicados'}
              </Typography>
              {cotizaciones.length === 0 && (
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/cotizacion/nueva')}
                >
                  Crear Primera Cotización
                </Button>
              )}
            </Paper>
          ) : (
            <Grid container spacing={3}>
              {cotizacionesFiltradas.map((cotizacion) => (
                <Grid item xs={12} md={6} lg={4} key={cotizacion.id}>
                  <Card 
                    sx={{ 
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: 4
                      }
                    }}
                  >
                    <CardContent sx={{ flexGrow: 1 }}>
                      {/* Header */}
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Box>
                          <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976d2' }}>
                            Cotización #{cotizacion.id}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {new Date(cotizacion.fecha_creacion).toLocaleString('es-ES')}
                          </Typography>
                        </Box>
                        <Chip
                          label={getEstadoLabel(cotizacion.estado)}
                          color={getEstadoColor(cotizacion.estado)}
                          size="small"
                          sx={{ fontWeight: 'bold' }}
                        />
                      </Box>

                      <Divider sx={{ mb: 2 }} />

                      {/* Info */}
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="body2" color="textSecondary">
                          <strong>Supervisor:</strong> {cotizacion.supervisor}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          <strong>Items:</strong> {cotizacion.total_items} producto(s)/servicio(s)
                        </Typography>
                      </Box>

                      {cotizacion.observaciones && (
                        <Box sx={{ mt: 2, p: 1, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
                          <Typography variant="caption" color="textSecondary">
                            {cotizacion.observaciones.length > 80
                              ? cotizacion.observaciones.substring(0, 80) + '...'
                              : cotizacion.observaciones}
                          </Typography>
                        </Box>
                      )}
                    </CardContent>

                    <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                      <Box>
                        <IconButton
                          color="primary"
                          onClick={() => navigate(`/cotizacion/${cotizacion.id}`)}
                          title="Editar"
                          size="small"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          color="error"
                          onClick={() => {
                            setCotizacionToDelete(cotizacion);
                            setDeleteDialogOpen(true);
                          }}
                          title="Eliminar"
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<PictureAsPdfIcon />}
                        onClick={() => handleGeneratePdf(cotizacion.id)}
                        disabled={generatingPdfId === cotizacion.id}
                        sx={{
                          backgroundColor: '#e91e63',
                          '&:hover': { backgroundColor: '#c2185b' }
                        }}
                      >
                        {generatingPdfId === cotizacion.id ? 'Generando...' : 'PDF'}
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </Container>

      {/* Dialog de Confirmación de Eliminación */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirmar Eliminación</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Está seguro que desea eliminar la cotización #{cotizacionToDelete?.id}?
          </Typography>
          <Typography variant="body2" color="error" sx={{ mt: 1 }}>
            Esta acción no se puede deshacer.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancelar
          </Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default CotizacionHistorial;

