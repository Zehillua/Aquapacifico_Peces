import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './CojinovaEdit.module.css'; // Asegúrate de que la ruta sea correcta

const CojinovaEdit = () => {
  const navigate = useNavigate();
  const [cojinovaData, setcojinovaData] = useState([]);
  const [isSaving, setIsSaving] = useState(false);  // Estado para controlar el guardado
  const [saveMessage, setSaveMessage] = useState('');  // Estado para el mensaje de guardado
  const [error, setError] = useState(null);  // Estado para manejar errores
  const [canEditPeces, setCanEditPeces] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token'); // Obtener el token almacenado
    if (!token) {
      console.error('Token no encontrado');
      navigate('/login'); // Redirigir al login si no hay token
      return;
    }

    fetchUserPermissions(token);
  }, [navigate]);

  const fetchUserPermissions = async (token) => {
    try {
      const response = await fetch('http://localhost:5000/profile', {
        headers: { 'Authorization': token },
      });
      const data = await response.json();
      if (data.success) {
        setCanEditPeces(data.user.ed_peces);
        fetchData(token); // Fetch data if the user has permission
      }
    } catch (error) {
      console.error('Error al obtener el perfil del usuario:', error);
    }
  };

  const fetchData = async (token) => {
    try {
      const response = await fetch('http://localhost:5000/cojinova-edit', {
        headers: {
          'Authorization': token,  // Usando el token almacenado
        },
      });
      if (!response.ok) {
        throw new Error('Permiso denegado');
      }
      const data = await response.json();
      setcojinovaData(data);
    } catch (error) {
      console.error('Error al obtener los datos:', error);
      setError(error.message);
    }
  };

  if (error) {
    return <p>No tienes permisos para ver esta página.</p>; // Mostrar mensaje de error o redirigir
  }

  // Mostrar las etapas del cojinova con un botón de "Editar"
  const renderStages = () => {
    return cojinovaData.map((item) => (
      <div key={item._id} className={styles.stageItem}>
        <span>{item.etapa}</span>
        <button onClick={() => navigate(`/edit-peces/${item._id}`)}>Editar</button>
      </div>
    ));
  };

  return (
    <div className={styles.cojinovaEditContainer}>
      <h1>Editar Datos del cojinova</h1>
      {saveMessage && <div className={styles.saveMessage}>{saveMessage}</div>}
      {renderStages()}
      <button className={styles.backButton} onClick={() => navigate('/cojinova')}>Volver</button>
    </div>
  );
};

export default CojinovaEdit;
