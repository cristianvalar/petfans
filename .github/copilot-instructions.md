# PetFans - Instrucciones de Desarrollo

> **Nota Importante**: Este archivo debe actualizarse cada vez que se realicen cambios significativos en la arquitectura, patrones de desarrollo, o flujos de trabajo del proyecto. Mantener estas instrucciones actualizadas garantiza la productividad inmediata al trabajar en el proyecto.

> **📝 IMPORTANTE**: Cada vez que se implemente una nueva funcionalidad o se realice un cambio arquitectónico significativo, **DEBES ACTUALIZAR** el archivo `FEATURES.md` en la raíz del proyecto. Este archivo sirve como documentación de estado del proyecto y debe reflejar siempre las capacidades actuales del sistema.

## Visión General de la Arquitectura

PetFans es una API REST de Django para gestión de mascotas con autenticación basada en email. La aplicación usa una **arquitectura de una sola app** con toda la lógica de negocio en la app `core`.

### Componentes Clave
- **Modelos**: Pet, Species, Breed, PetVaccine, VaccineReminder, UserProfile, LoginCode
- **Autenticación**: Login por email con códigos temporales (sin contraseñas)
- **Funciones Automáticas**: Los recordatorios de vacunas se crean automáticamente al guardar PetVaccine con `next_dose_date`
- **Comandos de Gestión**: `send_vaccine_reminders` para notificaciones masivas por email

## Patrones Críticos

### 1. Arquitectura de Settings
```
petfans/settings/
├── base.py      # Configuración compartida
├── local.py     # Desarrollo (importa base)
└── prod.py      # Producción (importa base)
```
**Siempre especifica settings**: `--settings=petfans.settings.local` para comandos de desarrollo.

### 2. Sistema Automático de Recordatorios
Cuando se guarda un `PetVaccine` con `next_dose_date`, el modelo crea automáticamente instancias de `VaccineReminder` para todos los dueños de la mascota (7 días y 1 día antes). **Nunca crear recordatorios manualmente** - se manejan con `VaccineReminder.create_automatic_reminders()`.

### 3. Claves Primarias UUID
El modelo `Pet` usa claves primarias UUID por seguridad. Otros modelos usan PKs enteros estándar.

### 4. Relaciones Multi-Dueño
Las mascotas tienen `ManyToManyField` a User vía `owners`. Siempre considera múltiples dueños al crear notificaciones o verificar permisos.

### 5. Seguridad y Variables de Entorno
**CRÍTICO**: Todos los datos sensibles (claves API, contraseñas de base de datos, SECRET_KEY, credenciales de email) DEBEN estar definidos en variables de entorno. Nunca hardcodear credenciales en el código. Usar archivo `.env` para desarrollo local y configurar variables de entorno apropiadas en producción.

## Flujo de Desarrollo

### Configuración del Entorno
1. Crear archivo `.env` con variables requeridas (ver README.md)
2. Usar Docker: `docker-compose up --build` (preferido)
3. O local: `pip install -r requirements.txt` + configurar PostgreSQL

### Comandos Clave
```bash
# Servidor de desarrollo (con Docker)
docker-compose up

# Desarrollo local
python manage.py runserver --settings=petfans.settings.local

# Enviar recordatorios de vacunas pendientes
python manage.py send_vaccine_reminders --dry-run

# Migraciones
python manage.py makemigrations --settings=petfans.settings.local
python manage.py migrate --settings=petfans.settings.local
```

### Evolución del Esquema de Base de Datos
El proyecto ha evolucionado a través de 9 migraciones. Cambios clave:
- `0007`: Renombrado de `Vaccine` a `PetVaccine`
- `0008`: Agregado sistema `VaccineReminder`
- `0009`: Arregladas restricciones null de fecha de recordatorio

## Patrones de API

### Flujo de Autenticación
1. POST `/auth/request-code/` con email → envía código de 6 dígitos
2. POST `/auth/verify-code/` con email+código → retorna tokens JWT
3. Usar tokens JWT para endpoints autenticados

### Estructura de ViewSets
Todos los modelos principales usan `ModelViewSet` con routers DRF:
- `/species/`, `/breeds/`, `/pets/`, `/vaccines/`, `/vaccine-reminders/`

## Convenciones de Subida de Archivos
- Fotos de mascotas: `media/pets/`
- Avatares de usuarios: `media/avatars/`
- Siempre manejar campos de imagen opcionales con `blank=True, null=True`

## Al Agregar Funcionalidades

1. **Modelos**: Seguir convenciones de nomenclatura existentes (campos verbose_name en español)
2. **Recordatorios**: Aprovechar patrones existentes de `VaccineReminder` para nuevos tipos de notificación
3. **Settings**: Agregar variables de entorno tanto en local.py como en prod.py
4. **Tests**: Seguir el patrón en `core/tests.py`
5. **Email**: Usar infraestructura de email existente en comandos de gestión
6. **📝 DOCUMENTACIÓN**: **Actualizar `FEATURES.md`** con la nueva funcionalidad implementada, cambiando su estado de ❌ a ✅, o agregándola si no existía

## Checklist de Implementación de Nueva Funcionalidad

Cuando implementes una nueva funcionalidad, sigue este checklist:

- [ ] Implementar la funcionalidad (modelo, serializer, viewset, etc.)
- [ ] Crear tests unitarios
- [ ] Actualizar admin.py si es necesario
- [ ] Crear/aplicar migraciones
- [ ] Actualizar `FEATURES.md` con el nuevo estado
- [ ] Si es un cambio arquitectónico, actualizar este archivo (copilot-instructions.md)
- [ ] Actualizar README.md si afecta la instalación o uso
- [ ] Probar en desarrollo
- [ ] Commit con mensaje descriptivo

## Mantenimiento de Documentación

### Archivos que Deben Mantenerse Sincronizados:
1. **`FEATURES.md`**: Estado actual de funcionalidades (actualizar con cada nueva feature)
2. **`.github/copilot-instructions.md`**: Patrones y convenciones de desarrollo (este archivo)
3. **`README.md`**: Guía de instalación y uso para nuevos desarrolladores
4. **Migraciones**: Documentar cambios significativos en el esquema

### Cuándo Actualizar Cada Archivo:
- **FEATURES.md**: Cada vez que completes una funcionalidad nueva o cambies el estado de una existente
- **copilot-instructions.md**: Cuando cambies patrones de arquitectura, añadas nuevas convenciones o modifiques flujos críticos
- **README.md**: Cuando agregues nuevas dependencias, cambies la configuración del entorno, o modifiques comandos de instalación
