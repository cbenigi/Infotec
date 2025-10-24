import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, IconButton } from '@mui/material';

const ImageUpload = ({ onUpload, images, onRemove }) => {
  const onDrop = useCallback((acceptedFiles) => {
    acceptedFiles.forEach((file) => {
      const formData = new FormData();
      formData.append('file', file);
      fetch('/upload', {
        method: 'POST',
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => onUpload(data.url));
    });
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: 'image/*' });

  return (
    <Box>
      <Box {...getRootProps()} sx={{ border: '2px dashed #ccc', p: 2, textAlign: 'center', cursor: 'pointer' }}>
        <input {...getInputProps()} />
        {isDragActive ? <Typography>Arrastra las imágenes aquí...</Typography> : <Typography>Arrastra y suelta imágenes aquí, o haz clic para seleccionar</Typography>}
      </Box>
      <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap' }}>
        {images.map((img, index) => (
          <Box key={index} sx={{ position: 'relative', mr: 1, mb: 1 }}>
            <img src={`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}${img}`} alt="preview" style={{ width: 100, height: 100, objectFit: 'cover' }} />
            <IconButton size="small" onClick={() => onRemove(index)} sx={{ position: 'absolute', top: 0, right: 0 }}>
              <span style={{ fontSize: '18px', color: 'red' }}>×</span>
            </IconButton>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default ImageUpload;