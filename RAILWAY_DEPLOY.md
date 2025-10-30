# 🚀 Guía de Deploy - Railway.app

## ✅ Pre-requisitos completados

Todos los ajustes técnicos ya están listos:
- ✅ Dependencias de producción agregadas
- ✅ WhiteNoise configurado
- ✅ Procfile creado
- ✅ Health check endpoint agregado
- ✅ Variables de entorno documentadas
- ✅ Settings de producción optimizados

## 📝 Paso a Paso - Deploy en Railway

### Paso 1: Commit y Push de los cambios

```bash
git add .
git commit -m "feat: configurar proyecto para deploy en Railway"
git push origin main
```

### Paso 2: Crear cuenta en Railway

1. Ve a https://railway.app
2. Click en "Start a New Project"
3. Login con GitHub (recomendado)

### Paso 3: Crear nuevo proyecto

1. Click en "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Busca y selecciona `cristianvalar/petfans`
4. Railway detectará automáticamente que es un proyecto Django

### Paso 4: Agregar PostgreSQL

1. En tu proyecto, click en "+ New"
2. Selecciona "Database"
3. Selecciona "Add PostgreSQL"
4. Railway creará la base de datos automáticamente

### Paso 5: Configurar variables de entorno

1. Click en tu servicio web (petfans)
2. Ve a la pestaña "Variables"
3. Click en "Raw Editor"
4. Pega las siguientes variables (ajusta los valores):

```env
SECRET_KEY=genera-una-clave-super-segura-de-50-caracteres-minimo-usa-un-generador-online
DEBUG=False
DJANGO_SETTINGS_MODULE=petfans.settings.prod
ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}},${{RAILWAY_STATIC_URL}}

# Email - Usa tus credenciales reales
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=hola@petfans.app
EMAIL_HOST_PASSWORD=tu-app-password-de-gmail-aqui
EMAIL_USE_TLS=True

# CORS - Actualizar después con tu dominio frontend
CORS_ALLOWED_ORIGINS=https://${{RAILWAY_PUBLIC_DOMAIN}}

# PostgreSQL - Railway configura DATABASE_URL automáticamente, no agregar manualmente
```

### Paso 6: Generar SECRET_KEY segura

Opción 1 - En tu terminal local:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Opción 2 - Online:
https://djecrety.ir/

Copia la key generada y pégala en la variable `SECRET_KEY` en Railway.

### Paso 7: Configurar Gmail para emails

Si usas Gmail para enviar emails:

1. Ve a tu cuenta de Google
2. Habilita verificación en 2 pasos
3. Ve a: https://myaccount.google.com/apppasswords
4. Genera una "App Password" para "Correo"
5. Usa esa password en `EMAIL_HOST_PASSWORD`

### Paso 8: Deploy inicial

1. Railway desplegará automáticamente después de configurar variables
2. Verifica los logs en la pestaña "Deployments"
3. Espera a que el deploy termine (1-3 minutos)

### Paso 9: Ejecutar migraciones

Railway ejecutará automáticamente las migraciones gracias al `Procfile`:
```
release: python manage.py migrate --settings=petfans.settings.prod
```

Verifica en los logs que se ejecutaron correctamente.

### Paso 10: Crear superusuario

1. En Railway, ve a tu servicio
2. Click en "Settings"
3. Scroll hasta "Service Settings"
4. En "One-Off Commands", ejecuta:

```bash
python manage.py createsuperuser --settings=petfans.settings.prod
```

Sigue las instrucciones en la consola.

### Paso 11: Collectstatic (archivos estáticos)

Ejecuta este comando en "One-Off Commands":

```bash
python manage.py collectstatic --no-input --settings=petfans.settings.prod
```

### Paso 12: Verificar el deploy

1. Railway te dará una URL como: `https://petfans-production.up.railway.app`
2. Prueba el health check: `https://tu-url.railway.app/health/`
3. Deberías ver: `{"status":"ok","service":"petfans-api","version":"1.0.0"}`
4. Prueba el admin: `https://tu-url.railway.app/admin/`

### Paso 13: Configurar dominio personalizado (opcional)

1. En Railway, ve a "Settings"
2. En "Domains", click "Generate Domain" o "Custom Domain"
3. Si tienes un dominio propio:
   - Agrega un registro CNAME en tu proveedor DNS
   - Apunta a la URL de Railway
   - Actualiza `ALLOWED_HOSTS` con tu dominio

---

## 🧪 Testing en Producción

### Endpoints para probar:

```bash
# Health check
curl https://tu-url.railway.app/health/

# Solicitar código de login
curl -X POST https://tu-url.railway.app/api/auth/request-code/ \
  -H "Content-Type: application/json" \
  -d '{"email":"tu@email.com"}'

# Listar especies
curl https://tu-url.railway.app/api/species/

# Admin
# Visita: https://tu-url.railway.app/admin/
```

---

## 📊 Monitoreo

Railway provee automáticamente:
- ✅ Logs en tiempo real
- ✅ Métricas de uso (CPU, RAM)
- ✅ Historial de deploys
- ✅ Rollback a versiones anteriores

Para ver logs:
1. Click en tu servicio
2. Pestaña "Deployments"
3. Click en el deploy activo
4. Verás logs en tiempo real

---

## 💰 Costos Estimados

**Plan Hobby (Gratis):**
- $5 USD de crédito gratis por mes
- Suficiente para ~500 horas de ejecución
- PostgreSQL incluido
- Perfecto para MVP y pruebas

**Cuando necesites escalar:**
- Plan Developer: $5/mes base + uso
- PostgreSQL: Gratis en plan Hobby, después $5/mes
- Estimado para app pequeña: $5-15/mes

---

## 🔄 Deploys Futuros

Después del setup inicial, cada vez que hagas push a `main`:

```bash
git add .
git commit -m "feat: nueva funcionalidad"
git push origin main
```

Railway desplegará automáticamente. No necesitas hacer nada más. 🎉

---

## 🆘 Troubleshooting

### Error: "Bad Request (400)"
- Verifica que `ALLOWED_HOSTS` incluya el dominio de Railway
- Usa: `${{RAILWAY_PUBLIC_DOMAIN}}`

### Error: "500 Internal Server Error"
- Revisa los logs en Railway
- Verifica que todas las variables de entorno estén configuradas
- Verifica que SECRET_KEY exista

### Error: "Database connection failed"
- Railway configura DATABASE_URL automáticamente
- No agregues variables POSTGRES_* manualmente si usas DATABASE_URL

### Emails no se envían
- Verifica EMAIL_HOST_PASSWORD (debe ser App Password de Gmail)
- Verifica que EMAIL_USE_TLS=True
- Revisa logs para errores específicos

### Archivos estáticos no cargan
- Ejecuta collectstatic manualmente
- Verifica que WhiteNoise esté en MIDDLEWARE

---

## ✅ Checklist Final

Antes de considerar el deploy completo:

- [ ] Health check responde OK
- [ ] Admin panel accesible
- [ ] Puedes hacer login con superuser
- [ ] API endpoints responden correctamente
- [ ] Emails de login se envían correctamente
- [ ] Archivos estáticos cargan (admin CSS)
- [ ] Puedes crear una mascota desde admin
- [ ] Puedes subir una foto de mascota
- [ ] Variables de entorno configuradas
- [ ] CORS configurado para tu frontend

---

## 🎯 Próximos Pasos

1. **Frontend**: Conectar tu app frontend a la API en Railway
2. **Dominio**: Configurar dominio personalizado
3. **Backups**: Configurar backups automáticos de PostgreSQL
4. **Monitoring**: Agregar Sentry para monitoreo de errores
5. **Media Files**: Migrar a S3/Cloudinary para imágenes
6. **Cache**: Agregar Redis para mejor performance

---

**¿Necesitas ayuda?** Revisa los logs en Railway o contacta soporte.

¡Tu API está lista para producción! 🚀
