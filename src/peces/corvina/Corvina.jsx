import React from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Corvina.module.css'; // Asegúrate de que la ruta sea correcta
import logo from '../../assets/LogoAquaPacifico.jpg'; // Asegúrate de que la ruta sea correcta

const Corvina = () => {
  const navigate = useNavigate();

  return (
    <div className={styles.corvinaContainer}>
      <img src={logo} alt="Logo AquaPacifico" className={styles.corvinaLogo} />
      <div className={styles.corvinaContent}>
        <h2 className={styles.corvinaHeading}>¿Qué desea hacer?</h2>
        <div className={styles.corvinaButtonContainer}>
          <button className={styles.corvinaButton} onClick={() => navigate('/corvina-food')}>
            Alimentar
          </button>
          <button className={styles.corvinaButton} onClick={() => navigate('/corvina-edit')}>
            Editar datos
          </button>
        </div>
        <button className={styles.corvinaBackButton} onClick={() => navigate('/menuPeces')}>
          Volver
        </button>
      </div>
    </div>
  );
};

export default Corvina;
