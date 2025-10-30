# PetFans

Aplicación web Django para la gestión de mascotas.

## Configuración del Entorno

### 1. Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables según tu entorno:

### 2. Variables de Entorno Requeridas

#### Para Desarrollo Local:
```env
DJANGO_ENVIRONMENT=local
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
POSTGRES_DB=petfans
POSTGRES_USER=postgres  
POSTGRES_PASSWORD=tu_password_aqui
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Para Docker
POSTGRES_HOST=db

# Email
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password_aqui
EMAIL_USE_TLS=True

# CORS (para desarrollo)
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3002,http://localhost:3003
```

#### Para Producción:
```env
DJANGO_ENVIRONMENT=production
SECRET_KEY=tu_clave_secreta_super_segura
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Base de datos de producción
POSTGRES_DB=petfans_prod
POSTGRES_USER=petfans_user
POSTGRES_PASSWORD=password_super_seguro
POSTGRES_HOST=tu-servidor-db.com
POSTGRES_PORT=5432

# Email de producción
EMAIL_HOST_USER=noreply@tu-dominio.com
EMAIL_HOST_PASSWORD=password_aplicacion_seguro
EMAIL_USE_TLS=True

# CORS (para producción)
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
```

### 3. Instalación

```bash
# 1. Crear archivo .env con las variables mostradas arriba

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar migraciones
python manage.py migrate

# 4. Crear superusuario
python manage.py createsuperuser

# 5. Ejecutar servidor de desarrollo
python manage.py runserver
```

### 4. Docker

```bash
# Construir y ejecutar con Docker Compose
docker-compose up --build

# Para ejecutar en segundo plano
docker-compose up -d
```

## Seguridad

⚠️ **IMPORTANTE**: 

- Nunca commitees el archivo `.env` al repositorio
- Cambia todas las claves y passwords por defecto antes de usar en producción
- Usa `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` para generar una nueva SECRET_KEY
- Para el email, usa contraseñas de aplicación específicas, no tu contraseña principal

## Estructura del Proyecto

```
petfans/
├── core/                 # App principal
├── petfans/             # Configuración del proyecto
│   ├── settings/        # Configuraciones por entorno
│   │   ├── base.py     # Configuración base
│   │   ├── local.py    # Configuración de desarrollo
│   │   └── prod.py     # Configuración de producción
├── media/               # Archivos multimedia
├── .env                 # Variables de entorno (NO COMMITEAR)
├── .env.example         # Ejemplo de variables de entorno
├── .gitignore           # Archivos ignorados por Git
├── docker-compose.yaml  # Configuración de Docker
├── Procfile             # Configuración para Railway
├── railway.json         # Configuración Railway
├── requirements.txt     # Dependencias de Python
├── FEATURES.md          # Estado de funcionalidades
└── RAILWAY_DEPLOY.md    # Guía de deploy paso a paso
```

## 🚀 Deploy en Producción

Este proyecto está listo para deploy en Railway.app. Ver guía completa en:

📖 **[RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md)** - Guía paso a paso completa

### Deploy rápido:

1. Push a GitHub
2. Conectar repo en Railway.app
3. Agregar PostgreSQL
4. Configurar variables de entorno
5. Deploy automático ✨

Tiempo estimado: **5-10 minutos**

## Contribución

1. Clona el repositorio
2. Configura tu entorno según las instrucciones anteriores
3. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
4. Realiza tus cambios y commitea: `git commit -m 'Agregar nueva funcionalidad'`
5. Push a la rama: `git push origin feature/nueva-funcionalidad`
6. Abre un Pull Request

## 📚 Documentación Adicional

- **[FEATURES.md](FEATURES.md)** - Estado completo de funcionalidades
- **[DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md)** - Checklist técnico de deploy
- **[RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md)** - Guía de deploy en Railway
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - Guía para desarrolladores

