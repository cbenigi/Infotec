import React from 'react';
import { Container, Typography, Box, Grid, Card, CardContent, CardActions, Button } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import BusinessIcon from '@mui/icons-material/Business';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';

const NominaDashboard = () => {
  const navigate = useNavigate();

  return (
    <>
      <Navbar />
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 3 }}>
            Panel de Nómina
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Registra la empresa madre para comenzar a administrar tus colaboradores y sus nóminas.
          </Typography>
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, sm: 6, md: 4 }}>
              <Card sx={{ height: '100%', '&:hover': { boxShadow: 6 } }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <BusinessIcon sx={{ fontSize: 42, color: '#1976d2', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Registrar Empresa
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Configura la empresa base que respaldará todos los procesos de nómina.
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                  <Button
                    variant="contained"
                    onClick={() => navigate('/empresa')}
                    startIcon={<AddIcon />}
                    fullWidth
                  >
                    Crear Empresa
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </Container>
    </>
  );
};

export default NominaDashboard;

