import os
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
workers = 2  # Reducido para Railway (más RAM por worker)
timeout = 300  # 5 minutos para generación de PDF + envío de correo
graceful_timeout = 300
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
worker_class = 'sync'  # Para operaciones síncronas como PDF y correo
