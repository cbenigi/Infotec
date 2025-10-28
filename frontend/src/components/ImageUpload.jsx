import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, IconButton, CircularProgress } from '@mui/material';
import axios from '../api/axiosConfig';

const ImageUpload = ({ onUpload, images, onRemove }) => {
  const [uploading, setUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

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
      setUploadSuccess(false);
      
      const formData = new FormData();
      formData.append('file', file);
      
      axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
        .then((response) => {
          console.log('Imagen subida exitosamente:', response.data.url);
          onUpload(response.data.url);
          setUploading(false);
          setUploadSuccess(true);
          // Mantener la vista previa por un momento para confirmar
          setTimeout(() => {
            setPreviewUrl(null);
            setUploadSuccess(false);
          }, 2000);
        })
        .catch((error) => {
          console.error('Error uploading:', error);
          setUploading(false);
          setPreviewUrl(null);
          setUploadSuccess(false);
          alert('Error al subir la imagen. Por favor, intenta nuevamente.');
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
          <Typography variant="subtitle2" sx={{ mb: 1, color: uploadSuccess ? '#4caf50' : '#1976d2', fontWeight: 'bold' }}>
            {uploadSuccess ? '✅ Imagen subida exitosamente!' : 'Vista previa:'}
          </Typography>
          <img 
            src={previewUrl} 
            alt="preview" 
            style={{ 
              width: 120, 
              height: 120, 
              objectFit: 'cover',
              borderRadius: '8px',
              border: uploadSuccess ? '3px solid #4caf50' : '2px solid #1976d2',
              boxShadow: uploadSuccess ? '0 4px 12px rgba(76, 175, 80, 0.3)' : '0 2px 8px rgba(0,0,0,0.1)'
            }} 
          />
          {uploadSuccess && (
            <Typography variant="body2" sx={{ mt: 1, color: '#4caf50', fontWeight: 'bold' }}>
              La imagen se guardará al registrar
            </Typography>
          )}
        </Box>
      )}
      
      {/* Imágenes ya subidas */}
      {images.length > 0 && !previewUrl && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1, color: '#4caf50', fontWeight: 'bold' }}>
            ✅ Logo seleccionado:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
          {images.map((img, index) => (
            <Box key={index} sx={{ position: 'relative', mr: 1, mb: 1 }}>
              <img 
                src={`${axios.defaults.baseURL}${img}`} 
                alt="Logo seleccionado" 
                style={{ 
                  width: 120, 
                  height: 120, 
                  objectFit: 'cover',
                  borderRadius: '8px',
                  border: '3px solid #4caf50',
                  boxShadow: '0 4px 12px rgba(76, 175, 80, 0.3)'
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
          <Typography variant="body2" sx={{ mt: 1, color: '#666', fontStyle: 'italic' }}>
            Este logo aparecerá en los PDFs generados
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ImageUpload;