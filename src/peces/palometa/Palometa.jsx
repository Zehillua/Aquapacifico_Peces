import React from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Palometa.module.css'; // Asegúrate de que la ruta sea correcta
import logo from '../../assets/LogoAquaPacifico.jpg'; // Asegúrate de que la ruta sea correcta

const Palometa = () => {
  const navigate = useNavigate();

  return (
    <div className={styles.palometaContainer}>
      <img src={logo} alt="Logo AquaPacifico" className={styles.palometaLogo} />
      <div className={styles.palometaContent}>
        <h2 className={styles.palometaHeading}>¿Qué desea hacer?</h2>
        <div className={styles.palometaButtonContainer}>
          <button className={styles.palometaButton} onClick={() => navigate('/palometa-food')}>
            Alimentar
          </button>
          <button className={styles.palometaButton} onClick={() => navigate('/palometa-edit')}>
            Editar datos
          </button>
        </div>
        <button className={styles.palometaBackButton} onClick={() => navigate('/menuPeces')}>
          Volver
        </button>
      </div>
    </div>
  );
};

export default Palometa;
