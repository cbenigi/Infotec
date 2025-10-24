import React, { useEffect, useState } from 'react';
import { Container, Typography, List, ListItem, ListItemText, Button, Box, Grid, Paper, Card, CardContent, CardActions, IconButton, ListItemSecondaryAction } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from '../api/axiosConfig';
import Navbar from '../components/Navbar';
import AddIcon from '@mui/icons-material/Add';
import BusinessIcon from '@mui/icons-material/Business';
import SupervisorAccountIcon from '@mui/icons-material/SupervisorAccount';
import AssignmentIcon from '@mui/icons-material/Assignment';
import { Download, Visibility, Delete } from '@mui/icons-material';

const Dashboard = () => {
  const [visitas, setVisitas] = useState([]);
  const navigate = useNavigate();

  const handleDownloadPDF = async (visitaId) => {
    try {
      const response = await axios.post(`/generar-pdf/${visitaId}`, {}, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `visita-${visitaId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error al descargar PDF:', error);
      alert('Error al descargar el PDF');
    }
  };

  const handleDeleteVisita = async (visitaId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta visita? Esta acción no se puede deshacer.')) {
      try {
        await axios.delete(`/visita/${visitaId}`);
        alert('Visita eliminada exitosamente');
        // Recargar la lista de visitas
        const res = await axios.get('/visitas');
        setVisitas(res.data);
      } catch (error) {
        console.error('Error al eliminar visita:', error);
        alert('Error al eliminar la visita');
      }
    }
  };

  useEffect(() => {
    const fetchVisitas = async () => {
      try {
        const res = await axios.get('/visitas');
        setVisitas(res.data);
      } catch (err) {
        console.error('Error fetching visitas:', err);
      }
    };
    fetchVisitas();
  }, []);

  return (
    <>
      <Navbar />
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 3 }}>
            Panel de Control
          </Typography>
          
          {/* Tarjetas de acciones rápidas */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ height: '100%', '&:hover': { boxShadow: 6 } }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <AssignmentIcon sx={{ fontSize: 40, color: '#1976d2', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Nueva Visita
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Crear un nuevo informe de visita técnica
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                  <Button 
                    variant="contained" 
                    onClick={() => navigate('/visita')}
                    startIcon={<AddIcon />}
                    fullWidth
                  >
                    Crear Visita
                  </Button>
                </CardActions>
              </Card>
            </Grid>

            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ height: '100%', '&:hover': { boxShadow: 6 } }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <BusinessIcon sx={{ fontSize: 40, color: '#1976d2', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Registrar Cliente
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Agregar un nuevo cliente al sistema
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                  <Button 
                    variant="contained" 
                    onClick={() => navigate('/clientes/new')}
                    startIcon={<AddIcon />}
                    fullWidth
                  >
                    Nuevo Cliente
                  </Button>
                </CardActions>
              </Card>
            </Grid>

            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ height: '100%', '&:hover': { boxShadow: 6 } }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <SupervisorAccountIcon sx={{ fontSize: 40, color: '#1976d2', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Registrar Supervisor
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Agregar supervisores y técnicos
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                  <Button 
                    variant="contained" 
                    onClick={() => navigate('/supervisores/new')}
                    startIcon={<AddIcon />}
                    fullWidth
                  >
                    Nuevo Supervisor
                  </Button>
                </CardActions>
              </Card>
            </Grid>

            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ height: '100%', '&:hover': { boxShadow: 6 } }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <BusinessIcon sx={{ fontSize: 40, color: '#1976d2', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Mi Empresa
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Configurar datos de la empresa
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                  <Button 
                    variant="outlined" 
                    onClick={() => navigate('/empresa')}
                    fullWidth
                  >
                    Configurar
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          </Grid>

          {/* Lista de visitas recientes */}
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
              Visitas Recientes
            </Typography>
            {visitas.length > 0 ? (
              <List>
        {visitas.map((v) => (
                  <ListItem 
                    key={v.id} 
                    sx={{ 
                      '&:hover': { backgroundColor: '#f5f5f5' },
                      borderRadius: 1,
                      mb: 1,
                      border: '1px solid #e0e0e0'
                    }}
                  >
                    <ListItemText 
                      primary={`Visita ${v.id} - ${v.cliente}`} 
                      secondary={`Fecha: ${v.fecha} | Supervisor: ${v.supervisor}`} 
                    />
                    <ListItemSecondaryAction>
                      <IconButton 
                        edge="end" 
                        onClick={() => navigate(`/visita/${v.id}`)}
                        sx={{ mr: 1 }}
                        title="Ver detalles"
                      >
                        <Visibility />
                      </IconButton>
                      <IconButton 
                        edge="end" 
                        onClick={() => handleDownloadPDF(v.id)}
                        sx={{ mr: 1 }}
                        title="Descargar PDF"
                      >
                        <Download />
                      </IconButton>
                      <IconButton 
                        edge="end" 
                        onClick={() => handleDeleteVisita(v.id)}
                        title="Eliminar visita"
                        sx={{ color: 'red' }}
                      >
                        <Delete />
                      </IconButton>
                    </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body1" color="text.secondary">
                  No hay visitas registradas aún
                </Typography>
                <Button 
                  variant="contained" 
                  onClick={() => navigate('/visita')} 
                  sx={{ mt: 2 }}
                  startIcon={<AddIcon />}
                >
                  Crear Primera Visita
                </Button>
              </Box>
            )}
          </Paper>
        </Box>
      </Container>
    </>
  );
};

export default Dashboard;