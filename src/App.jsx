import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Switch } from 'react-router-dom';
import Login from './auth/Login';
import Register from './auth/Register';
import ForgotPassword from './auth/ForgotPassword';
import VerifyCode from './auth/VerifyCode';
import ResetPassword from './auth/ResetPassword';
import MenuPrincipal from './menu/MenuPrincipal' // Asegúrate de ajustar la ruta de MenuPrincipal
import MenuPeces from './menuPeces/MenuPeces';
import ListaPellet from './menuIngredientes/ListaPellets';
import Congrio from './peces/congrio/Congrio';
import CongrioFood from './peces/congrio/CongrioFood';
import CongrioEdit from './peces/congrio/CongrioEdit'; // Asegúrate de importar CongrioFood
import Palometa from './peces/palometa/Palometa';
import PalometaFood from './peces/palometa/PalometaFood';
import PalometaEdit from './peces/palometa/PalometaEdit'; // Ajustar la ruta de Palometa
import Cojinova from './peces/cojinova/Cojinova';
import CojinovaFood from './peces/cojinova/CojinovaFood';
import CojinovaEdit from './peces/cojinova/CojinovaEdit'; // Ajustar la ruta de Cojinova
import Corvina from './peces/corvina/Corvina';
import CorvinaFood from './peces/corvina/CorvinaFood';
import CorvinaEdit from './peces/corvina/CorvinaEdit'; // Ajustar la ruta de Corvina
import EditPeces from './peces/edit/EditPeces'; // Asegúrate de ajustar la ruta de EditPeces
import ProtectedRoute from './components/ProtectedRoute';
import FontSizeControl from './components/FontSizeControl';

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <FontSizeControl />
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/verify-code" element={<VerifyCode />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/menuPrincipal" element={<ProtectedRoute><MenuPrincipal /></ProtectedRoute>} />
            <Route path="/menuPeces" element={<ProtectedRoute><MenuPeces /></ProtectedRoute>} />
            <Route path="/lista-pellets" element={<ProtectedRoute><ListaPellet /></ProtectedRoute>} />
            <Route path="/congrio" element={<ProtectedRoute><Congrio /></ProtectedRoute>} />
            <Route path="/congrio-food" element={<ProtectedRoute><CongrioFood /></ProtectedRoute>} />
            <Route path="/congrio-edit" element={<ProtectedRoute><CongrioEdit /></ProtectedRoute>} />
            <Route path="/edit-peces/:id" element={<ProtectedRoute><EditPeces /></ProtectedRoute>} />
            <Route path="/palometa" element={<ProtectedRoute><Palometa /></ProtectedRoute>} />
            <Route path="/palometa-food" element={<ProtectedRoute><PalometaFood /></ProtectedRoute>} />
            <Route path="/palometa-edit" element={<ProtectedRoute><PalometaEdit /></ProtectedRoute>} />
            <Route path="/cojinova" element={<ProtectedRoute><Cojinova /></ProtectedRoute>} />
            <Route path="/cojinova-food" element={<ProtectedRoute><CojinovaFood /></ProtectedRoute>} />
            <Route path="/cojinova-edit" element={<ProtectedRoute><CojinovaEdit /></ProtectedRoute>} />
            <Route path="/corvina" element={<ProtectedRoute><Corvina /></ProtectedRoute>} />
            <Route path="/corvina-food" element={<ProtectedRoute><CorvinaFood /></ProtectedRoute>} />
            <Route path="/corvina-edit" element={<ProtectedRoute><CorvinaEdit /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/login" />} />
          </Routes>
        </Router>
      </header>
    </div>
  );
};

export default App;
