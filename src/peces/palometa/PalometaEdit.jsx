import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './PalometaEdit.module.css'; // Asegúrate de que la ruta sea correcta

const PalometaEdit = () => {
  const navigate = useNavigate();
  const [palometaData, setpalometaData] = useState([]);
  const [isSaving, setIsSaving] = useState(false);  // Estado para controlar el guardado
  const [saveMessage, setSaveMessage] = useState('');  // Estado para el mensaje de guardado

  useEffect(() => {
    // Obtener los datos del palometa desde la API
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:5000/palometa-edit');
        if (response.ok) {
          const data = await response.json();
          setpalometaData(data);
        } else {
          console.error('Error al obtener los datos:', response.statusText);
        }
      } catch (error) {
        console.error('Error de red:', error);
      }
    };

    fetchData();
  }, []);

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
