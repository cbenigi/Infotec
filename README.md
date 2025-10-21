# Informetec - Informes de Visitas Técnicas

## Por qué hice esto

En una ocasión tuve la oportunidad de contactarme con varias empresas de aseo y mantenimiento, y me di cuenta de que tienen problemas serios con sus procesos de documentación. Muchas siguen usando papel, Excel o formatos desordenados para registrar sus visitas técnicas. Esto les hace perder tiempo, se les pierden los documentos, y no se ve profesional frente a sus clientes.

Vi ahí una oportunidad real de ayudar. Quería crear una solución inicial con una buena propuesta de valor que les facilitara el trabajo del día a día. La idea es empezar con lo básico pero bien hecho, y si funciona, después agregar más funciones según lo que realmente necesiten.

## Qué hace esta aplicación

Es una herramienta web para que las empresas de aseo puedan llevar el registro de sus visitas técnicas de manera ordenada y generar informes en PDF que se ven profesionales. Así de simple.

Básicamente puedes:

- Registrar tus clientes
- Crear visitas técnicas para cada cliente
- Tomar o subir fotos de las diferentes zonas donde trabajaste
- Generar un PDF automático con toda la información y las fotos bien organizadas (Solo desde pagina web) que sera hosteada en vercel tanto el frontend como el backend ya que me permite la logica en flask Python que tenemos.

El PDF sale con un formato específico que incluye el logo de la empresa, tablas con los datos, las fotos de cada zona, y se ve bastante profesional.

## Con qué está hecho

La parte de atrás (donde se guarda todo y se hace la lógica):

- Python con Flask
- PostgreSQL para la base de datos
- ReportLab para generar los PDFs
- Flask-Mail por si después se quiere enviar los informes por email

La parte de adelante (lo que ven los usuarios):

- React para la interfaz
- Material-UI para que se vea bien
- React Router para navegar entre páginas
- Axios para comunicarse con el backend
- React Dropzone para subir fotos fácilmente

Todo se puede correr con Docker para que sea más fácil de instalar y mover a producción.

## Próximas Herramientas

Como dije, esto es solo el punto de partida. Hay muchas cosas que se podrían agregar después:

- Envío automático de informes por email
- Firma digital del cliente
- Estadísticas y reportes
- App móvil para tomar fotos directo desde el celular
- Gestión de inventario
- Y lo que vaya surgiendo según las necesidades reales
