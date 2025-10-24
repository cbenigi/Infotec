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
      {images.length > 0 && (
        <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap' }}>
          {images.map((img, index) => (
            <Box key={index} sx={{ position: 'relative', mr: 1, mb: 1 }}>
              <img 
                src={`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}${img}`} 
                alt="preview" 
                style={{ 
                  width: 100, 
                  height: 100, 
                  objectFit: 'cover',
                  borderRadius: '8px',
                  border: '2px solid #1976d2'
                }} 
              />
              <IconButton 
                size="small" 
                onClick={() => onRemove(index)} 
                sx={{ 
                  position: 'absolute', 
                  top: -8, 
                  right: -8,
                  backgroundColor: 'red',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'darkred'
                  }
                }}
              >
                ×
              </IconButton>
            </Box>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default ImageUpload;