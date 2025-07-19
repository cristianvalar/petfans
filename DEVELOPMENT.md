# Guía de Desarrollo - PetFans

## Flujo de Trabajo con Git

### Estructura de Ramas

- **main**: Rama principal con código estable y listo para producción
- **dev**: Rama de desarrollo donde se integran las nuevas funcionalidades
- **feature/**: Ramas para desarrollar funcionalidades específicas

### Workflow Recomendado

1. **Para nuevas funcionalidades:**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/nombre-de-la-funcionalidad
   # Desarrollar la funcionalidad
   git add .
   git commit -m "Descripción de los cambios"
   git push origin feature/nombre-de-la-funcionalidad
   # Crear Pull Request hacia dev
   ```

2. **Para integrar a producción:**
   ```bash
   git checkout main
   git merge dev
   git push origin main
   ```

### Ejemplos de Nombres de Ramas

- `feature/user-authentication`
- `feature/pet-profile-photos`
- `feature/search-filters`
- `bugfix/login-validation`
- `hotfix/security-patch`

## Configuración de Desarrollo

### Entorno Local
- Python 3.x
- Django
- PostgreSQL (recomendado para producción)
- Docker para desarrollo

### Variables de Entorno
Crear archivo `.env` con:
```
DEBUG=True
SECRET_KEY=tu-clave-secreta-de-desarrollo
DATABASE_URL=postgresql://...
```
