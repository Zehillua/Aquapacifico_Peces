import React, { useState, useCallback } from 'react';
import debounce from 'lodash/debounce';

const FontSizeControl = () => {
  const [fontSize, setFontSize] = useState(100); // Tamaño de fuente predeterminado (100%)

  const debouncedSetFontSize = useCallback(
    debounce((size) => {
      document.documentElement.style.fontSize = `${size}%`;
    }, 300),
    []
  );

  const handleFontSizeChange = (e) => {
    const size = e.target.value;
    setFontSize(size);
    debouncedSetFontSize(size);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', padding: '10px', backgroundColor: '#002b5c', borderRadius: '5px' }}>
      <label style={{ marginRight: '10px', color: 'white' }}>Tamaño de fuente:</label>
      <input
        type="range"
        min="50"
        max="150"
        value={fontSize}
        onChange={handleFontSizeChange}
        style={{ marginRight: '10px' }}
      />
      <span style={{ color: 'white' }}>{fontSize}%</span>
    </div>
  );
};

export default FontSizeControl;
