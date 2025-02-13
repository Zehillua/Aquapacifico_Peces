import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './CongrioEdit.module.css'; // Asegúrate de que la ruta sea correcta

const CongrioEdit = () => {
  const navigate = useNavigate();
  const [congrioData, setCongrioData] = useState([]);
  const [isSaving, setIsSaving] = useState(false);  // Estado para controlar el guardado
  const [saveMessage, setSaveMessage] = useState('');  // Estado para el mensaje de guardado

  useEffect(() => {
    // Obtener los datos del congrio desde la API
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:5000/congrio-edit');
        if (response.ok) {
          const data = await response.json();
          setCongrioData(data);
        } else {
          console.error('Error al obtener los datos:', response.statusText);
        }
      } catch (error) {
        console.error('Error de red:', error);
      }
    };

    fetchData();
  }, []);

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
