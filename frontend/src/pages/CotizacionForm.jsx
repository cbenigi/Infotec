import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  TextField,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import axios from '../api/axiosConfig';
import Navbar from '../components/Navbar';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import SaveIcon from '@mui/icons-material/Save';
import RequestQuoteIcon from '@mui/icons-material/RequestQuote';

const CotizacionForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [generatingPdf, setGeneratingPdf] = useState(false);
  
  const [form, setForm] = useState({
    observaciones: ''
  });

  const [items, setItems] = useState([
    { producto_servicio: '', cantidad: '', uso: '' }
  ]);

  const loadCotizacion = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/cotizacion/${id}`);
      const cotizacion = response.data;
      
      setForm({
        observaciones: cotizacion.observaciones || ''
      });
      
      if (cotizacion.items && cotizacion.items.length > 0) {
        setItems(cotizacion.items.map(item => ({
          producto_servicio: item.producto_servicio,
          cantidad: item.cantidad,
          uso: item.uso
        })));
      }
    } catch (err) {
      console.error('Error cargando cotización:', err);
      alert('Error al cargar la cotización: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      loadCotizacion();
    }
  }, [id, loadCotizacion]);

  const addItem = () => {
    setItems([...items, { producto_servicio: '', cantidad: '', uso: '' }]);
  };

  const removeItem = (index) => {
    if (items.length === 1) {
      alert('Debe tener al menos un producto o servicio');
      return;
    }
    setItems(items.filter((_, i) => i !== index));
  };

  const updateItem = (index, field, value) => {
    const newItems = [...items];
    newItems[index][field] = value;
    setItems(newItems);
  };

  const validateForm = () => {
    // Validar que todos los items tengan información
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (!item.producto_servicio.trim() || !item.cantidad.trim() || !item.uso.trim()) {
        alert(`Por favor complete toda la información del item ${i + 1}`);
        return false;
      }
    }
    return true;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      const cotizacionData = {
        observaciones: form.observaciones,
        items: items
      };

      if (id) {
        await axios.put(`/cotizacion/${id}`, cotizacionData);
        alert('Cotización actualizada exitosamente');
      } else {
        const response = await axios.post('/cotizacion', cotizacionData);
        alert('Cotización creada exitosamente');
        navigate(`/cotizacion/${response.data.id}`);
      }
    } catch (err) {
      alert('Error al guardar cotización: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePdf = async () => {
    if (!id) {
      alert('Primero debe guardar la cotización antes de generar el PDF');
      return;
    }

    setGeneratingPdf(true);
    try {
      const response = await axios.post(`/generar-pdf-cotizacion/${id}`, {}, {
        responseType: 'blob'
      });

      // Crear un link para descargar el PDF
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `cotizacion-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      alert('PDF generado exitosamente');
    } catch (err) {
      console.error('Error generando PDF:', err);
      alert('Error al generar PDF: ' + (err.response?.data?.message || err.message));
    } finally {
      setGeneratingPdf(false);
    }
  };

  if (loading && id) {
    return (
      <>
        <Navbar />
        <Container>
          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography>Cargando...</Typography>
          </Box>
        </Container>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, mb: 4 }}>
          {/* Título */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <RequestQuoteIcon sx={{ fontSize: 40, color: '#1976d2', mr: 2 }} />
            <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2' }}>
              {id ? 'Editar Cotización' : 'Nueva Cotización'}
            </Typography>
          </Box>

          {/* Información */}
          <Paper sx={{ p: 3, mb: 3, backgroundColor: '#f5f9ff', borderLeft: '4px solid #1976d2' }}>
            <Typography variant="body2" color="textSecondary">
              Complete la información de los productos o servicios que desea cotizar.
              Esta solicitud será enviada a los proveedores en formato PDF.
            </Typography>
          </Paper>

          {/* Tabla de Items */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976d2' }}>
                Productos y Servicios
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={addItem}
                size="small"
                sx={{ backgroundColor: '#4caf50', '&:hover': { backgroundColor: '#45a049' } }}
              >
                Agregar Fila
              </Button>
            </Box>

            <Divider sx={{ mb: 2 }} />

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                    <TableCell sx={{ fontWeight: 'bold', width: '5%' }}>#</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', width: '35%' }}>Producto / Servicio *</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', width: '15%' }}>Cantidad *</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', width: '35%' }}>Uso *</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', width: '10%', textAlign: 'center' }}>Acciones</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {items.map((item, index) => (
                    <TableRow 
                      key={index}
                      sx={{ 
                        '&:hover': { backgroundColor: '#f9f9f9' },
                        '& td': { borderBottom: '1px solid #e0e0e0' }
                      }}
                    >
                      <TableCell sx={{ color: '#1976d2', fontWeight: 'bold' }}>
                        {index + 1}
                      </TableCell>
                      <TableCell>
                        <TextField
                          value={item.producto_servicio}
                          onChange={(e) => updateItem(index, 'producto_servicio', e.target.value)}
                          placeholder="Ej: Papel higiénico jumbo"
                          fullWidth
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          value={item.cantidad}
                          onChange={(e) => updateItem(index, 'cantidad', e.target.value)}
                          placeholder="Ej: 50 unidades"
                          fullWidth
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          value={item.uso}
                          onChange={(e) => updateItem(index, 'uso', e.target.value)}
                          placeholder="Ej: Baños administrativos"
                          fullWidth
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell sx={{ textAlign: 'center' }}>
                        <IconButton
                          onClick={() => removeItem(index)}
                          color="error"
                          size="small"
                          disabled={items.length === 1}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {items.length === 0 && (
              <Box sx={{ textAlign: 'center', py: 3 }}>
                <Typography color="textSecondary">
                  No hay items. Haga clic en "Agregar Fila" para comenzar.
                </Typography>
              </Box>
            )}
          </Paper>

          {/* Observaciones */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#1976d2' }}>
              Observaciones y Comentarios (Opcional)
            </Typography>
            <TextField
              label="Observaciones adicionales"
              value={form.observaciones}
              onChange={(e) => setForm({ ...form, observaciones: e.target.value })}
              fullWidth
              multiline
              rows={4}
              placeholder="Agregue cualquier información adicional relevante para los proveedores..."
            />
          </Paper>

          {/* Botones de Acción */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="outlined"
              onClick={() => navigate('/cotizaciones')}
              size="large"
              sx={{ px: 4 }}
            >
              Cancelar
            </Button>
            
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSave}
              disabled={loading}
              size="large"
              sx={{ px: 4 }}
            >
              {loading ? 'Guardando...' : (id ? 'Actualizar' : 'Guardar Cotización')}
            </Button>

            {id && (
              <Button
                variant="contained"
                startIcon={<PictureAsPdfIcon />}
                onClick={handleGeneratePdf}
                disabled={generatingPdf}
                size="large"
                sx={{ 
                  px: 4,
                  backgroundColor: '#e91e63',
                  '&:hover': { backgroundColor: '#c2185b' }
                }}
              >
                {generatingPdf ? 'Generando...' : 'Generar PDF'}
              </Button>
            )}
          </Box>
        </Box>
      </Container>
    </>
  );
};

export default CotizacionForm;

