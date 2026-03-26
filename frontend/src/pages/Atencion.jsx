import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Skeleton
} from '@mui/material';
import {
  Search as SearchIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Clear as ClearIcon,
  SupportAgent as SupportIcon
} from '@mui/icons-material';
import axios from '../api/axiosConfig';

const Atencion = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);

  // Estados para edición
  const [editForm, setEditForm] = useState({});

  const filterOptions = [
    { value: 'all', label: 'Todo' },
    { value: 'visitas', label: 'Visitas' },
    { value: 'clientes', label: 'Clientes' },
    { value: 'supervisores', label: 'Supervisores' }
  ];

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    try {
      const results = await axios.get(`/search?q=${encodeURIComponent(searchTerm)}&type=${filterType}`);
      setSearchResults(results.data);
    } catch (error) {
      console.error('Error en búsqueda:', error);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearSearch = () => {
    setSearchTerm('');
    setSearchResults([]);
    setFilterType('all');
  };

  const handleEdit = (item) => {
    setSelectedItem(item);
    setEditForm(item);
    setEditDialogOpen(true);
  };

  const handleView = (item) => {
    setSelectedItem(item);
    setViewDialogOpen(true);
  };

  const handleSaveEdit = async () => {
    try {
      // Aquí implementarías la lógica de guardado según el tipo
      console.log('Guardando:', editForm);
      setEditDialogOpen(false);
      // Recargar resultados
      handleSearch();
    } catch (error) {
      console.error('Error al guardar:', error);
    }
  };

  const renderSearchResults = () => {
    if (loading) {
      return (
        <Grid container spacing={2} sx={{ mt: 2 }}>
          {[1, 2, 3].map((i) => (
            <Grid item xs={12} md={6} lg={4} key={i}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Skeleton variant="text" width="60%" height={32} />
                  <Skeleton variant="text" width="40%" />
                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <Skeleton variant="circular" width={32} height={32} />
                    <Skeleton variant="circular" width={32} height={32} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      );
    }

    if (searchResults.length === 0 && searchTerm) {
      return (
        <Alert severity="info" sx={{ mt: 2 }}>
          No se encontraron resultados para "{searchTerm}"
        </Alert>
      );
    }

    return (
      <Grid container spacing={2} sx={{ mt: 2 }}>
        {searchResults.map((item, index) => (
          <Grid item xs={12} md={6} lg={4} key={index}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Typography variant="h6" component="div">
                    {item.tipo === 'visita' ? `Visita ${item.id}` : 
                     item.tipo === 'cliente' ? item.nombre : 
                     item.tipo === 'supervisor' ? item.nombre : 'Item'}
                  </Typography>
                  <Chip 
                    label={item.tipo} 
                    size="small" 
                    color={item.tipo === 'visita' ? 'primary' : 
                           item.tipo === 'cliente' ? 'secondary' : 'default'}
                  />
                </Box>
                
                <Typography variant="body2" color="text.secondary" paragraph>
                  {item.tipo === 'visita' ? `Cliente: ${item.cliente_nombre}` :
                   item.tipo === 'cliente' ? `NIT: ${item.nit}` :
                   item.tipo === 'supervisor' ? `Email: ${item.email}` : ''}
                </Typography>

                {item.tipo === 'visita' && (
                  <Typography variant="body2" color="text.secondary">
                    Fecha: {item.fecha} | Supervisor: {item.supervisor_nombre}
                  </Typography>
                )}

                {(item.tipo !== 'visita') && (
                  <Box display="flex" gap={1} mt={2}>
                    <IconButton 
                      size="small" 
                      color="primary" 
                      onClick={() => handleView(item)}
                    >
                      <ViewIcon />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      color="secondary" 
                      onClick={() => handleEdit(item)}
                    >
                      <EditIcon />
                    </IconButton>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" mb={3}>
        <SupportIcon sx={{ mr: 2, fontSize: 32, color: '#f57c00' }} />
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          Centro de Atención
        </Typography>
      </Box>

      {/* Buscador */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Buscador Avanzado
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Tipo de búsqueda</InputLabel>
                <Select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  label="Tipo de búsqueda"
                >
                  {filterOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Buscar visitas, clientes, supervisores..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                  endAdornment: searchTerm && (
                    <InputAdornment position="end">
                      <IconButton onClick={handleClearSearch} size="small">
                        <ClearIcon />
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={handleSearch}
                disabled={!searchTerm.trim()}
                sx={{ height: '56px' }}
              >
                Buscar
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Resultados */}
      {renderSearchResults()}

      {/* Dialog de Edición */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Editar {selectedItem?.tipo}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Funcionalidad de edición en desarrollo...
          </Typography>
          {/* Aquí irían los campos de edición según el tipo */}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancelar</Button>
          <Button onClick={handleSaveEdit} variant="contained">Guardar</Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de Visualización */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Detalles de {selectedItem?.tipo}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Funcionalidad de visualización en desarrollo...
          </Typography>
          {/* Aquí irían los detalles del item */}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Cerrar</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Atencion;
