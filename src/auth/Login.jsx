import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Login.module.css';
import logo from '../assets/LogoAquaPacifico.jpg'; // Asegúrate de ajustar la ruta según tu estructura de archivos

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    setIsLoading(true); // Iniciar la carga

    try {
      const response = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo: email, password })
      });

      if (!response.ok) {
        throw new Error('Error al iniciar sesión');
      }

      const data = await response.json();
      if (data.success) {
        alert('Inicio de sesión exitoso');
        localStorage.setItem('token', data.token);
        navigate('/menuPrincipal');
      } else {
        alert('Error de inicio de sesión');
      }
    } catch (error) {
      alert('Fallo en la solicitud: ' + error.message);
    } finally {
      setIsLoading(false); // Finalizar la carga
    }
  };

  return (
    <div className={styles.loginContainer}>
      <div className={styles.loginLogoContainer}>
        <img src={logo} alt="Logo AquaPacifico" className={styles.loginLogo} />
      </div>
      <div className={styles.loginFormContainer}>
        <form className={styles.loginForm} onSubmit={handleSubmit}>
          <h2 className={styles.loginHeading}>Inicio de Sesión</h2>
          <div className={styles.loginFormGroup}>
            <label>Ingrese su correo:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className={styles.loginFormGroup}>
            <label>Ingrese su contraseña:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className={styles.loginButton} disabled={isLoading}>
            {isLoading ? 'Cargando...' : 'Iniciar Sesión'}
          </button>
          <button type="button" onClick={() => navigate('/register')} className={styles.secondaryLoginButton} disabled={isLoading}>
            {isLoading ? 'Cargando...' : 'Registrarse'}
          </button>
          <button type="button" onClick={() => navigate('/forgot-password')} className={styles.secondaryLoginButton} disabled={isLoading}>
            {isLoading ? 'Cargando...' : 'Presione aquí si se le olvidó la contraseña'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
