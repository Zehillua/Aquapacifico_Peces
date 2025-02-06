import React from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Cojinova.module.css'; // Asegúrate de que la ruta sea correcta
import logo from '../../assets/LogoAquaPacifico.jpg'; // Asegúrate de que la ruta sea correcta

const Cojinova = () => {
  const navigate = useNavigate();

  return (
    <div className={styles.cojinovaContainer}>
      <img src={logo} alt="Logo AquaPacifico" className={styles.cojinovaLogo} />
      <div className={styles.cojinovaContent}>
        <h2 className={styles.cojinovaHeading}>¿Qué desea hacer?</h2>
        <div className={styles.cojinovaButtonContainer}>
          <button className={styles.cojinovaButton} onClick={() => navigate('/cojinova-food')}>
            Alimentar
          </button>
          <button className={styles.cojinovaButton} onClick={() => navigate('/cojinova-edit')}>
            Editar datos
          </button>
        </div>
        <button className={styles.cojinovaBackButton} onClick={() => navigate('/menuPeces')}>
          Volver
        </button>
      </div>
    </div>
  );
};

export default Cojinova;
