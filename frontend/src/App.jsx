import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import NominaDashboard from './pages/NominaDashboard';
import VisitaForm from './pages/VisitaForm';
import EmpresaForm from './pages/EmpresaForm';
import ClienteForm from './pages/ClienteForm';
import SupervisorForm from './pages/SupervisorForm';
import Atencion from './pages/Atencion';
import CotizacionHistorial from './pages/CotizacionHistorial';
import CotizacionForm from './pages/CotizacionForm';
import OrdenCompraHistorial from './pages/OrdenCompraHistorial';
import OrdenCompraForm from './pages/OrdenCompraForm';
import ProveedorForm from './pages/ProveedorForm';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/empresa" element={<EmpresaForm />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/dashboard/nomina" element={<NominaDashboard />} />
          <Route path="/visita/:id?" element={<VisitaForm />} />
          <Route path="/clientes/new" element={<ClienteForm />} />
          <Route path="/supervisores/new" element={<SupervisorForm />} />
          <Route path="/atencion" element={<Atencion />} />
          <Route path="/cotizaciones" element={<CotizacionHistorial />} />
          <Route path="/cotizacion/nueva" element={<CotizacionForm />} />
          <Route path="/cotizacion/:id" element={<CotizacionForm />} />
          <Route path="/ordenes-compra" element={<OrdenCompraHistorial />} />
          <Route path="/orden-compra/nueva" element={<OrdenCompraForm />} />
          <Route path="/orden-compra/:id" element={<OrdenCompraForm />} />
          <Route path="/proveedores/nuevo" element={<ProveedorForm />} />
          <Route path="/" element={<Login />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;