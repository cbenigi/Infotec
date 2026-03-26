import React, { useEffect, useState, useCallback, useMemo } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import axios from '../api/axiosConfig';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';

const ESTADOS = [
  { value: 'borrador', label: 'Borrador' },
  { value: 'emitida', label: 'Emitida' },
  { value: 'recibida', label: 'Recibida' },
  { value: 'cerrada', label: 'Cerrada' }
];

const defaultItem = { descripcion: '', cantidad: '', unidad: '', precio_unitario: '', comentarios: '' };
const IVA_RATE = 0.19;

const OrdenCompraForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [clientes, setClientes] = useState([]);
  const [empresa, setEmpresa] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generatingPdf, setGeneratingPdf] = useState(false);
  const [proveedores, setProveedores] = useState([]);
  const [form, setForm] = useState({
    numero: '',
    fecha_entrega: '',
    comprador_tipo: 'cliente',
    comprador_id: '',
    proveedor_nombre: '',
    proveedor_nit: '',
    proveedor_direccion: '',
    proveedor_tipo_insumos: '',
    proveedor_id: '',
    condiciones_pago: '',
    notas: '',
    estado: 'borrador',
    subtotal: '',
    total: ''
  });
  const [items, setItems] = useState([defaultItem]);

  const loadClientes = useCallback(async () => {
    try {
      const { data } = await axios.get('/clientes');
      setClientes(data);
    } catch (error) {
      console.error('Error cargando clientes:', error);
    }
  }, []);

  const loadEmpresa = useCallback(async () => {
    try {
      const { data } = await axios.get('/empresa');
      if (data.exists) {
        setEmpresa(data);
        if (!form.comprador_id && form.comprador_tipo === 'empresa') {
          setForm((prev) => ({ ...prev, comprador_id: data.id }));
        }
      }
    } catch (error) {
      console.error('Error cargando empresa:', error);
    }
  }, [form.comprador_id, form.comprador_tipo]);

  const loadProveedores = useCallback(async () => {
    try {
      const { data } = await axios.get('/proveedores');
      setProveedores(data);
    } catch (error) {
      console.error('Error cargando proveedores:', error);
    }
  }, []);

  const loadOrden = useCallback(async () => {
    try {
      setLoading(true);
      const { data } = await axios.get(`/orden-compra/${id}`);
      setForm({
        numero: data.numero,
        fecha_entrega: data.fecha_entrega || '',
        comprador_tipo: data.comprador_tipo,
        comprador_id: data.comprador_id,
        proveedor_nombre: data.proveedor_nombre,
        proveedor_nit: data.proveedor_nit || '',
         proveedor_direccion: data.proveedor_direccion || '',
         proveedor_tipo_insumos: data.proveedor_tipo_insumos || '',
         proveedor_id: data.proveedor_id || '',
        condiciones_pago: data.condiciones_pago || '',
        notas: data.notas || '',
        estado: data.estado,
        subtotal: data.subtotal ? String(data.subtotal) : '',
        total: data.total ? String(data.total) : ''
      });
      if (data.items?.length) {
        setItems(
          data.items
            .sort((a, b) => (a.posicion || 0) - (b.posicion || 0))
            .map((item) => ({
              descripcion: item.descripcion,
              cantidad: item.cantidad,
              unidad: item.unidad,
              precio_unitario: item.precio_unitario ?? '',
              comentarios: item.comentarios ?? ''
            }))
        );
      }
    } catch (error) {
      console.error('Error cargando orden:', error);
      alert('Error al cargar la orden: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  }, [id]);

  const compradorOptions = useMemo(() => (
    form.comprador_tipo === 'cliente' ? clientes : empresa ? [empresa] : []
  ), [form.comprador_tipo, clientes, empresa]);

  useEffect(() => {
    loadClientes();
    loadEmpresa();
    loadProveedores();
  }, [loadClientes, loadEmpresa, loadProveedores]);

  useEffect(() => {
    if (id) {
      loadOrden();
    }
  }, [id, loadOrden]);

  useEffect(() => {
    if (!form.comprador_id && compradorOptions.length > 0) {
      setForm((prev) => ({ ...prev, comprador_id: compradorOptions[0].id }));
    }
  }, [compradorOptions, form.comprador_id]);

  const handleAddItem = () => setItems((prev) => [...prev, defaultItem]);

  const handleRemoveItem = (index) => {
    if (items.length === 1) {
      alert('La orden debe tener al menos un item');
      return;
    }
    setItems((prev) => prev.filter((_, i) => i !== index));
  };

  const updateItem = (index, field, value) => {
    setItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, [field]: value } : item))
    );
  };

  const parseNumber = (value) => {
    if (value === null || value === undefined || value === '') return null;
    const parsed = parseFloat(String(value).replace(',', '.'));
    return Number.isNaN(parsed) ? null : parsed;
  };

  const calculateItemsSubtotal = useCallback(() => {
    let subtotalValue = 0;
    let hasValues = false;
    items.forEach((item) => {
      const cantidad = parseNumber(item.cantidad);
      const precio = parseNumber(item.precio_unitario);
      if (cantidad !== null && precio !== null) {
        subtotalValue += cantidad * precio;
        hasValues = true;
      }
    });
    return hasValues ? subtotalValue : null;
  }, [items]);

  useEffect(() => {
    const subtotalFromItems = calculateItemsSubtotal();
    if (subtotalFromItems !== null) {
      const iva = subtotalFromItems * IVA_RATE;
      const total = subtotalFromItems + iva;
      setForm((prev) => ({
        ...prev,
        subtotal: subtotalFromItems.toFixed(2),
        total: total.toFixed(2)
      }));
    } else {
      setForm((prev) => ({ ...prev, subtotal: '', total: '' }));
    }
  }, [items, calculateItemsSubtotal]);

  const getSubtotal = (item) => {
    const cantidad = parseNumber(item.cantidad);
    const precio = parseNumber(item.precio_unitario);
    if (cantidad === null || precio === null) return 0;
    return cantidad * precio;
  };
  const getIva = (item) => {
    const subtotal = getSubtotal(item);
    return subtotal * IVA_RATE;
  };

  const totalEstimado = items.reduce((acc, item) => acc + getSubtotal(item), 0);

  const validateForm = () => {
    if (!form.comprador_id) {
      alert('Selecciona un comprador');
      return false;
    }
    if (!form.proveedor_nombre.trim()) {
      alert('El nombre del proveedor es requerido');
      return false;
    }
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (!item.descripcion.trim() || !item.cantidad.trim() || !item.unidad.trim()) {
        alert(`Completa todos los campos del item ${i + 1}`);
        return false;
      }
    }
    return true;
  };

  const handleProveedorSelect = (value) => {
    const proveedorId = value ? Number(value) : '';
    const proveedor = proveedores.find((prov) => prov.id === proveedorId);
    setForm((prev) => ({
      ...prev,
      proveedor_id: proveedorId,
      proveedor_nombre: proveedor ? proveedor.nombre_comercial : prev.proveedor_nombre,
      proveedor_nit: proveedor ? proveedor.nit : prev.proveedor_nit,
      proveedor_direccion: proveedor?.direccion || '',
      proveedor_tipo_insumos: proveedor?.tipo_insumos || ''
    }));
  };

  const handleSave = async () => {
    if (!validateForm()) return;
    setLoading(true);
    try {
      const payload = {
        ...form,
        proveedor_id: form.proveedor_id || null,
        items: items.map((item) => ({
          ...item,
          precio_unitario: parseNumber(item.precio_unitario)
        }))
      };
      if (id) {
        await axios.put(`/orden-compra/${id}`, payload);
        alert('Orden actualizada exitosamente');
      } else {
        const { data } = await axios.post('/orden-compra', payload);
        alert('Orden creada exitosamente');
        navigate(`/orden-compra/${data.id}`);
      }
    } catch (error) {
      console.error('Error guardando orden:', error);
      alert('Error al guardar la orden: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePdf = async () => {
    if (!id) return;
    setGeneratingPdf(true);
    try {
      const response = await axios.post(`/generar-pdf-orden/${id}`, {}, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `orden-compra-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('Error al generar PDF: ' + (error.response?.data?.message || error.message));
    } finally {
      setGeneratingPdf(false);
    }
  };

  if (loading && id && !form.numero) {
    return (
      <>
        <Navbar />
        <Container>
          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography>Cargando orden...</Typography>
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
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <ShoppingCartIcon sx={{ fontSize: 40, color: '#1976d2', mr: 2 }} />
            <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2' }}>
              {id ? `Editar Orden ${form.numero}` : 'Nueva Orden de Compra'}
            </Typography>
          </Box>

          <Paper sx={{ p: 3, mb: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Número"
                  value={form.numero || 'Se generará automáticamente'}
                  fullWidth
                  InputProps={{ readOnly: true }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Fecha estimada de entrega"
                  type="date"
                  value={form.fecha_entrega}
                  onChange={(e) => setForm({ ...form, fecha_entrega: e.target.value })}
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Estado</InputLabel>
                  <Select
                    label="Estado"
                    value={form.estado}
                    onChange={(e) => setForm({ ...form, estado: e.target.value })}
                  >
                    {ESTADOS.map((estado) => (
                      <MenuItem key={estado.value} value={estado.value}>
                        {estado.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Comprador</InputLabel>
                  <Select
                    label="Comprador"
                    value={form.comprador_tipo}
                    onChange={(e) => setForm({ ...form, comprador_tipo: e.target.value, comprador_id: '' })}
                  >
                    <MenuItem value="cliente">Cliente</MenuItem>
                    <MenuItem value="empresa" disabled={!empresa}>
                      Empresa
                    </MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={8}>
                <FormControl fullWidth>
                  <InputLabel>{form.comprador_tipo === 'cliente' ? 'Selecciona cliente' : 'Selecciona empresa'}</InputLabel>
                  <Select
                    label={form.comprador_tipo === 'cliente' ? 'Selecciona cliente' : 'Selecciona empresa'}
                    value={form.comprador_id}
                    onChange={(e) => setForm({ ...form, comprador_id: e.target.value })}
                  >
                    {compradorOptions.map((option) => (
                      <MenuItem key={option.id} value={option.id}>
                        {option.nombre}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Proveedor *"
                  value={form.proveedor_nombre}
                  onChange={(e) => setForm({ ...form, proveedor_nombre: e.target.value })}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="NIT proveedor"
                  value={form.proveedor_nit}
                  onChange={(e) => setForm({ ...form, proveedor_nit: e.target.value })}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Selecciona proveedor</InputLabel>
                  <Select
                    label="Selecciona proveedor"
                    value={form.proveedor_id || ''}
                    onChange={(e) => handleProveedorSelect(e.target.value)}
                  >
                    <MenuItem value="">Manual</MenuItem>
                    {proveedores.map((prov) => (
                      <MenuItem key={prov.id} value={prov.id}>
                        {prov.nombre_comercial}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <Button variant="outlined" onClick={() => navigate('/proveedores/nuevo')}>
                  Gestionar proveedores
                </Button>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Dirección proveedor"
                  value={form.proveedor_direccion}
                  onChange={(e) => setForm({ ...form, proveedor_direccion: e.target.value })}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Tipo de insumos"
                  value={form.proveedor_tipo_insumos}
                  onChange={(e) => setForm({ ...form, proveedor_tipo_insumos: e.target.value })}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Condiciones de pago"
                  value={form.condiciones_pago}
                  onChange={(e) => setForm({ ...form, condiciones_pago: e.target.value })}
                  fullWidth
                  placeholder="Ej: 30 días, transferencia, anticipo, etc."
                />
              </Grid>
            </Grid>
          </Paper>

          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976d2' }}>
                Detalle de la orden
              </Typography>
              <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddItem} size="small">
                Agregar Item
              </Button>
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>#</TableCell>
                    <TableCell>Descripción *</TableCell>
                    <TableCell>Cantidad *</TableCell>
                    <TableCell>Unidad *</TableCell>
                    <TableCell>Precio Unitario</TableCell>
                    <TableCell>IVA (19 %)</TableCell>
                    <TableCell>Subtotal</TableCell>
                    <TableCell>Acciones</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {items.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell>{index + 1}</TableCell>
                      <TableCell>
                        <TextField
                          value={item.descripcion}
                          onChange={(e) => updateItem(index, 'descripcion', e.target.value)}
                          fullWidth
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          value={item.cantidad}
                          onChange={(e) => updateItem(index, 'cantidad', e.target.value)}
                          fullWidth
                          size="small"
                          placeholder="Ej: 10"
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          value={item.unidad}
                          onChange={(e) => updateItem(index, 'unidad', e.target.value)}
                          fullWidth
                          size="small"
                          placeholder="Caja, Unidad, etc."
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          value={item.precio_unitario}
                          onChange={(e) => updateItem(index, 'precio_unitario', e.target.value)}
                          fullWidth
                          size="small"
                          placeholder="Ej: 25000"
                        />
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>
                        {getSubtotal(item) > 0 ? `$ ${getIva(item).toLocaleString('es-CO')}` : '—'}
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>
                        {getSubtotal(item) > 0 ? `$ ${getSubtotal(item).toLocaleString('es-CO')}` : '—'}
                      </TableCell>
                      <TableCell>
                        <IconButton color="error" onClick={() => handleRemoveItem(index)} disabled={items.length === 1} size="small">
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <Box sx={{ textAlign: 'right', mt: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                Total estimado: {totalEstimado > 0 ? `$ ${totalEstimado.toLocaleString('es-CO')}` : 'Por definir'}
              </Typography>
            </Box>
          </Paper>

          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Notas internas
            </Typography>
            <TextField
              label="Notas u observaciones"
              value={form.notas}
              onChange={(e) => setForm({ ...form, notas: e.target.value })}
              fullWidth
              multiline
              rows={4}
              placeholder="Instrucciones especiales, entregas parciales, contactos de proveedor, etc."
            />
          </Paper>

          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Button variant="outlined" onClick={() => navigate('/ordenes-compra')}>
              Cancelar
            </Button>
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSave}
              disabled={loading}
              sx={{ px: 4 }}
            >
              {loading ? 'Guardando...' : id ? 'Actualizar Orden' : 'Guardar Orden'}
            </Button>
            {id && (
              <Button
                variant="contained"
                color="secondary"
                startIcon={<PictureAsPdfIcon />}
                onClick={handleGeneratePdf}
                disabled={generatingPdf}
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

export default OrdenCompraForm;

