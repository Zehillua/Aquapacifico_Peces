import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './CongrioEdit.module.css'; // Asegúrate de que la ruta sea correcta

const CongrioEdit = () => {
  const navigate = useNavigate();
  const [congrioData, setCongrioData] = useState([]);
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
      const response = await fetch('http://localhost:5000/congrio-edit', {
        headers: {
          'Authorization': token,  // Usando el token almacenado
        },
      });
      if (!response.ok) {
        throw new Error('Permiso denegado');
      }
      const data = await response.json();
      setCongrioData(data);
    } catch (error) {
      console.error('Error al obtener los datos:', error);
      setError(error.message);
    }
  };

  if (error) {
    return <p>No tienes permisos para ver esta página.</p>; // Mostrar mensaje de error o redirigir
  }

  // Mostrar las etapas del Congrio con un botón de "Editar"
  const renderStages = () => {
    return congrioData.map((item) => (
      <div key={item._id} className={styles.stageItem}>
        <span>{item.etapa}</span>
        <button onClick={() => navigate(`/edit-peces/${item._id}`)}>Editar</button>
      </div>
    ));
  };

  return (
    <div className={styles.congrioEditContainer}>
      <h1>Editar Datos del Congrio</h1>
      {saveMessage && <div className={styles.saveMessage}>{saveMessage}</div>}
      {renderStages()}
      <button className={styles.backButton} onClick={() => navigate('/congrio')}>Volver</button>
    </div>
  );
};

export default CongrioEdit;
