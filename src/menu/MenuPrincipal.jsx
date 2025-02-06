import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './MenuPrincipal.module.css'; // Asegúrate de que la ruta es correcta
import logo from '../assets/LogoAquaPacifico.jpg'; // Asegúrate de que la ruta sea correcta
import pecesImage from '../assets/peces.jpg'; // Imagen de peces
import pelletImage from '../assets/pellet.jpg'; // Imagen de pellets

const MenuPrincipal = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('No autorizado. Por favor, inicie sesión.');
      navigate('/login'); // Redirigir a la página de inicio de sesión si no hay token
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login'); // Redirigir a la página de inicio de sesión al cerrar sesión
  };

  return (
    <div className={styles.menuPrincipalContainer}>
      <div className={styles.menuPrincipalHeader}>
        <img src={logo} alt="Logo AquaPacifico" className={styles.menuPrincipalLogo} />
        <h1>¿Qué sección va a modificar?</h1>
      </div>
      <div className={styles.menuPrincipalPezContainer}>
        <div className={styles.menuPrincipalPezItem} onClick={() => navigate('/menuPeces')}>
          <img src={pecesImage} alt="Peces" className={styles.menuPrincipalPezImage} />
          <p>Peces</p>
        </div>
        <div className={styles.menuPrincipalPezItem} onClick={() => navigate('/lista-pellets')}>
          <img src={pelletImage} alt="Pellets" className={styles.menuPrincipalPezImage} />
          <p>Pellets</p>
        </div>
      </div>
      <button className={styles.menuPrincipalButton} onClick={handleLogout}>Cerrar Sesión</button>
    </div>
  );
};

export default MenuPrincipal;
