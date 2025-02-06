import React from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Congrio.module.css'; // Asegúrate de que la ruta sea correcta
import logo from '../../assets/LogoAquaPacifico.jpg'; // Asegúrate de que la ruta sea correcta

const Congrio = () => {
  const navigate = useNavigate();

  return (
    <div className={styles.congrioContainer}>
      <img src={logo} alt="Logo AquaPacifico" className={styles.congrioLogo} />
      <div className={styles.congrioContent}>
        <h2 className={styles.congrioHeading}>¿Qué desea hacer?</h2>
        <div className={styles.congrioButtonContainer}>
          <button className={styles.congrioButton} onClick={() => navigate('/congrio-food')}>
            Alimentar
          </button>
          <button className={styles.congrioButton} onClick={() => navigate('/congrio-edit')}>
            Editar datos
          </button>
        </div>
        <button className={styles.congrioBackButton} onClick={() => navigate('/menuPeces')}>
          Volver
        </button>
      </div>
    </div>
  );
};

export default Congrio;
