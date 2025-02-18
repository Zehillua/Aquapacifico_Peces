import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './MenuPeces.module.css'; // Asegúrate de que la ruta es correcta
import congrioImage from '../assets/congrio.jpg';
import palometaImage from '../assets/palometa.jpg';
import cojinovaImage from '../assets/cojinova.jpg';
import corvinaImage from '../assets/corvina.jpg';
import logo from '../assets/LogoAquaPacifico.jpg';

const MenuPeces = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('No autorizado. Por favor, inicie sesión.');
      navigate('/login'); // Redirigir a la página de inicio de sesión si no hay token
    }
  }, [navigate]);

  const handleSelectPez = (especie, ruta) => {
    localStorage.setItem('nombre_especie', especie);
    navigate(ruta);
  };

  return (
    <div className={styles.menuPrincipalContainer}>
      <div className={styles.menuPrincipalHeader}>
        <img src={logo} alt="Logo AquaPacifico" className={styles.menuPrincipalLogo} />
        <h1>¿A qué pez desea alimentar?</h1>
      </div>
      <div className={styles.menuPrincipalPezContainer}>
        <div className={styles.menuPrincipalPezItem} onClick={() => handleSelectPez('Congrio', '/congrio')}>
          <img src={congrioImage} alt="Congrio" className={styles.menuPrincipalPezImage} />
          <p>Congrio</p>
        </div>
        <div className={styles.menuPrincipalPezItem} onClick={() => handleSelectPez('Palometa', '/palometa')}>
          <img src={palometaImage} alt="Palometa" className={styles.menuPrincipalPezImage} />
          <p>Palometa</p>
        </div>
        <div className={styles.menuPrincipalPezItem} onClick={() => handleSelectPez('Cojinova', '/cojinova')}>
          <img src={cojinovaImage} alt="Cojinova" className={styles.menuPrincipalPezImage} />
          <p>Cojinova</p>
        </div>
        <div className={styles.menuPrincipalPezItem} onClick={() => handleSelectPez('Corvina', '/corvina')}>
          <img src={corvinaImage} alt="Corvina" className={styles.menuPrincipalPezImage} />
          <p>Corvina</p>
        </div>
      </div>
      <button className={styles.menuPrincipalButton} onClick={() => navigate('/menuPrincipal')}>Volver</button>
    </div>
  );
};

export default MenuPeces;
