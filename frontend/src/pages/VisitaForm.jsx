import React, { useState, useEffect } from 'react';
import { TextField, Button, Container, Typography, Box, Select, MenuItem, FormControl, InputLabel, IconButton, InputAdornment } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import ImageUpload from '../components/ImageUpload';
import Navbar from '../components/Navbar';

const VisitaForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    cliente_id: '', supervisor_id: '', tecnico_id: '', fecha: '', goal: '', calificacion: '',
    notas: '', seguridad_obs: '', productividad_obs: '', conclusiones_obs: '', zonas: []
  });
  const [clientes, setClientes] = useState([]);
  const [usuarios, setUsuarios] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [clientesRes, usuariosRes] = await Promise.all([
          axios.get('http://localhost:5000/clientes'),
          axios.get('http://localhost:5000/usuarios')
        ]);
        setClientes(clientesRes.data);
        setUsuarios(usuariosRes.data);
      } catch (err) {
        console.error('Error fetching data:', err);
      }
    };
    fetchData();
    if (id) {
      // Cargar visita existente
      axios.get(`http://localhost:5000/visitas/${id}`).then((res) => setForm(res.data));
      axios.get(`http://localhost:5000/zonas/${id}`).then((res) => setForm((prev) => ({ ...prev, zonas: res.data })));
    }
  }, [id]);

  const handleSubmit = async () => {
    const data = { ...form, tipo_codigo: clientes.find(c => c.id === form.cliente_id)?.tipo_codigo };
    const visitaRes = id ? await axios.put(`http://localhost:5000/visitas/${id}`, data) : await axios.post('http://localhost:5000/visitas', data);
    const visitaId = id || visitaRes.data.id;
    await Promise.all(form.zonas.map(z => axios.post('http://localhost:5000/zonas', { ...z, visita_id: visitaId })));
    navigate('/dashboard');
  };

  const addZona = () => setForm({ ...form, zonas: [...form.zonas, { nombre: '', observaciones: '', actividades: '', calificacion: 'Bueno', foto_url: '' }] });
  const removeZona = (index) => setForm({ ...form, zonas: form.zonas.filter((_, i) => i !== index) });
  const updateZona = (index, field, value) => {
    const newZonas = [...form.zonas];
    newZonas[index][field] = value;
    setForm({ ...form, zonas: newZonas });
  };

  const hasPhoto = form.zonas.some(z => z.foto_url);

  return (
    <>
      <Navbar />
      <Container maxWidth="md" sx={{ mt: 3 }}>
        <Typography variant="h4">{id ? 'Editar Visita' : 'Nueva Visita'}</Typography>
      <Box component="form" sx={{ mt: 2 }}>
        <FormControl fullWidth margin="normal">
          <InputLabel>Cliente</InputLabel>
          <Select
            value={form.cliente_id}
            onChange={(e) => setForm({ ...form, cliente_id: e.target.value })}
            endAdornment={
              clientes.length === 0 ? (
                <InputAdornment position="end">
                  <IconButton onClick={() => navigate('/clientes/new')} size="small">
                    <AddIcon />
                  </IconButton>
                </InputAdornment>
              ) : null
            }
          >
            {clientes.map(c => <MenuItem key={c.id} value={c.id}>{c.nombre}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Supervisor</InputLabel>
          <Select
            value={form.supervisor_id}
            onChange={(e) => setForm({ ...form, supervisor_id: e.target.value })}
            endAdornment={
              usuarios.length === 0 ? (
                <InputAdornment position="end">
                  <IconButton onClick={() => navigate('/usuarios/new')} size="small">
                    <AddIcon />
                  </IconButton>
                </InputAdornment>
              ) : null
            }
          >
            {usuarios.map(u => <MenuItem key={u.id} value={u.id}>{u.nombre}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Técnico</InputLabel>
          <Select value={form.tecnico_id} onChange={(e) => setForm({ ...form, tecnico_id: e.target.value })}>
            {usuarios.map(u => <MenuItem key={u.id} value={u.id}>{u.nombre}</MenuItem>)}
          </Select>
        </FormControl>
        <TextField label="Fecha" type="date" value={form.fecha} onChange={(e) => setForm({ ...form, fecha: e.target.value })} fullWidth margin="normal" InputLabelProps={{ shrink: true }} />
        <TextField label="Goal" type="number" value={form.goal} onChange={(e) => setForm({ ...form, goal: e.target.value })} fullWidth margin="normal" />
        <TextField label="Calificación" type="number" value={form.calificacion} onChange={(e) => setForm({ ...form, calificacion: e.target.value })} fullWidth margin="normal" />
        <TextField label="Notas" value={form.notas} onChange={(e) => setForm({ ...form, notas: e.target.value })} fullWidth margin="normal" multiline />
        <Typography variant="h6">Zonas</Typography>
        {form.zonas.map((z, i) => (
          <Box key={i} sx={{ border: '1px solid #ccc', p: 2, mb: 2 }}>
            <TextField label="Nombre" value={z.nombre} onChange={(e) => updateZona(i, 'nombre', e.target.value)} fullWidth margin="normal" />
            <TextField label="Observaciones" value={z.observaciones} onChange={(e) => updateZona(i, 'observaciones', e.target.value)} fullWidth margin="normal" multiline />
            <TextField label="Actividades" value={z.actividades} onChange={(e) => updateZona(i, 'actividades', e.target.value)} fullWidth margin="normal" multiline />
            <FormControl fullWidth margin="normal">
              <InputLabel>Calificación</InputLabel>
              <Select value={z.calificacion} onChange={(e) => updateZona(i, 'calificacion', e.target.value)}>
                <MenuItem value="Bueno">Bueno</MenuItem>
                <MenuItem value="Regular">Regular</MenuItem>
                <MenuItem value="Malo">Malo</MenuItem>
              </Select>
            </FormControl>
            <ImageUpload
              onUpload={(url) => updateZona(i, 'foto_url', url)}
              images={z.foto_url ? [z.foto_url] : []}
              onRemove={() => updateZona(i, 'foto_url', '')}
            />
            <IconButton onClick={() => removeZona(i)}><span style={{ fontSize: '18px', color: 'red' }}>×</span></IconButton>
          </Box>
        ))}
        <Button onClick={addZona}>Agregar Zona</Button>
        <TextField label="Seguridad Observaciones" value={form.seguridad_obs} onChange={(e) => setForm({ ...form, seguridad_obs: e.target.value })} fullWidth margin="normal" multiline />
        <TextField label="Productividad Observaciones" value={form.productividad_obs} onChange={(e) => setForm({ ...form, productividad_obs: e.target.value })} fullWidth margin="normal" multiline />
        <TextField label="Conclusiones Observaciones" value={form.conclusiones_obs} onChange={(e) => setForm({ ...form, conclusiones_obs: e.target.value })} fullWidth margin="normal" multiline />
        <Button variant="contained" onClick={handleSubmit} fullWidth sx={{ mt: 2 }}>Guardar</Button>
        {hasPhoto && <Button variant="outlined" onClick={() => axios.post(`http://localhost:5000/generar-pdf/${id || 'new'}`, { enviar_email: false })} sx={{ mt: 1 }}>Generar PDF</Button>}
      </Box>
    </Container>
    </>
  );
};

export default VisitaForm;