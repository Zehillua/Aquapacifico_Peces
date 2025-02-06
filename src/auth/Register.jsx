import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // Importa useNavigate
import styles from './Register.module.css';
import logo from '../assets/LogoAquaPacifico.jpg'; // Asegúrate de ajustar la ruta según tu estructura de archivos

const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [cargo, setCargo] = useState('');
  const [cargos, setCargos] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate(); // Usa useNavigate

  useEffect(() => {
    const fetchCargos = async () => {
      const response = await fetch('http://localhost:5000/cargos'); // Endpoint para obtener los cargos desde la base de datos
      const data = await response.json();
      setCargos(data);
    };

    fetchCargos();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert('Las contraseñas no coinciden');
      return;
    }

    setIsLoading(true); // Iniciar la carga

    try {
      const response = await fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre: name, correo: email, password, confirmPassword, cargo })
      });

      const data = await response.json();
      if (data.success) {
        alert('Registro exitoso');
        navigate('/login'); // Redirigir al inicio de sesión
      } else {
        alert('Error de registro');
      }
    } catch (error) {
      alert('Fallo en la solicitud: ' + error.message);
    } finally {
      setIsLoading(false); // Finalizar la carga
    }
  };

  return (
    <div className={styles.registerContainer}>
      <div className={styles.registerLogoContainer}>
        <img src={logo} alt="Logo AquaPacifico" className={styles.registerLogo} />
      </div>
      <div className={styles.registerFormContainer}>
        <form className={styles.registerForm} onSubmit={handleSubmit}>
          <h2 className={styles.registerHeading}>Registro</h2>
          <div className={styles.registerFormGroup}>
            <label>Ingrese su nombre:</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className={styles.registerFormGroup}>
            <label>Ingrese su correo:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className={styles.registerFormGroup}>
            <label>Ingrese su contraseña:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div className={styles.registerFormGroup}>
            <label>Reescriba su contraseña:</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>
          <div className={styles.registerFormGroup}>
            <label>Seleccione su cargo correspondiente:</label>
            <select value={cargo} onChange={(e) => setCargo(e.target.value)} required>
              <option value="">Selecciona tu cargo</option>
              {cargos.map((cargo) => (
                <option key={cargo.id} value={cargo.nombre}>{cargo.nombre}</option>
              ))}
            </select>
          </div>
          <button type="submit" className={styles.registerButton} disabled={isLoading}>
            {isLoading ? 'Cargando...' : 'Registrarse'}
          </button>
          <button type="button" onClick={() => navigate('/login')} className={`${styles.registerButton} ${styles.secondaryRegisterButton}`} disabled={isLoading}>
            {isLoading ? 'Cargando...' : 'Volver a Inicio de Sesión'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Register;
