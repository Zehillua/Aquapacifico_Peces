import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './VerifyCode.module.css';
import logo from '../assets/LogoAquaPacifico.jpg'; // Asegúrate de ajustar la ruta según tu estructura de archivos

const VerifyCode = () => {
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    setIsLoading(true); // Iniciar la carga

    console.log("Código ingresado:", code); // Imprimir el código ingresado

    try {
      const response = await fetch('http://localhost:5000/verify-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code })  // Solo enviar el código
      });

      const data = await response.json();
      console.log("Datos recibidos:", data); // Imprimir los datos recibidos

      if (data.success) {
        alert('Código verificado correctamente.');
        // Guardar el correo verificado, puede ser en el estado o en localStorage
        localStorage.setItem("verifiedEmail", data.email);
        navigate('/reset-password');
      } else {
        alert(data.message || 'Error al verificar el código');
      }
    } catch (error) {
      alert('Error en la solicitud: ' + error.message);
    } finally {
      setIsLoading(false); // Finalizar la carga
    }
  };

  return (
    <div className={styles.verifyCodeContainer}>
      <div className={styles.verifyCodeLogoContainer}>
        <img src={logo} alt="Logo AquaPacifico" className={styles.verifyCodeLogo} />
      </div>
      <div className={styles.verifyCodeFormContainer}>
        <form className={styles.verifyCodeForm} onSubmit={handleSubmit}>
          <h2 className={styles.verifyCodeHeading}>Verificar Código</h2>
          <div className={styles.verifyCodeFormGroup}>
            <label>Código:</label>
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
            />
          </div>
          <button type="submit" className={styles.verifyCodeButton} disabled={isLoading}>
            {isLoading ? 'Cargando...' : 'Verificar'}
          </button>
          <button type="button" onClick={() => navigate('/forgot-password')} className={styles.secondaryVerifyCodeButton} disabled={isLoading}>
            {isLoading ? 'Cargando...' : 'Volver a Inicio de Sesión'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default VerifyCode;

