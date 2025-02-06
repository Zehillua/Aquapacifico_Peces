import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './ListaPellets.module.css';

const ListaPellets = () => {
  const navigate = useNavigate();
  const [ingredientes, setIngredientes] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('add'); // 'add' o 'edit'
  const [currentIngrediente, setCurrentIngrediente] = useState({
    nombre: '',
    coste: '',
    proteinas: '',
    lipidos: '',
    carbohidratos: '',
    stock: ''
  });
  const [editId, setEditId] = useState(null);
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);
  const [deleteId, setDeleteId] = useState(null);

  useEffect(() => {
    fetchIngredientes();
  }, []);

  const fetchIngredientes = async () => {
    try {
      const response = await fetch('http://localhost:5000/ingredientes');
      const data = await response.json();
      setIngredientes(data);
    } catch (error) {
      console.error('Error al obtener los ingredientes:', error);
    }
  };

  const handleAdd = () => {
    setModalMode('add');
    setCurrentIngrediente({
      nombre: '',
      coste: '',
      proteinas: '',
      lipidos: '',
      carbohidratos: '',
      stock: ''
    });
    setShowModal(true);
  };

  const handleEdit = (id) => {
    const ingrediente = ingredientes.find((ing) => ing._id === id);
    setModalMode('edit');
    setCurrentIngrediente(ingrediente);
    setEditId(id);
    setShowModal(true);
  };

  const handleConfirmDelete = (id) => {
    setDeleteId(id);
    setShowConfirmDelete(true);
  };

  const handleDelete = async () => {
    try {
      await fetch(`http://localhost:5000/ingredientes/${deleteId}`, {
        method: 'DELETE',
      });
      fetchIngredientes();
      setShowConfirmDelete(false);
    } catch (error) {
      console.error('Error al eliminar el ingrediente:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const url = modalMode === 'add' ? 'http://localhost:5000/ingredientes' : `http://localhost:5000/ingredientes/${editId}`;
    const method = modalMode === 'add' ? 'POST' : 'PUT';

    try {
      await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentIngrediente),
      });
      fetchIngredientes();
      setShowModal(false);
    } catch (error) {
      console.error('Error al guardar el ingrediente:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCurrentIngrediente((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className={styles.listaPelletsContainer}>
      <h1>Lista de Ingredientes</h1>
      <button className={styles.backButton} onClick={() => navigate('/menuPrincipal')}>Volver</button>
      <button className={styles.addButton} onClick={handleAdd}>+ Agregar</button>
      <div className={styles.tableContainer}>
        <table className={styles.ingredientesTable}>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Coste</th>
              <th>Proteínas</th>
              <th>Lípidos</th>
              <th>Carbohidratos</th>
              <th>Stock</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {ingredientes.map((ingrediente) => (
              <tr key={ingrediente._id}>
                <td>{ingrediente.nombre}</td>
                <td>{ingrediente.coste}</td>
                <td>{ingrediente.proteinas}</td>
                <td>{ingrediente.lipidos}</td>
                <td>{ingrediente.carbohidratos}</td>
                <td>{ingrediente.stock}</td>
                <td>
                  <button className={styles.actionButton} onClick={() => handleEdit(ingrediente._id)}>Editar</button>
                  <button className={styles.actionButton} onClick={() => handleConfirmDelete(ingrediente._id)}>Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <h2>{modalMode === 'add' ? 'Agregar Ingrediente' : 'Editar Ingrediente'}</h2>
            <form onSubmit={handleSubmit}>
              <label>Nombre:</label>
              <input type="text" name="nombre" value={currentIngrediente.nombre} onChange={handleChange} required />
              <label>Coste:</label>
              <input type="number" name="coste" value={currentIngrediente.coste} onChange={handleChange} required />
              <label>Proteínas:</label>
              <input type="number" name="proteinas" value={currentIngrediente.proteinas} onChange={handleChange} required />
              <label>Lípidos:</label>
              <input type="number" name="lipidos" value={currentIngrediente.lipidos} onChange={handleChange} required />
              <label>Carbohidratos:</label>
              <input type="number" name="carbohidratos" value={currentIngrediente.carbohidratos} onChange={handleChange} required />
              <label>Stock:</label>
              <input type="number" name="stock" value={currentIngrediente.stock} onChange={handleChange} required />
              <button type="submit">Guardar</button>
              <button type="button" onClick={() => setShowModal(false)}>Cancelar</button>
            </form>
          </div>
        </div>
      )}

      {showConfirmDelete && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <h2>Confirmar Eliminación</h2>
            <p>¿Estás seguro de que deseas eliminar este ingrediente?</p>
            <div className={styles.buttonContainer}>
              <button className={`${styles.modalContent} ${styles.confirmButton}`} onClick={handleDelete}>Confirmar</button>
              <button className={styles.modalContent} type="button" onClick={() => setShowConfirmDelete(false)}>Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ListaPellets;
