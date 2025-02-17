import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './PalometaEdit.module.css'; // Asegúrate de que la ruta sea correcta

const PalometaEdit = () => {
  const navigate = useNavigate();
  const [palometaData, setpalometaData] = useState([]);
  const [isSaving, setIsSaving] = useState(false);  // Estado para controlar el guardado
  const [saveMessage, setSaveMessage] = useState('');  // Estado para el mensaje de guardado
  const [error, setError] = useState(null);  // Estado para manejar errores

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('token'); // Obtener el token almacenado
      if (!token) {
        console.error('Token no encontrado');
        navigate('/login'); // Redirigir al login si no hay token
        return;
      }

      try {
        const response = await fetch('http://localhost:5000/palometa-edit', {
          headers: {
            'Authorization': token,  // Usando el token almacenado
          },
        });
        if (!response.ok) {
          throw new Error('Permiso denegado');
        }
        const data = await response.json();
        setpalometaData(data);
      } catch (error) {
        console.error('Error al obtener los datos:', error);
        setError(error.message);
      }
    };

    fetchData();
  }, [navigate]);

  if (error) {
    return <p>No tienes permisos para ver esta página.</p>; // Mostrar mensaje de error o redirigir
  }

  // Mostrar las etapas del palometa con un botón de "Editar"
  const renderStages = () => {
    return palometaData.map((item) => (
      <div key={item._id} className={styles.stageItem}>
        <span>{item.etapa}</span>
        <button onClick={() => navigate(`/edit-peces/${item._id}`)}>Editar</button>
      </div>
    ));
  };

  return (
    <div className={styles.palometaEditContainer}>
      <h1>Editar Datos del palometa</h1>
      {saveMessage && <div className={styles.saveMessage}>{saveMessage}</div>}
      {renderStages()}
      <button className={styles.backButton} onClick={() => navigate('/palometa')}>Volver</button>
    </div>
  );
};

export default PalometaEdit;
