import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Congrio.module.css'; // Asegúrate de que la ruta sea correcta
import logo from '../../assets/LogoAquaPacifico.jpg'; // Asegúrate de que la ruta sea correcta

const Congrio = () => {
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
    <div className={styles.congrioContainer}>
      <img src={logo} alt="Logo AquaPacifico" className={styles.congrioLogo} />
      <div className={styles.congrioContent}>
        <h2 className={styles.congrioHeading}>¿Qué desea hacer?</h2>
        <div className={styles.congrioButtonContainer}>
          <button className={styles.congrioButton} onClick={() => navigate('/congrio-food')}>
            Alimentar
          </button>
          {isAdmin && (
            <button className={styles.congrioButton} onClick={() => navigate('/congrio-edit')}>
              Editar datos
            </button>
          )}
        </div>
        <button className={styles.congrioBackButton} onClick={() => navigate('/menuPeces')}>
          Volver
        </button>
      </div>
    </div>
  );
};

export default Congrio;
