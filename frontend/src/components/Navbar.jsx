import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, IconButton, Menu, MenuItem, Avatar } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import MenuIcon from '@mui/icons-material/Menu';
import BusinessIcon from '@mui/icons-material/Business';
import PersonIcon from '@mui/icons-material/Person';
import LogoutIcon from '@mui/icons-material/Logout';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AssignmentIcon from '@mui/icons-material/Assignment';
import PeopleIcon from '@mui/icons-material/People';
import axios from 'axios';

const Navbar = () => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [empresa, setEmpresa] = useState(null);
  const [userName, setUserName] = useState('Usuario');

  useEffect(() => {
    // Obtener datos de la empresa
    const fetchEmpresa = async () => {
      try {
        const res = await axios.get('http://localhost:5000/empresa');
        if (res.data.exists) {
          setEmpresa(res.data);
        }
      } catch (err) {
        console.error('Error al cargar empresa:', err);
      }
    };
    fetchEmpresa();

    // Obtener nombre del usuario del localStorage o session
    const storedName = localStorage.getItem('userName');
    if (storedName) {
      setUserName(storedName);
    }
  }, []);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    try {
      await axios.post('http://localhost:5000/logout');
      localStorage.clear();
      navigate('/login');
    } catch (err) {
      console.error('Error al cerrar sesión:', err);
      localStorage.clear();
      navigate('/login');
    }
  };

  return (
    <AppBar position="static" sx={{ backgroundColor: '#ffffff', color: '#1976d2', boxShadow: 2 }}>
      <Toolbar>
        {/* Logo de la empresa o icono por defecto */}
        <Box sx={{ display: 'flex', alignItems: 'center', mr: 3 }}>
          {empresa && empresa.logo_url ? (
            <Avatar
              src={`http://localhost:5000${empresa.logo_url}`}
              alt={empresa.nombre}
              sx={{ width: 45, height: 45, mr: 1.5, border: '2px solid #1976d2' }}
            />
          ) : (
            <BusinessIcon sx={{ fontSize: 40, mr: 1.5, color: '#1976d2' }} />
          )}
          <Box>
            <Typography variant="h6" component="div" sx={{ fontWeight: 600, color: '#1976d2', lineHeight: 1.2 }}>
              {empresa ? empresa.nombre : 'Informetec'}
            </Typography>
            <Typography variant="caption" sx={{ color: '#666', fontSize: '0.7rem' }}>
              Informes Técnicos
            </Typography>
          </Box>
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        {/* Navegación principal - Desktop */}
        <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1, mr: 2 }}>
          <Button
            color="inherit"
            startIcon={<DashboardIcon />}
            onClick={() => navigate('/dashboard')}
            sx={{ '&:hover': { backgroundColor: 'rgba(25, 118, 210, 0.08)' } }}
          >
            Dashboard
          </Button>
          <Button
            color="inherit"
            startIcon={<PeopleIcon />}
            onClick={() => navigate('/clientes')}
            sx={{ '&:hover': { backgroundColor: 'rgba(25, 118, 210, 0.08)' } }}
          >
            Clientes
          </Button>
          <Button
            color="inherit"
            startIcon={<AssignmentIcon />}
            onClick={() => navigate('/visita')}
            sx={{ '&:hover': { backgroundColor: 'rgba(25, 118, 210, 0.08)' } }}
          >
            Nueva Visita
          </Button>
        </Box>

        {/* Usuario y menú */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ display: { xs: 'none', sm: 'flex' }, alignItems: 'center', mr: 1 }}>
            <PersonIcon sx={{ mr: 0.5, color: '#1976d2' }} />
            <Typography variant="body2" sx={{ color: '#333', fontWeight: 500 }}>
              {userName}
            </Typography>
          </Box>
          
          <IconButton
            size="large"
            onClick={handleMenu}
            color="inherit"
            sx={{ display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Button
            variant="outlined"
            startIcon={<LogoutIcon />}
            onClick={handleLogout}
            size="small"
            sx={{
              display: { xs: 'none', md: 'flex' },
              borderColor: '#1976d2',
              color: '#1976d2',
              '&:hover': {
                borderColor: '#1565c0',
                backgroundColor: 'rgba(25, 118, 210, 0.08)'
              }
            }}
          >
            Salir
          </Button>
        </Box>

        {/* Menú móvil */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleClose}
          sx={{ mt: 1 }}
        >
          <MenuItem onClick={() => { navigate('/dashboard'); handleClose(); }}>
            <DashboardIcon sx={{ mr: 1 }} /> Dashboard
          </MenuItem>
          <MenuItem onClick={() => { navigate('/clientes'); handleClose(); }}>
            <PeopleIcon sx={{ mr: 1 }} /> Clientes
          </MenuItem>
          <MenuItem onClick={() => { navigate('/visita'); handleClose(); }}>
            <AssignmentIcon sx={{ mr: 1 }} /> Nueva Visita
          </MenuItem>
          <MenuItem onClick={handleLogout}>
            <LogoutIcon sx={{ mr: 1 }} /> Cerrar Sesión
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;

