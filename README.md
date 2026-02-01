# 📹 Zoom Meetings Manager - Django + Zoom API

## 📋 Descripción del Proyecto
Sistema de gestión de reuniones de Zoom integrado con Django que permite:
- Crear reuniones automáticamente desde Django
- Programar clases, citas médicas, entrevistas
- Obtener enlaces de reunión únicos
- Listar reuniones programadas
- Webhooks en tiempo real
- Panel de administración completo

## 👨‍🎓 Información del Alumno
- **Nombre Completo:** Cota Guerrero Leslie Azeneth
- **Matrícula:** 24311032
- **Carrera:** Tecnico en desarollo de software multiplataformas
- **Semestre:** 5 semestre
- **Materia:** Servicios Web Orientadas a servidores
- **Profesor:** Prado Días Bernardo
- **Ciclo:** 2026-1

## 🚀 Tecnologías Utilizadas
- Python 3.x
- Django 4.2.x
- Zoom API (OAuth 2.0 User-Level (Cuenta Gratuita))
- requests 2.31.0
- MySQL
- Bootstrap 5.3.0
- ngrok (para webhooks)

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone [URL_DE_TU_REPO]
cd zoom_project
```

### 2. Crear entorno virtual
```bash
python -m venv venv
.\venv\Scripts\Activate  # Windows
source venv/bin/activate # Linux/Mac
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Zoom Marketplace
1. Crea cuenta en https://marketplace.zoom.us
2. Crea app OAuth 2.0 User-Level (Cuenta Gratuita)
3. Configura scopes necesarios
4. Obtén credenciales (Client ID, Client ID, Client Secret)
5. Activa la app

### 5. Configurar variables de entorno
```bash
# Copia el template:
copy .env.example .env

# Edita .env con tus credenciales:
ZOOM_CLIENT_ID  # Solo 2 credenciales (no Client ID)=abc123XYZ
ZOOM_CLIENT_ID=A1B2C3D4E5F6G7H8
ZOOM_CLIENT_SECRET=ABC123def456GHI789
```

### 6. Aplicar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crear superusuario
```bash
python manage.py createsuperuser
```

### 8. Ejecutar servidor
```bash
python manage.py runserver
```

### 9. Acceder al sistema
- Frontend: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## 📸 Capturas de Pantalla
(Ver carpeta `screenshots/`)
1. Dashboard principal
2. Formulario crear reunión
3. Lista de reuniones
4. Vista detallada
5. Zoom Marketplace app
6. Reunión creada en Zoom app

## 🧪 Pruebas Realizadas
- ✅ Autenticación OAuth con Zoom verificada
- ✅ Crear reunión funcional
- ✅ Listar reuniones desde BD y API
- ✅ Actualizar/eliminar reuniones
- ✅ Webhooks recibiendo eventos
- ✅ Templates renderizando correctamente

## 🔐 Seguridad
- ⚠️ `.env` está en `.gitignore`
- ⚠️ Credenciales NO incluidas en el código
- ⚠️ Variables de entorno para producción
- ⚠️ CSRF protection habilitado

## 📝 Notas Adicionales
[Agrega aquí cualquier nota relevante sobre tu implementación]

## 📚 Referencias
- Zoom API: https://developers.zoom.us/
- Zoom Marketplace: https://marketplace.zoom.us/
- Django Docs: https://docs.djangoproject.com/

## 📄 Licencia
Este proyecto es para fines educativos - UTH 2026-1