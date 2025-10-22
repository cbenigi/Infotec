import React, { useState } from 'react';
import { TextField, Button, Container, Typography, Box, Link } from '@mui/material';
import axios from 'axios';
import { useNavigate, Link as RouterLink } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const res = await axios.post('http://localhost:5000/login', { email, password });
      localStorage.setItem('token', 'basic'); // Simular token
      localStorage.setItem('rol', res.data.rol);
      
      // Verificar si el usuario tiene empresa registrada
      const empresaRes = await axios.get('http://localhost:5000/empresa');
      
      if (empresaRes.data.exists) {
        navigate('/dashboard');
      } else {
        alert('Por favor registra tu empresa para continuar');
        navigate('/empresa');
      }
    } catch (err) {
      alert('Credenciales inválidas');
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography component="h1" variant="h5">Login</Typography>
        <TextField label="Email" value={email} onChange={(e) => setEmail(e.target.value)} fullWidth margin="normal" />
        <TextField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} fullWidth margin="normal" />
        <Button variant="contained" onClick={handleLogin} fullWidth sx={{ mt: 3 }}>Login</Button>
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Link component={RouterLink} to="/register" variant="body2">
            ¿No tienes cuenta? Regístrate
          </Link>
        </Box>
      </Box>
    </Container>
  );
};

export default Login;