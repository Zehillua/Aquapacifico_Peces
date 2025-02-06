import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './CongrioEdit.module.css'; // Asegúrate de que la ruta sea correcta

const CongrioEdit = () => {
  const navigate = useNavigate();
  const [congrioData, setCongrioData] = useState([]);
  const [editedData, setEditedData] = useState({});
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

  const handleEdit = (id, field, value) => {
    // Si el campo es anidado, separar el campo principal y subcampo
    const [mainField, subField] = field.split('.');
    if (subField) {
      setEditedData(prevState => ({
        ...prevState,
        [id]: {
          ...prevState[id],
          [mainField]: {
            ...prevState[id]?.[mainField],
            [subField]: value
          }
        },
      }));
    } else {
      setEditedData(prevState => ({
        ...prevState,
        [id]: {
          ...prevState[id],
          [field]: value,
        },
      }));
    }
  };

  const handleSave = async (id) => {
    setIsSaving(true); // Deshabilitar el botón de guardar

    const updatedData = editedData[id];

    // Convertir los valores a float si es posible
    const convertedData = {};
    for (const key in updatedData) {
      if (typeof updatedData[key] === 'object' && updatedData[key] !== null) {
        convertedData[key] = {};
        for (const subKey in updatedData[key]) {
          convertedData[key][subKey] = parseFloat(updatedData[key][subKey]) || updatedData[key][subKey];
        }
      } else {
        convertedData[key] = parseFloat(updatedData[key]) || updatedData[key];
      }
    }

    if (updatedData) {
      try {
        const response = await fetch('http://localhost:5000/congrio-edit', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ _id: id, ...convertedData }),
        });
        if (response.ok) {
          const data = await response.json();

          // Actualizar la tabla con los datos completos
          setCongrioData(prevData => prevData.map(item => 
            item._id === id ? { ...item, ...convertedData } : item
          ));
          setSaveMessage('Datos actualizados correctamente');
          setTimeout(() => {
            setSaveMessage('');
            window.location.reload(); // Recargar la página después de actualizar los datos
          }, 3000); // Limpiar el mensaje después de 3 segundos
        } else {
          console.error('Error al actualizar los datos:', response.statusText);
          setSaveMessage('Error al actualizar los datos');
        }
      } catch (error) {
        console.error('Error de red:', error);
        setSaveMessage('Error de red');
      }
    }

    setIsSaving(false); // Habilitar el botón de guardar nuevamente
  };

  // Obtener los nombres de los campos dinámicamente y asegurarse de que 'nombre' y 'etapa' sean los primeros
  const getColumnNames = () => {
    if (congrioData.length > 0) {
      const allKeys = new Set();
      congrioData.forEach(item => {
        Object.keys(item).forEach(key => {
          if (key !== '_id') {
            allKeys.add(key);
          }
        });
      });
      const columns = Array.from(allKeys);
      const orderedColumns = ['nombre', 'etapa', 'proteina', 'lipidos', 'carbohidratos'];
      return orderedColumns;
    }
    return [];
  };

  // Diccionario para mostrar nombres personalizados
  const displayName = {
    'nombre': 'Nombre',
    'etapa': 'Etapa',
    'proteina': 'Proteína',
    'lipidos': 'Lípidos',
    'carbohidratos': 'Carbohidratos',
    'max': 'Aumentar Peso',
    'mantener': 'Mantener Peso',
    'min': 'Disminuir Peso'
  };

  // Renderizar las celdas de la tabla, descomponiendo objetos cuando sea necesario
  const renderTableCell = (item, column) => {
    if (typeof item[column] === 'object' && item[column] !== null) {
      return (
        <>
          {Object.entries(item[column]).map(([key, value]) => (
            <div key={key} className={styles.nestedField}>
              <label>{displayName[key] || key}</label>
              <input
                type="text"
                value={editedData[item._id]?.[column]?.[key] || value}
                onChange={(e) => handleEdit(item._id, `${column}.${key}`, e.target.value)}
              />
            </div>
          ))}
        </>
      );
    }
    return (
      <input
        type="text"
        value={editedData[item._id]?.[column] || item[column]}
        onChange={(e) => handleEdit(item._id, column, e.target.value)}
      />
    );
  };

  return (
    <div className={styles.congrioEditContainer}>
      <h1>Editar Datos del Congrio</h1>
      {saveMessage && <div className={styles.saveMessage}>{saveMessage}</div>}
      <div className={styles.tableContainer}>
        <table className={styles.congrioEditTable}>
          <thead>
            <tr>
              {getColumnNames().map(column => (
                <th key={column}>{displayName[column] || column}</th>
              ))}
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {congrioData.map(item => (
              <tr key={item._id}>
                {getColumnNames().map(column => (
                  <td key={column}>
                    {renderTableCell(item, column)}
                  </td>
                ))}
                <td>
                  <button onClick={() => handleSave(item._id)} disabled={isSaving}>Guardar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button className={styles.backButton} onClick={() => navigate('/congrio')}>Volver</button>
    </div>
  );
};

export default CongrioEdit;
