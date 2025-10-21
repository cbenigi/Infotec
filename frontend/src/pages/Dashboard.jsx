import React, { useEffect, useState } from 'react';
import { Container, Typography, List, ListItem, ListItemText, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Dashboard = () => {
  const [visitas, setVisitas] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchVisitas = async () => {
      try {
        const res = await axios.get('http://localhost:5000/visitas');
        setVisitas(res.data);
      } catch (err) {
        console.error('Error fetching visitas:', err);
      }
    };
    fetchVisitas();
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="h4">Dashboard</Typography>
        <Button variant="outlined" onClick={handleLogout}>Logout</Button>
      </Box>
      <Button variant="contained" onClick={() => navigate('/visita')} sx={{ mt: 2 }}>Nueva Visita</Button>
      <List sx={{ mt: 2 }}>
        {visitas.map((v) => (
          <ListItem key={v.id} button onClick={() => navigate(`/visita/${v.id}`)}>
            <ListItemText primary={`Visita ${v.id} - ${v.cliente}`} secondary={`Fecha: ${v.fecha}`} />
          </ListItem>
        ))}
      </List>
    </Container>
  );
};

export default Dashboard;