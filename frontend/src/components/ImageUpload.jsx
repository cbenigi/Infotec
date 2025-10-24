import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, IconButton, CircularProgress } from '@mui/material';

const ImageUpload = ({ onUpload, images, onRemove }) => {
  const [uploading, setUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0]; // Solo tomar el primer archivo
    if (file) {
      // Crear vista previa inmediata
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrl(e.target.result);
      };
      reader.readAsDataURL(file);

      setUploading(true);
      
      const formData = new FormData();
      formData.append('file', file);
      
      fetch('/upload', {
        method: 'POST',
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => {
          onUpload(data.url);
          setUploading(false);
          setPreviewUrl(null);
        })
        .catch((error) => {
          console.error('Error uploading:', error);
          setUploading(false);
          setPreviewUrl(null);
        });
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: 'image/*' });

  return (
    <Box>
      <Box {...getRootProps()} sx={{ 
        border: '2px dashed #ccc', 
        p: 2, 
        textAlign: 'center', 
        cursor: 'pointer',
        backgroundColor: uploading ? '#f5f5f5' : 'transparent',
        opacity: uploading ? 0.7 : 1
      }}>
        <input {...getInputProps()} />
        {uploading ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <CircularProgress size={24} sx={{ mb: 1 }} />
            <Typography>Subiendo imagen...</Typography>
          </Box>
        ) : isDragActive ? (
          <Typography>Arrastra las imágenes aquí...</Typography>
        ) : (
          <Typography>Arrastra y suelta imágenes aquí, o haz clic para seleccionar</Typography>
        )}
      </Box>
      
      {/* Vista previa mientras se sube */}
      {previewUrl && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Vista previa:
          </Typography>
          <img 
            src={previewUrl} 
            alt="preview" 
            style={{ 
              width: 100, 
              height: 100, 
              objectFit: 'cover',
              borderRadius: '8px',
              border: '2px solid #1976d2'
            }} 
          />
        </Box>
      )}
      
      {/* Imágenes ya subidas */}
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