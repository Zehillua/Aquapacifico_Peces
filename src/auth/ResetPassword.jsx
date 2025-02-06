import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './ResetPassword.module.css';
import logo from '../assets/LogoAquaPacifico.jpg';

const ResetPassword = () => {
  const [email, setEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  // Obtener el correo verificado desde localStorage
  useEffect(() => {
    const storedEmail = localStorage.getItem("verifiedEmail");
    if (storedEmail) {
      setEmail(storedEmail);
    } else {
      alert("No se encontró un correo verificado. Por favor, verifica tu código nuevamente.");
      navigate('/verify-code');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      alert('Las contraseñas no coinciden');
      return;
    }

    setIsLoading(true); // Iniciar la carga

    console.log("Nueva contraseña ingresada:", newPassword); // Imprimir la nueva contraseña

    try {
      const response = await fetch('http://localhost:5000/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo: email, newPassword: newPassword })
      });

      const data = await response.json();
      console.log("Datos recibidos:", data); // Imprimir los datos recibidos

      if (data.success) {
        alert('Contraseña restablecida correctamente.');
        navigate('/login');
      } else {
        alert(data.message || 'Error al restablecer la contraseña');
      }
    } catch (error) {
      alert('Error en la solicitud: ' + error.message);
    } finally {
      setIsLoading(false); // Finalizar la carga
    }
  };

  return (
    <div className={styles.resetPasswordContainer}>
      <div className={styles.resetPasswordLogoContainer}>
        <img src={logo} alt="Logo AquaPacifico" className={styles.resetPasswordLogo} />
      </div>
      <div className={styles.resetPasswordFormContainer}>
        <form className={styles.resetPasswordForm} onSubmit={handleSubmit}>
          <h2 className={styles.resetPasswordHeading}>Restablecer Contraseña</h2>
          <div className={styles.resetPasswordFormGroup}>
            <label>Nueva Contraseña:</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
          </div>
          <div className={styles.resetPasswordFormGroup}>
            <label>Confirmar Nueva Contraseña:</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className={styles.resetPasswordButton} disabled={isLoading}>
            {isLoading ? 'Cargando...' : 'Restablecer Contraseña'}
          </button>
          <button type="button" onClick={() => navigate('/forgot-password')} className={styles.secondaryResetPasswordButton} disabled={isLoading}>
            {isLoading ? 'Cargando...' : 'Regresar'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;

