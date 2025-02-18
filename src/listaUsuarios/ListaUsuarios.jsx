import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './ListaUsuarios.module.css'; // Asegúrate de que la ruta es correcta

const ListaUsuarios = () => {
  const navigate = useNavigate();
  const [usuarios, setUsuarios] = useState([]);
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchUsuarios();
  }, []);

  const fetchUsuarios = async () => {
    try {
      const response = await fetch('http://localhost:5000/usuarios', {
        headers: { 'Authorization': localStorage.getItem('token') },
      });
      const data = await response.json();
      setUsuarios(data);
    } catch (error) {
      console.error('Error al obtener los usuarios:', error);
    }
  };

  const togglePermiso = async (id, campo) => {
    try {
      await fetch(`http://localhost:5000/usuarios/${id}`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': localStorage.getItem('token') 
        },
        body: JSON.stringify({ campo }),
      });
      fetchUsuarios();
    } catch (error) {
      console.error('Error al actualizar los permisos:', error);
    }
  };

  const handleConfirmDelete = (id) => {
    setDeleteId(id);
    setShowConfirmDelete(true);
  };

  const handleDelete = async () => {
    try {
      await fetch(`http://localhost:5000/usuarios/${deleteId}`, {
        method: 'DELETE',
        headers: { 'Authorization': localStorage.getItem('token') },
      });
      fetchUsuarios();
      setShowConfirmDelete(false);
      setMessage('Usuario eliminado correctamente');
    } catch (error) {
      console.error('Error al eliminar el usuario:', error);
    }
  };

  const renderPermiso = (id, permiso, campo) => (
    <span
      className={`${styles.permiso} ${permiso ? styles.permisoVerde : styles.permisoRojo}`}
      onClick={() => togglePermiso(id, campo)}
    ></span>
  );

  return (
    <div className={styles.listaUsuariosContainer}>
      <h1>Lista de Usuarios</h1>
      {message && <div className={styles.message}>{message}</div>}
      <table className={styles.usuariosTable}>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Cargo</th>
            <th>Edición Peces</th>
            <th>Edición Ingredientes</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {usuarios.map((usuario) => (
            <tr key={usuario._id}>
              <td>{usuario.nombre}</td>
              <td>{usuario.cargo}</td>
              <td>{renderPermiso(usuario._id, usuario.ed_peces, 'ed_peces')}</td>
              <td>{renderPermiso(usuario._id, usuario.ed_ingred, 'ed_ingred')}</td>
              <td>
                <button className={styles.actionButton} onClick={() => handleConfirmDelete(usuario._id)}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button className={styles.volverButton} onClick={() => navigate('/menuPrincipal')}>Volver</button>

      {showConfirmDelete && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <h2>Confirmar Eliminación</h2>
            <p>¿Estás seguro de que deseas eliminar este usuario?</p>
            <div className={styles.buttonContainer}>
              <button className={`${styles.confirmButton}`} onClick={handleDelete}>Confirmar</button>
              <button className={`${styles.cancelButton}`} onClick={() => setShowConfirmDelete(false)}>Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ListaUsuarios;
