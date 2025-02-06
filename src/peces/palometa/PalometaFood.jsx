import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './PalometaFood.module.css';
import logo from '../../assets/LogoAquaPacifico.jpg'; // Asegúrate de ajustar la ruta según tu estructura de archivos

const PalometaFood = () => {
  const navigate = useNavigate();
  const [stage, setStage] = useState('');
  const [fishCount, setFishCount] = useState('');
  const [averageWeight, setAverageWeight] = useState('');
  const [weightGoal, setWeightGoal] = useState('');
  const [yeastAmount, setYeastAmount] = useState('');
  const [proteinPercentage, setProteinPercentage] = useState('');
  const [lipidPercentage, setLipidPercentage] = useState('');
  const [carbohydratePercentage, setCarbohydratePercentage] = useState('');
  const [stages, setStages] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [yeastPercentage, setYeastPercentage] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchStages = async () => {
      try {
        const response = await fetch('http://localhost:5000/palometa-etapas', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();

        if (data.success) {
          setStages(data.etapas);
        } else {
          console.error(data.message);
        }
      } catch (error) {
        console.error("Error al obtener las etapas:", error);
      }
    };

    fetchStages();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setIsLoading(true);

    const formData = {
      etapa: stage,
      cantidad_peces: fishCount,
      peso_promedio: averageWeight,
      peso_objetivo: weightGoal,
      levadura_gramos: yeastAmount,
      proteina_actual: proteinPercentage,
      lipido_actual: lipidPercentage,
      carbohidrato_actual: carbohydratePercentage
    };

    try {
      const response = await fetch('http://localhost:5000/palometa-food', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Error al enviar el formulario');
      }

      const data = await response.json();

      if (data.success) {
        setIngredients(data.ingredientes_usados || []);
        animateYeastPercentage(data.porcentaje_levadura || 0);
      } else {
        alert(data.message || 'Error al procesar los datos');
      }
    } catch (error) {
      alert('Fallo en la solicitud: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const animateYeastPercentage = (targetPercentage) => {
    let currentPercentage = 0;
    const increment = targetPercentage / 100;

    const interval = setInterval(() => {
      if (currentPercentage < targetPercentage) {
        currentPercentage += increment;
        setYeastPercentage(currentPercentage);
      } else {
        clearInterval(interval);
        setYeastPercentage(targetPercentage);
      }
    }, 10);
  };

  const getPercentageBarClass = (percentage) => {
    if (percentage <= 25) return styles.green;
    if (percentage <= 50) return styles.yellow;
    if (percentage <= 75) return styles.orange;
    return styles.red;
  };

  return (
    <div className={styles.palometaFoodContainer}>
      <img src={logo} alt="Logo AquaPacifico" className={styles.palometaFoodLogo} />
      <div className={styles.palometaFoodMain}>
        <div className={styles.palometaFoodContent}>
          <form className={styles.palometaFoodForm} onSubmit={handleSubmit}>
            <div className={styles.palometaFoodFormGroup}>
              <label htmlFor="stage">Etapa:</label>
              <select
                id="stage"
                value={stage}
                onChange={(e) => setStage(e.target.value)}
                required
              >
                <option value="">Selecciona una etapa</option>
                {stages.map((stage) => (
                  <option key={stage} value={stage}>{stage}</option>
                ))}
              </select>
            </div>
            <div className={styles.palometaFoodFormGroup}>
              <label htmlFor="fishCount">Cantidad de peces:</label>
              <input
                type="number"
                id="fishCount"
                value={fishCount}
                onChange={(e) => setFishCount(e.target.value)}
                required
              />
            </div>
            <div className={styles.palometaFoodFormGroup}>
              <label htmlFor="averageWeight">Peso promedio (gramos):</label>
              <input
                type="number"
                step="0.01"
                id="averageWeight"
                value={averageWeight}
                onChange={(e) => setAverageWeight(e.target.value)}
                required
              />
            </div>
            <div className={styles.palometaFoodFormGroup}>
              <label htmlFor="weightGoal">Peso objetivo:</label>
              <select
                id="weightGoal"
                value={weightGoal}
                onChange={(e) => setWeightGoal(e.target.value)}
                required
              >
                <option value="">Selecciona un objetivo</option>
                <option value="aumentar">Aumentar peso</option>
                <option value="mantener">Mantener peso</option>
                <option value="disminuir">Disminuir peso</option>
              </select>
            </div>
            <div className={styles.palometaFoodFormGroup}>
              <label htmlFor="yeastAmount">Cantidad de levadura (gramos):</label>
              <input
                type="number"
                id="yeastAmount"
                value={yeastAmount}
                onChange={(e) => setYeastAmount(e.target.value)}
                required
              />
            </div>
            <div className={styles.palometaFoodFormGroup}>
              <label htmlFor="proteinPercentage">% de proteína:</label>
              <input
                type="number"
                step="0.01"
                id="proteinPercentage"
                value={proteinPercentage}
                onChange={(e) => setProteinPercentage(e.target.value)}
                required
              />
            </div>
            <div className={styles.palometaFoodFormGroup}>
              <label htmlFor="lipidPercentage">% de lípido:</label>
              <input
                type="number"
                step="0.01"
                id="lipidPercentage"
                value={lipidPercentage}
                onChange={(e) => setLipidPercentage(e.target.value)}
                required
              />
            </div>
            <div className={styles.palometaFoodFormGroup}>
              <label htmlFor="carbohydratePercentage">% de carbohidrato:</label>
              <input
                type="number"
                step="0.01"
                id="carbohydratePercentage"
                value={carbohydratePercentage}
                onChange={(e) => setCarbohydratePercentage(e.target.value)}
                required
              />
            </div>
            <button type="submit" className={styles.palometaFoodButton} disabled={isLoading}>
              {isLoading ? 'Cargando...' : 'Enviar'}
            </button>
          </form>
          <button
            type="button"
            className={styles.palometaFoodBackButton}
            onClick={() => navigate('/palometa')}
            disabled={isLoading}
          >
            {isLoading ? 'Cargando...' : 'Volver'}
          </button>
        </div>
        <div className={styles.palometaFoodDetails}>
          <div className={styles.palometaFoodDetailBox}>
            <h3>% de Levadura</h3>
            <div className={`${styles.percentageBar} ${getPercentageBarClass(Math.min(yeastPercentage, 100))}`} 
                 style={{ width: `${Math.min(yeastPercentage, 100)}%` }}>
            </div>
            <p>{yeastPercentage.toFixed(2)}%</p>
          </div>
          <div className={styles.palometaFoodDetailBox}>
            <h3>Ingredientes y Cantidades</h3>
            {ingredients.length > 0 ? (
              ingredients.map((ingredient, index) => (
                <p key={index}>{ingredient.nombre}: {ingredient.cantidad_gramos} gramos</p>
              ))
            ) : (
              <p>No hay ingredientes calculados.</p>
            )}
          </div>
          <div className={styles.palometaFoodDetailBox}>
            <h3>Listado de Ingredientes Usados y Stock Restante</h3>
            {ingredients.length > 0 ? (
              <table className={styles.ingredientsTable}>
                <thead>
                  <tr>
                    <th>Ingrediente</th>
                    <th>Cantidad Usada (gramos)</th>
                    <th>Stock Restante (gramos)</th>
                  </tr>
                </thead>
                <tbody>
                {ingredients.map((ingredient, index) => (
                    <tr key={index}>
                      <td>{ingredient.nombre}</td>
                      <td>{ingredient.cantidad_gramos}</td>
                      <td>
                        {ingredient.stock_usado
                          ? `Stock insuficiente por ${ingredient.cantidad_adicional.toFixed(2)} gramos`
                          : ingredient.stock_restante.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p>No hay ingredientes calculados.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PalometaFood;

