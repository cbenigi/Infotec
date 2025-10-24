import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Button, 
  TextField, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Divider
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import axios from '../api/axiosConfig';
import Navbar from '../components/Navbar';
import ImageUpload from '../components/ImageUpload';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import AssignmentIcon from '@mui/icons-material/Assignment';

const VisitaForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [clientes, setClientes] = useState([]);
  const [supervisores, setSupervisores] = useState([]);
  
  const [form, setForm] = useState({
    cliente_id: '',
    supervisor_id: '',
    fecha: new Date().toISOString().split('T')[0],
    conclusiones: ''
  });

  const [zonas, setZonas] = useState({
    aseo: [],
    seguridad: [],
    colaborador: []
  });

  useEffect(() => {
    loadClientes();
    loadSupervisores();
    if (id) {
      loadVisita();
    }
  }, [id]);

  const loadClientes = async () => {
    try {
      const response = await axios.get('/clientes');
      setClientes(response.data);
    } catch (err) {
      console.error('Error cargando clientes:', err);
    }
  };

  const loadSupervisores = async () => {
    try {
      const response = await axios.get('/usuarios');
      const supervisoresData = response.data.filter(user => user.rol === 'supervisor');
      setSupervisores(supervisoresData);
    } catch (err) {
      console.error('Error cargando supervisores:', err);
    }
  };

  const loadVisita = async () => {
    try {
      const response = await axios.get(`/visita/${id}`);
      const visita = response.data;
      setForm({
        cliente_id: visita.cliente_id,
        supervisor_id: visita.supervisor_id,
        fecha: visita.fecha,
        conclusiones: visita.conclusiones || ''
      });
      // Cargar zonas por sección
      const zonasData = { aseo: [], seguridad: [], colaborador: [] };
      visita.zonas.forEach(zona => {
        zonasData[zona.seccion.toLowerCase().replace(' ', '_')].push(zona);
      });
      setZonas(zonasData);
    } catch (err) {
      console.error('Error cargando visita:', err);
    }
  };

  const addZona = (seccion) => {
    const nuevaZona = {
      concepto_actividad: '',
      calificacion: 'Buena',
      observaciones: '',
      foto_url: ''
    };

    setZonas(prev => ({
      ...prev,
      [seccion]: [...prev[seccion], nuevaZona]
    }));
  };

  const updateZona = (seccion, index, field, value) => {
    setZonas(prev => ({
      ...prev,
      [seccion]: prev[seccion].map((zona, i) => 
        i === index ? { ...zona, [field]: value } : zona
      )
    }));
  };

  const removeZona = (seccion, index) => {
    setZonas(prev => ({
      ...prev,
      [seccion]: prev[seccion].filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async () => {
    if (!form.cliente_id || !form.supervisor_id) {
      alert('Por favor selecciona cliente y supervisor');
      return;
    }

    setLoading(true);
    try {
      const visitaData = {
        ...form,
        zonas: [
          ...zonas.aseo.map(z => ({ ...z, seccion: 'Aseo y Limpieza' })),
          ...zonas.seguridad.map(z => ({ ...z, seccion: 'Seguridad y Salud' })),
          ...zonas.colaborador.map(z => ({ ...z, seccion: 'Colaborador' }))
        ]
      };

      if (id) {
        await axios.put(`/visita/${id}`, visitaData);
        alert('Visita actualizada exitosamente');
      } else {
        await axios.post('/visita', visitaData);
        alert('Visita creada exitosamente');
      }
      navigate('/dashboard');
    } catch (err) {
      alert('Error al guardar visita: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  const renderSeccion = (titulo, seccion, zonasData, tieneFoto = true) => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <AssignmentIcon sx={{ mr: 1, color: '#1976d2' }} />
          <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976d2' }}>
            {titulo}
          </Typography>
          <Button
            startIcon={<AddIcon />}
            onClick={() => addZona(seccion)}
            size="small"
            sx={{ ml: 'auto' }}
          >
            Agregar Actividad
          </Button>
        </Box>

        {zonasData.map((zona, index) => (
          <Paper key={index} sx={{ p: 2, mb: 2, backgroundColor: '#f8f9fa' }}>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  label="Concepto Actividad"
                  value={zona.concepto_actividad}
                  onChange={(e) => updateZona(seccion, index, 'concepto_actividad', e.target.value)}
                  fullWidth
                  size="small"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <FormControl fullWidth size="small">
                  <InputLabel>Calificación</InputLabel>
                  <Select
                    value={zona.calificacion}
                    onChange={(e) => updateZona(seccion, index, 'calificacion', e.target.value)}
                  >
                    <MenuItem value="Buena">Buena</MenuItem>
                    <MenuItem value="Media">Media</MenuItem>
                    <MenuItem value="Mala">Mala</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <IconButton
                    onClick={() => removeZona(seccion, index)}
                    color="error"
                    size="small"
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  label="Observaciones"
                  value={zona.observaciones}
                  onChange={(e) => updateZona(seccion, index, 'observaciones', e.target.value)}
                  fullWidth
                  multiline
                  rows={2}
                  size="small"
                />
              </Grid>
              {tieneFoto && (
                <Grid size={{ xs: 12 }}>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                    Evidencia (Foto)
                  </Typography>
                  <ImageUpload
                    onUpload={(url) => updateZona(seccion, index, 'foto_url', url)}
                    images={zona.foto_url ? [zona.foto_url] : []}
                    onRemove={() => updateZona(seccion, index, 'foto_url', '')}
                  />
                </Grid>
              )}
            </Grid>
          </Paper>
        ))}
      </CardContent>
    </Card>
  );

  return (
    <>
      <Navbar />
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 3 }}>
            {id ? 'Editar Visita' : 'Nueva Visita Técnica'}
          </Typography>

          {/* Información básica */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Información de la Visita
            </Typography>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, md: 4 }}>
                <FormControl fullWidth>
                  <InputLabel>Cliente *</InputLabel>
          <Select
            value={form.cliente_id}
            onChange={(e) => setForm({ ...form, cliente_id: e.target.value })}
                  >
                    {clientes.map(cliente => (
                      <MenuItem key={cliente.id} value={cliente.id}>
                        {cliente.nombre}
                      </MenuItem>
                    ))}
          </Select>
        </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <FormControl fullWidth>
                  <InputLabel>Supervisor *</InputLabel>
          <Select
            value={form.supervisor_id}
            onChange={(e) => setForm({ ...form, supervisor_id: e.target.value })}
                  >
                    {supervisores.map(supervisor => (
                      <MenuItem key={supervisor.id} value={supervisor.id}>
                        {supervisor.nombre}
                      </MenuItem>
                    ))}
          </Select>
        </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <TextField
                  label="Fecha"
                  type="date"
                  value={form.fecha}
                  onChange={(e) => setForm({ ...form, fecha: e.target.value })}
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
          </Paper>

          {/* Secciones */}
          {renderSeccion('Aseo y Limpieza', 'aseo', zonas.aseo, true)}
          {renderSeccion('Seguridad y Salud en el Trabajo', 'seguridad', zonas.seguridad, true)}
          {renderSeccion('Colaborador', 'colaborador', zonas.colaborador, false)}

          {/* Conclusiones */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Conclusiones
            </Typography>
            <TextField
              label="Conclusiones de la visita"
              value={form.conclusiones}
              onChange={(e) => setForm({ ...form, conclusiones: e.target.value })}
              fullWidth
              multiline
              rows={4}
            />
          </Paper>

          {/* Botones */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="outlined"
              onClick={() => navigate('/dashboard')}
              size="large"
              sx={{ px: 4 }}
            >
              Cancelar
            </Button>
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={loading}
              size="large"
              sx={{ px: 4 }}
            >
              {loading ? 'Guardando...' : (id ? 'Actualizar Visita' : 'Crear Visita')}
            </Button>
          </Box>
      </Box>
    </Container>
    </>
  );
};

export default VisitaForm;