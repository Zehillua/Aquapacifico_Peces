import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './CorvinaEdit.module.css'; // Asegúrate de que la ruta sea correcta

const CorvinaEdit = () => {
  const navigate = useNavigate();
  const [corvinaData, setcorvinaData] = useState([]);
  const [isSaving, setIsSaving] = useState(false);  // Estado para controlar el guardado
  const [saveMessage, setSaveMessage] = useState('');  // Estado para el mensaje de guardado

  useEffect(() => {
    // Obtener los datos del corvina desde la API
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:5000/corvina-edit');
        if (response.ok) {
          const data = await response.json();
          setcorvinaData(data);
        } else {
          console.error('Error al obtener los datos:', response.statusText);
        }
      } catch (error) {
        console.error('Error de red:', error);
      }
    };

    fetchData();
  }, []);

  // Mostrar las etapas del corvina con un botón de "Editar"
  const renderStages = () => {
    return corvinaData.map((item) => (
      <div key={item._id} className={styles.stageItem}>
        <span>{item.etapa}</span>
        <button onClick={() => navigate(`/edit-peces/${item._id}`)}>Editar</button>
      </div>
    ));
  };

  return (
    <div className={styles.corvinaEditContainer}>
      <h1>Editar Datos del corvina</h1>
      {saveMessage && <div className={styles.saveMessage}>{saveMessage}</div>}
      {renderStages()}
      <button className={styles.backButton} onClick={() => navigate('/corvina')}>Volver</button>
    </div>
  );
};

export default CorvinaEdit;
