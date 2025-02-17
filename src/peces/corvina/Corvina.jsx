import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Corvina.module.css'; // Asegúrate de que la ruta sea correcta
import logo from '../../assets/LogoAquaPacifico.jpg'; // Asegúrate de que la ruta sea correcta

const Corvina = () => {
  const navigate = useNavigate();
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const fetchUserRole = async () => {
      const token = localStorage.getItem('token'); // Obtener el token almacenado
      if (!token) {
        console.error('Token no encontrado');
        return;
      }

      try {
        const response = await fetch('http://localhost:5000/profile', {
          headers: {
            'Authorization': token,  // Usando el token almacenado
          },
        });
        const data = await response.json();
        if (data.success) {
          setIsAdmin(data.user.is_admin);
        }
      } catch (error) {
        console.error('Error al obtener el perfil del usuario:', error);
      }
    };

    fetchUserRole();
  }, []);

  return (
    <div className={styles.corvinaContainer}>
      <img src={logo} alt="Logo AquaPacifico" className={styles.corvinaLogo} />
      <div className={styles.corvinaContent}>
        <h2 className={styles.corvinaHeading}>¿Qué desea hacer?</h2>
        <div className={styles.corvinaButtonContainer}>
          <button className={styles.corvinaButton} onClick={() => navigate('/corvina-food')}>
            Alimentar
          </button>
          {isAdmin && (
            <button className={styles.corvinaButton} onClick={() => navigate('/corvina-edit')}>
              Editar datos
            </button>
          )}
        </div>
        <button className={styles.corvinaBackButton} onClick={() => navigate('/menuPeces')}>
          Volver
        </button>
      </div>
    </div>
  );
};

export default Corvina;