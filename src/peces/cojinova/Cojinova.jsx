import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Cojinova.module.css'; // Asegúrate de que la ruta sea correcta
import logo from '../../assets/LogoAquaPacifico.jpg'; // Asegúrate de que la ruta sea correcta

const Cojinova = () => {
  const navigate = useNavigate();
  const [canEditPeces, setCanEditPeces] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('No autorizado. Por favor, inicie sesión.');
      navigate('/login'); // Redirigir a la página de inicio de sesión si no hay token
    } else {
      fetchUserPermissions(token);
    }
  }, [navigate]);

  const fetchUserPermissions = async (token) => {
    try {
      const response = await fetch('http://localhost:5000/profile', {
        headers: { 'Authorization': token },
      });
      const data = await response.json();
      if (data.success) {
        setCanEditPeces(data.user.ed_peces);
        console.log('Permisos de edición de peces:', data.user.ed_peces);
      }
    } catch (error) {
      console.error('Error al obtener el perfil del usuario:', error);
    }
  };

  const handleSelectPez = (especie, ruta) => {
    localStorage.setItem('nombre_especie', especie);
    navigate(ruta);
  };

  return (
    <div className={styles.cojinovaContainer}>
      <img src={logo} alt="Logo AquaPacifico" className={styles.cojinovaLogo} />
      <div className={styles.cojinovaContent}>
        <h2 className={styles.cojinovaHeading}>¿Qué desea hacer?</h2>
        <div className={styles.cojinovaButtonContainer}>
          <button className={styles.cojinovaButton} onClick={() => handleSelectPez('cojinova', '/cojinova-food')}>
            Alimentar
          </button>
          {canEditPeces && (
            <button className={styles.cojinovaButton} onClick={() => handleSelectPez('cojinova', '/cojinova-edit')}>
              Editar datos
            </button>
          )}
        </div>
        <button className={styles.cojinovaBackButton} onClick={() => navigate('/menuPeces')}>
          Volver
        </button>
      </div>
    </div>
  );
};

export default Cojinova;
