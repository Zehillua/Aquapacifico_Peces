import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import styles from './EditPeces.module.css'; // Asegúrate de que la ruta sea correcta

const EditPeces = () => {
  const navigate = useNavigate();
  const { id } = useParams(); // Obtener el ID del pez desde la URL
  const [pezData, setPezData] = useState(null);
  const [editedData, setEditedData] = useState({});
  const [originalData, setOriginalData] = useState({});
  const [isSaving, setIsSaving] = useState(false);  // Estado para controlar el guardado
  const [showModal, setShowModal] = useState(false);  // Estado para controlar la ventana modal
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
  }, [navigate, id]);

  const fetchUserPermissions = async (token) => {
    try {
      const response = await fetch('http://localhost:5000/profile', {
        headers: { 'Authorization': token },
      });
      const data = await response.json();
      if (data.success) {
        setCanEditPeces(data.user.ed_peces);
        if (data.user.ed_peces) {
          fetchPezData(token);
        } else {
          setError('No tienes permisos para editar peces.');
        }
      }
    } catch (error) {
      console.error('Error al obtener el perfil del usuario:', error);
      setError('Error al obtener el perfil del usuario.');
    }
  };

  const fetchPezData = async (token) => {
    try {
      const response = await fetch(`http://localhost:5000/pez/${id}`, {
        headers: {
          'Authorization': token,  // Usando el token almacenado
        },
      });
      if (!response.ok) {
        throw new Error('Permiso denegado');
      }
      const data = await response.json();
      setPezData(data);
      setEditedData(data); // Inicializar los datos editados con los valores de la API
      setOriginalData(data); // Guardar los datos originales

      // Actualizar el título de la ventana central
      if (data.nombre && data.etapa) {
        document.title = `Editar datos ${data.nombre} ${data.etapa}`;
      }
    } catch (error) {
      console.error('Error al obtener los datos:', error);
      setError(error.message);
    }
  };

  if (error) {
    return <p>{error}</p>; // Mostrar mensaje de error o redirigir
  }

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
      const token = localStorage.getItem('token'); // Obtener el token almacenado
      if (!token) {
        console.error('Token no encontrado');
        navigate('/login'); // Redirigir al login si no hay token
        return;
      }

      const change = compareChanges(originalData, editedData); // Obtener el único cambio específico
      
      const response = await fetch(`http://localhost:5000/pez/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token,  // Usando el token almacenado
        },
        body: JSON.stringify(editedData)
      });

      if (response.ok) {
        const user = 'Katherine'; // Obtener el usuario actual del token o del estado
        const pez = pezData.nombre;
        const etapa = pezData.etapa;
        const { nutriente, peso, cambioAnterior, cambioNuevo } = change;


        setShowModal(true); // Mostrar la ventana modal en caso de éxito
      } else {
        console.error('Error al actualizar los datos:', response.statusText);
      }
    } catch (error) {
      console.error('Error de red:', error);
    }

    setIsSaving(false); // Habilitar el botón de guardar nuevamente
  };

  const compareChanges = (original, edited) => {
    // Implementar lógica para comparar los datos originales y editados
    // y retornar el único cambio específico
    // Esta función debe devolver un objeto con nutriente, peso, cambioAnterior y cambioNuevo
    let changes = {
      nutriente: '',
      peso: '',
      cambioAnterior: '',
      cambioNuevo: ''
    };
    
    // Comparar los valores específicos y retornar el primer cambio encontrado
    for (let key in original.requerimientos) {
      for (let subKey in original.requerimientos[key]) {
        if (original.requerimientos[key][subKey].min !== edited.requerimientos[key][subKey].min) {
          changes = {
            nutriente: subKey,
            peso: key,
            cambioAnterior: original.requerimientos[key][subKey].min,
            cambioNuevo: edited.requerimientos[key][subKey].min
          };
          return changes; // Retornar el primer cambio encontrado
        } else if (original.requerimientos[key][subKey].max !== edited.requerimientos[key][subKey].max) {
          changes = {
            nutriente: subKey,
            peso: key,
            cambioAnterior: original.requerimientos[key][subKey].max,
            cambioNuevo: edited.requerimientos[key][subKey].max
          };
          return changes; // Retornar el primer cambio encontrado
        }
      }
    }
    return changes;
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
