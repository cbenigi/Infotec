import React, { useState } from 'react';
import { TextField, Button, Container, Typography, Box } from '@mui/material';
import axios from 'axios';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { Link } from '@mui/material';

const Register = () => {
  const [form, setForm] = useState({ nombre: '', email: '', password: '' });
  const navigate = useNavigate();

  const handleRegister = async () => {
    try {
      const response = await axios.post('http://localhost:5000/usuarios', { ...form, rol: 'user' });
      
      // Guardar nombre del usuario
      localStorage.setItem('userName', form.nombre);
      
      // Verificar si el usuario tiene empresa registrada
      const empresaRes = await axios.get('http://localhost:5000/empresa');
      
      if (empresaRes.data.exists) {
        // Ya tiene empresa, ir al dashboard
        alert('Registro exitoso. Bienvenido de nuevo!');
        navigate('/dashboard');
      } else {
        // No tiene empresa, debe registrarla primero
        alert('Registro exitoso! Ahora registra tu empresa para empezar a crear informes.');
        navigate('/empresa');
      }
    } catch (err) {
      alert('Error al registrar usuario');
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography component="h1" variant="h5">Registro</Typography>
        <TextField label="Nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} fullWidth margin="normal" />
        <TextField label="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} fullWidth margin="normal" />
        <TextField label="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} fullWidth margin="normal" />
        <Button variant="contained" onClick={handleRegister} fullWidth sx={{ mt: 3 }}>Registrar</Button>
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Link component={RouterLink} to="/login" variant="body2">
            ¿Ya tienes cuenta? Inicia sesión
          </Link>
        </Box>
      </Box>
    </Container>
  );
};

export default Register;