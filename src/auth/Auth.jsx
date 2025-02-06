import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Auth.module.css';
import loginStyles from './Login.module.css';
import registerStyles from './Register.module.css';
import logo from '../assets/LogoAquaPacifico.jpg';

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();

  const toggleForm = () => {
    setIsLogin(!isLogin);
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    // Lógica para manejar el inicio de sesión
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    // Lógica para manejar el registro
  };

  return (
    <div className={styles.authContainer}>
      <div className={styles.authLogoContainer}>
        <img src={logo} alt="Logo AquaPacifico" className={styles.authLogo} />
      </div>
      <div className={styles.authFormContainer}>
        <form className={`${styles.authForm} ${loginStyles.loginForm} ${isLogin ? styles.active : ''}`} onSubmit={handleLoginSubmit}>
          <h2 className={loginStyles.loginHeading}>Inicio de Sesión</h2>
          <div className={loginStyles.loginFormGroup}>
            <label>Ingrese su correo:</label>
            <input type="email" required />
          </div>
          <div className={loginStyles.loginFormGroup}>
            <label>Ingrese su contraseña:</label>
            <input type="password" required />
          </div>
          <button type="submit" className={loginStyles.loginButton}><span>Iniciar Sesión</span></button>
          <button type="button" onClick={toggleForm} className={`${loginStyles.loginButton} ${loginStyles.secondaryLoginButton}`}><span>Registrarse</span></button>
        </form>

        <form className={`${styles.authForm} ${registerStyles.registerForm} ${!isLogin ? styles.active : ''}`} onSubmit={handleRegisterSubmit}>
          <h2 className={registerStyles.registerHeading}>Registro</h2>
          <div className={registerStyles.registerFormGroup}>
            <label>Ingrese su nombre:</label>
            <input type="text" required />
          </div>
          <div className={registerStyles.registerFormGroup}>
            <label>Ingrese su correo:</label>
            <input type="email" required />
          </div>
          <div className={registerStyles.registerFormGroup}>
            <label>Ingrese su contraseña:</label>
            <input type="password" required />
          </div>
          <div className={registerStyles.registerFormGroup}>
            <label>Reescriba su contraseña:</label>
            <input type="password" required />
          </div>
          <div className={registerStyles.registerFormGroup}>
            <label>Seleccione su cargo correspondiente:</label>
            <select required>
              <option value="">Selecciona tu cargo</option>
              {/* Cargos dinámicos */}
            </select>
          </div>
          <button type="submit" className={registerStyles.registerButton}><span>Registrarse</span></button>
          <button type="button" onClick={toggleForm} className={`${registerStyles.registerButton} ${registerStyles.secondaryRegisterButton}`}><span>Volver a Inicio de Sesión</span></button>
        </form>
      </div>
    </div>
  );
};

export default Auth;
