import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './ForgotPassword.module.css';
import logo from '../assets/LogoAquaPacifico.jpg'; // Asegúrate de ajustar la ruta según tu estructura de archivos

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [confirmEmail, setConfirmEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (email !== confirmEmail) {
      alert('Los correos electrónicos no coinciden');
      return;
    }

    setIsLoading(true); // Iniciar la carga

    console.log("Correo electrónico enviado:", email); // Imprimir el correo electrónico enviado

    try {
      const response = await fetch('http://localhost:5000/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo: email, confirmCorreo: confirmEmail })
      });

      console.log("Response recibido:", response); // Imprimir la respuesta del servidor

      const data = await response.json();
      console.log("Datos recibidos:", data); // Imprimir los datos recibidos

      if (data.success) {
        alert('Código enviado a tu correo electrónico');
        navigate('/verify-code');
      } else {
        alert(data.message || 'Error al enviar el código');
      }
    } catch (error) {
      alert('Error en la solicitud: ' + error.message);
    } finally {
      setIsLoading(false); // Finalizar la carga
    }
  };

  return (
    <div className={styles.forgotPasswordContainer}>
      <div className={styles.forgotPasswordLogoContainer}>
        <img src={logo} alt="Logo AquaPacifico" className={styles.forgotPasswordLogo} />
      </div>
      <div className={styles.forgotPasswordFormContainer}>
        <form className={styles.forgotPasswordForm} onSubmit={handleSubmit}>
          <h2 className={styles.forgotPasswordHeading}>Recuperar Contraseña</h2>
          <div className={styles.forgotPasswordFormGroup}>
            <label>Ingrese su correo electrónico registrado:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className={styles.forgotPasswordFormGroup}>
            <label>Reescriba el correo electrónico para confirmar:</label>
            <input
              type="email"
              value={confirmEmail}
              onChange={(e) => setConfirmEmail(e.target.value)}
              required
            />
          </div>
          <button type="submit" className={styles.forgotPasswordButton} disabled={isLoading}>
            {isLoading ? 'Cargando...' : 'Enviar Código a su correo'}
          </button>
          <button type="button" onClick={() => navigate('/login')} className={styles.secondaryForgotPasswordButton} disabled={isLoading}>
            {isLoading ? 'Cargando...' : 'Volver a Inicio de Sesión'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ForgotPassword;
