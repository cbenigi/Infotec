import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
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
import Navbar from '../components/Navbar';
import axios from '../api/axiosConfig';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import FilterListIcon from '@mui/icons-material/FilterList';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';

const ESTADOS = [
  { value: 'todos', label: 'Todos', color: 'default' },
  { value: 'borrador', label: 'Borrador', color: 'default' },
  { value: 'emitida', label: 'Emitida', color: 'info' },
  { value: 'recibida', label: 'Recibida', color: 'success' },
  { value: 'cerrada', label: 'Cerrada', color: 'primary' }
];

const getEstadoMeta = (estado) => ESTADOS.find((opt) => opt.value === estado) || ESTADOS[0];

const OrdenCompraHistorial = () => {
  const navigate = useNavigate();
  const [ordenes, setOrdenes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtroEstado, setFiltroEstado] = useState('todos');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [ordenToDelete, setOrdenToDelete] = useState(null);
  const [generatingPdfId, setGeneratingPdfId] = useState(null);

  useEffect(() => {
    loadOrdenes();
  }, []);

  const loadOrdenes = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/ordenes-compra');
      setOrdenes(response.data);
    } catch (error) {
      console.error('Error cargando órdenes de compra:', error);
      alert('Error al cargar órdenes de compra: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  const filteredOrdenes = ordenes.filter((orden) => {
    if (filtroEstado === 'todos') return true;
    return orden.estado === filtroEstado;
  });

  const handleDelete = async () => {
    if (!ordenToDelete) return;
    try {
      await axios.delete(`/orden-compra/${ordenToDelete.id}`);
      alert('Orden eliminada exitosamente');
      setDeleteDialogOpen(false);
      setOrdenToDelete(null);
      loadOrdenes();
    } catch (error) {
      alert('Error al eliminar la orden: ' + (error.response?.data?.message || error.message));
    }
  };

  const handleGeneratePdf = async (ordenId) => {
    setGeneratingPdfId(ordenId);
    try {
      const response = await axios.post(`/generar-pdf-orden/${ordenId}`, {}, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `orden-compra-${ordenId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('Error al generar PDF: ' + (error.response?.data?.message || error.message));
    } finally {
      setGeneratingPdfId(null);
    }
  };

  return (
    <>
      <Navbar />
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <ShoppingCartIcon sx={{ fontSize: 40, color: '#1976d2', mr: 2 }} />
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2' }}>
                  Órdenes de Compra
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Controla tus solicitudes de compra y proveedores
                </Typography>
              </Box>
            </Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/orden-compra/nueva')}
              size="large"
              sx={{
                backgroundColor: '#1976d2',
                '&:hover': { backgroundColor: '#1565c0' }
              }}
            >
              Nueva Orden
            </Button>
          </Box>

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
                sx={{ minWidth: 180 }}
              >
                {ESTADOS.map((estado) => (
                  <MenuItem key={estado.value} value={estado.value}>
                    {estado.label}
                  </MenuItem>
                ))}
              </TextField>
              {filtroEstado !== 'todos' && (
                <Button size="small" onClick={() => setFiltroEstado('todos')}>
                  Limpiar Filtros
                </Button>
              )}
            </Box>
          </Paper>

          {loading ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography>Cargando órdenes...</Typography>
            </Box>
          ) : filteredOrdenes.length === 0 ? (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <ShoppingCartIcon sx={{ fontSize: 64, color: '#ccc', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No hay órdenes registradas
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                {ordenes.length === 0
                  ? 'Crea tu primera orden de compra para controlar tus requisiciones'
                  : 'No se encontraron órdenes con el filtro aplicado'}
              </Typography>
              <Button variant="contained" startIcon={<AddIcon />} onClick={() => navigate('/orden-compra/nueva')}>
                Crear Orden
              </Button>
            </Paper>
          ) : (
            <Grid container spacing={3}>
              {filteredOrdenes.map((orden) => {
                const estadoMeta = getEstadoMeta(orden.estado);
                return (
                  <Grid item xs={12} md={6} lg={4} key={orden.id}>
                    <Card
                      sx={{
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        '&:hover': { boxShadow: 4, transform: 'translateY(-3px)' },
                        transition: 'all 0.2s ease'
                      }}
                    >
                      <CardContent sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Box>
                            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976d2' }}>
                              {orden.numero}
                            </Typography>
                            <Typography variant="caption" color="textSecondary">
                              Creada el {new Date(orden.fecha_creacion).toLocaleDateString('es-CO')}
                            </Typography>
                          </Box>
                          <Chip label={estadoMeta.label} color={estadoMeta.color} size="small" sx={{ fontWeight: 'bold' }} />
                        </Box>

                        <Divider sx={{ my: 1.5 }} />

                        <Typography variant="body2" color="textSecondary">
                          <strong>Comprador:</strong> {orden.comprador_nombre}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          <strong>Proveedor:</strong> {orden.proveedor_nombre}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          <strong>Items:</strong> {orden.total_items}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          <strong>Subtotal:</strong>{' '}
                          {orden.subtotal ? `$ ${Number(orden.subtotal).toLocaleString('es-CO')}` : 'Pendiente'}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          <strong>IVA:</strong>{' '}
                          {orden.iva ? `$ ${Number(orden.iva).toLocaleString('es-CO')}` : 'Pendiente'}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          <strong>Total:</strong>{' '}
                          {orden.total ? `$ ${Number(orden.total).toLocaleString('es-CO')}` : 'Pendiente'}
                        </Typography>
                        {orden.fecha_entrega && (
                          <Typography variant="body2" color="textSecondary">
                            <strong>Entrega:</strong> {new Date(orden.fecha_entrega).toLocaleDateString('es-CO')}
                          </Typography>
                        )}
                      </CardContent>
                      <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                        <Box>
                          <IconButton color="primary" onClick={() => navigate(`/orden-compra/${orden.id}`)} size="small">
                            <EditIcon />
                          </IconButton>
                          <IconButton
                            color="error"
                            onClick={() => {
                              setOrdenToDelete(orden);
                              setDeleteDialogOpen(true);
                            }}
                            size="small"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                        <Button
                          variant="contained"
                          size="small"
                          startIcon={<PictureAsPdfIcon />}
                          onClick={() => handleGeneratePdf(orden.id)}
                          disabled={generatingPdfId === orden.id}
                          sx={{
                            backgroundColor: '#e91e63',
                            '&:hover': { backgroundColor: '#c2185b' }
                          }}
                        >
                          {generatingPdfId === orden.id ? 'Generando...' : 'PDF'}
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          )}
        </Box>
      </Container>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Eliminar orden de compra</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Seguro que deseas eliminar la orden <strong>{ordenToDelete?.numero}</strong>? Esta acción no se puede deshacer.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancelar</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default OrdenCompraHistorial;

