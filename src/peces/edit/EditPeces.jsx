import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import styles from './EditPeces.module.css'; // Asegúrate de que la ruta sea correcta

const EditPeces = () => {
  const navigate = useNavigate();
  const { id } = useParams(); // Obtener el ID del pez desde la URL
  const [pezData, setPezData] = useState(null);
  const [editedData, setEditedData] = useState({});
  const [isSaving, setIsSaving] = useState(false);  // Estado para controlar el guardado
  const [showModal, setShowModal] = useState(false);  // Estado para controlar la ventana modal

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`http://localhost:5000/pez/${id}`);
        if (response.ok) {
          const data = await response.json();
          setPezData(data);
          setEditedData(data); // Inicializar los datos editados con los valores de la API

          // Actualizar el título de la ventana central
          if (data.nombre && data.etapa) {
            document.title = `Editar datos ${data.nombre} ${data.etapa}`;
          }
        } else {
          console.error('Error al obtener los datos:', response.statusText);
        }
      } catch (error) {
        console.error('Error de red:', error);
      }
    };

    fetchData();
  }, [id]);

  useEffect(() => {
    if (pezData) {
      // Actualizar el título de la ventana central
      const { nombre, etapa } = pezData;
      if (nombre && etapa) {
        document.title = `Editar datos ${nombre} ${etapa}`;
      }
    }
  }, [pezData]);

  const handleEdit = (field, value) => {
    setEditedData(prevState => {
      const updatedState = { ...prevState };
      const keys = field.split('.');
  
      let temp = updatedState;
      for (let i = 0; i < keys.length - 1; i++) {
        temp[keys[i]] = temp[keys[i]] || {};
        temp = temp[keys[i]];
      }
      temp[keys[keys.length - 1]] = value;
      console.log("Editando:", field, "Nuevo valor:", value);

      return { ...updatedState };
    });
  };

  const handleSave = async () => {
    setIsSaving(true); // Deshabilitar el botón de guardar

    try {
      const response = await fetch(`http://localhost:5000/pez/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editedData)
      });
      if (response.ok) {
        setShowModal(true); // Mostrar la ventana modal en caso de éxito
      } else {
        console.error('Error al actualizar los datos:', response.statusText);
      }
    } catch (error) {
      console.error('Error de red:', error);
    }

    setIsSaving(false); // Habilitar el botón de guardar nuevamente
  };

  const handleConfirm = () => {
    if (pezData && pezData.nombre) {
      navigate(`/${pezData.nombre.toLowerCase().replace(/ /g, '-')}-edit`); // Redirigir basado en el nombre del pez
    } else {
      navigate('/congrio-edit'); // Valor por defecto si no hay nombre de pez
    }
  };

  const renderField = (label, field, value) => (
    <div className={styles.fieldContainer}>
      <label>{label}</label>
      <input
        type="text"
        value={editedData[field] !== undefined ? editedData[field] : value}
        onChange={(e) => handleEdit(field, e.target.value)}
      />
    </div>
  );

  const renderColumn = (title, key) => (
    <form className={styles.column}>
      <h3>{title}</h3>
      {Object.entries(pezData.requerimientos[key]).map(([subKey, subValue]) => (
        <React.Fragment key={`${key}.${subKey}`}>
          {renderField(`${subKey} Min`, `requerimientos.${key}.${subKey}.min`, subValue.min)}
          {renderField(`${subKey} Max`, `requerimientos.${key}.${subKey}.max`, subValue.max)}
        </React.Fragment>
      ))}
      <button type="button" onClick={handleSave} disabled={isSaving} className={styles.saveButton}>
        {isSaving ? 'Guardando...' : 'Guardar'}
      </button>
    </form>
  );

  return (
    <div className={styles.pezEditContainer}>
      <h1>Editar datos {pezData?.nombre} {pezData?.etapa}</h1>
      {pezData && (
        <div className={styles.tableContainer}>
          {renderColumn('Mantener', 'mantener')}
          {renderColumn('Aumentar', 'aumentar')}
          {renderColumn('Disminuir', 'disminuir')}
        </div>
      )}
      <button onClick={handleConfirm} className={styles.backButton}>Volver</button>

      {/* Ventana modal */}
      {showModal && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <p>Datos guardados correctamente</p>
            <button onClick={handleConfirm}>Confirmar</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EditPeces;
