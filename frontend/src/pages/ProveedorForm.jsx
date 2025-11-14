import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import Navbar from '../components/Navbar';
import axios from '../api/axiosConfig';

const initialForm = {
  nombre_comercial: '',
  nit: '',
  direccion: '',
  tipo_insumos: ''
};

const ProveedorForm = () => {
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(false);
  const [proveedores, setProveedores] = useState([]);

  const loadProveedores = async () => {
    try {
      const { data } = await axios.get('/proveedores');
      setProveedores(data);
    } catch (error) {
      console.error('Error cargando proveedores:', error);
    }
  };

  useEffect(() => {
    loadProveedores();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.nombre_comercial.trim() || !form.nit.trim()) {
      alert('Nombre comercial y NIT son obligatorios');
      return;
    }
    setLoading(true);
    try {
      await axios.post('/proveedores', form);
      alert('Proveedor registrado exitosamente');
      setForm(initialForm);
      loadProveedores();
    } catch (error) {
      alert('Error al registrar proveedor: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este proveedor?')) return;
    try {
      await axios.delete(`/proveedores/${id}`);
      loadProveedores();
    } catch (error) {
      alert('Error al eliminar proveedor: ' + (error.response?.data?.message || error.message));
    }
  };

  return (
    <>
      <Navbar />
      <Container maxWidth="md">
        <Box sx={{ mt: 4, mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 3 }}>
            Registrar Proveedor
          </Typography>

          <Paper sx={{ p: 3, mb: 4 }} component="form" onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Nombre Comercial *"
                  value={form.nombre_comercial}
                  onChange={(e) => setForm({ ...form, nombre_comercial: e.target.value })}
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="NIT *"
                  value={form.nit}
                  onChange={(e) => setForm({ ...form, nit: e.target.value })}
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Dirección"
                  value={form.direccion}
                  onChange={(e) => setForm({ ...form, direccion: e.target.value })}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Tipo de insumos que ofrece"
                  value={form.tipo_insumos}
                  onChange={(e) => setForm({ ...form, tipo_insumos: e.target.value })}
                  fullWidth
                  multiline
                  rows={2}
                />
              </Grid>
            </Grid>
            <Box sx={{ textAlign: 'right', mt: 3 }}>
              <Button type="submit" variant="contained" disabled={loading}>
                {loading ? 'Guardando...' : 'Guardar proveedor'}
              </Button>
            </Box>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Proveedores registrados
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Nombre Comercial</TableCell>
                    <TableCell>NIT</TableCell>
                    <TableCell>Dirección</TableCell>
                    <TableCell>Tipo de Insumos</TableCell>
                    <TableCell align="right">Acciones</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {proveedores.map((prov) => (
                    <TableRow key={prov.id}>
                      <TableCell>{prov.nombre_comercial}</TableCell>
                      <TableCell>{prov.nit}</TableCell>
                      <TableCell>{prov.direccion || '—'}</TableCell>
                      <TableCell>{prov.tipo_insumos || '—'}</TableCell>
                      <TableCell align="right">
                        <IconButton color="error" size="small" onClick={() => handleDelete(prov.id)}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                  {proveedores.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        Aún no hay proveedores registrados.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Box>
      </Container>
    </>
  );
};

export default ProveedorForm;

