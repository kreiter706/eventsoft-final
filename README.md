# Estudiantes:
- Jose Fernando Rave Henao
- Luis Felipe Loaiza
- Yeison Jimenez

# Adso / Eventsoft — Documentación técnica

Este documento describe con detalle técnico el propósito, las tecnologías, la estructura y los procedimientos de configuración, ejecución y despliegue del proyecto. El README está escrito específicamente para este repositorio y refleja su organización real, el uso de Cloudinary para almacenamiento de imágenes y el despliegue en Render.

## Descripción del proyecto

Adso (también referenciado en el proyecto como `Eventsoft`) es una aplicación web desarrollada con Django orientada a la gestión integral de eventos: preinscripción, inscripción, administración de eventos, evaluación, certificación y gestión de usuarios con distintos roles (superadministrador, administrador de eventos, evaluador, expositor y asistente). El sistema incluye módulos para carga y gestión de imágenes asociadas a eventos mediante Cloudinary, manejo de usuarios personalizados y funciones administrativas para inicializar cuentas de superusuario.

### Roles del sistema

**Asistente**
Usuario que participa en el evento como público. Su función es observar, escuchar o asistir a las actividades programadas, sin intervenir activamente ni realizar exposiciones.

**Expositor**  
Usuario encargado de presentar, mostrar o explicar un proyecto, producto o tema durante el evento, ya sea mediante una charla, stand o demostración.

**Evaluador**  
Usuario responsable de evaluar a los expositores, asignando calificaciones y proporcionando retroalimentación de acuerdo con los criterios definidos por el sistema.

**Administrador de Eventos**  
Usuario encargado de la creación, gestión y supervisión de los eventos, asegurando su correcto desarrollo, organización y cumplimiento de los objetivos establecidos.

**Súper Administrador**  
Usuario con el nivel más alto de privilegios dentro del sistema. Tiene control total sobre la plataforma, incluyendo la administración de usuarios, eventos y configuraciones generales, garantizando el correcto funcionamiento del sistema.

## Tecnologías utilizadas

- Python 3.x (indicaciones en `render.yaml` sugieren compatibilidad con versiones recientes)
- Django 5.x
- Gunicorn (servidor WSGI para producción)
- PostgreSQL (sugerido para despliegue en Render; el repositorio incluye `psycopg2-binary`)
- Cloudinary + `django-cloudinary-storage` para almacenamiento y CDN de archivos media
- whitenoise (servir staticfiles en producción)
- python-dotenv (carga de variables de entorno en desarrollo)

Dependencias principales están listadas en `requirements.txt`.

## Estructura del proyecto (archivo por archivo / carpeta por carpeta)

Raíz del proyecto:

- `manage.py` — wrapper de comandos de Django. Punto de entrada para migraciones, ejecución del servidor, creación de superusuarios y tareas administrativas.
- `settings.py` — configuración principal de Django. Contiene configuraciones de `INSTALLED_APPS`, `STATICFILES_DIRS`, configuración de correo por variables de entorno y (en este repositorio) integración con Cloudinary mediante variables de entorno.
- `wsgi.py`, `asgi.py` — puntos de entrada WSGI/ASGI para servir la aplicación en producción y entornos compatibles.
- `requirements.txt` — lista de paquetes y versiones necesarias para correr la aplicación. Contiene, entre otros, `Django`, `gunicorn`, `cloudinary`, `django-cloudinary-storage`, `psycopg2-binary`.
- `Procfile` — define los procesos a ejecutar en plataformas tipo Heroku/Render; incluye comandos `release` (migraciones + collectstatic) y `web` (gunicorn).
- `render.yaml` — definición de servicio para Render: comandos de build, startCommand y variables de ejemplo (ej.: `PYTHON_VERSION`, `ENVIRONMENT`).
- `db.sqlite3`, `db.sqbpro` — bases de datos locales / archivos de respaldo (útil solo en desarrollo local; en producción se recomienda PostgreSQL u otra BD gestionada).
- Scripts administrativos y utilidades:
  - `create_superadmin.py`, `create_superuser.py`, `create_admin.py`, `reset_superadmin.py`, `reset_password.py`, `setup_admin.py` — scripts para crear/gestionar cuentas privilegiadas y restaurar contraseñas (uso manual/administrativo).
  - `check_db.py`, `cleanup_images.py`, `cloudinary_list.py`, `test_cloudinary.py` — utilidades relacionadas con base de datos e imágenes; `cloudinary_list.py` es un script para listar recursos subidos a Cloudinary bajo un prefijo (útil para auditoría y mantenimiento).

Carpetas principales (aplicaciones Django):

- `documentos/`
  - `admin.py` — registro de modelos en el admin.
  - `models.py` — modelos relacionados con documentos (contratos, certificados, etc.).
  - `views.py`, `tests.py` — vistas y pruebas específicas de la app.
  - `migrations/` — migraciones de la app.

- `evaluaciones/`
  - Contiene lógica de formularios y modelos para evaluación de exposiciones (calificaciones, criterios, etc.).

- `eventos/`
  - `models.py` — modelos de eventos (evento, imagenes_eventos, inscripciones, etc.).
  - `views.py` — vistas públicas y administrativas para crear/editar eventos.
  - `forms.py`, `forms_grupo.py` — formularios para creación y edición de eventos, grupos y carga de imágenes.
  - `signals.py` — señales Django para acciones en modelos (por ejemplo: generación de certificados, notificaciones o tareas asíncronas en cambios de estado).
  - `utils.py`, `certificados*.py` — utilidades para generación de documentos y certificados.
  - `templates/`, `static/` — recursos de plantilla y estáticos específicos de la app.

- `inscripciones/`
  - Gestión de inscripciones a eventos, señales relacionadas y vistas de participación.

- `proyectos/`
  - Modelos y vistas relacionadas con proyectos presentados en eventos (posiblemente exhibiciones o trabajos académicos).

- `usuarios/`
  - `models.py` — modelo de usuario extendido (posibles perfiles, códigos de acceso, etc.).
  - `backends.py` — backend(s) de autenticación personalizados.
  - `forms.py`, `custom_auth_form.py` — formularios de registro/login y formulario de autenticación personalizado.
  - `signals.py` — acciones que ocurren al crear/actualizar usuarios (p. ej. enviar notificaciones, crear perfiles asociados).
  - `management/` — comandos personalizados del manage.py relacionados con usuarios.

Otras carpetas y ficheros:

- `media/imagenes_eventos/` — localmente usado para almacenamiento de uploads antes de integrar Cloudinary. En producción, la media se gestiona a través de Cloudinary.
- `static/` — CSS y otros ficheros estáticos globales.
- `templates/` — plantillas globales (p. ej. `base.html`, `dashboard.html`, plantillas de `registration/`).
- `tests_*` y `tests.py` dispersos — pruebas unitarias y de integración (hay tests en la raíz y en varias apps: `test_upload.py`, `test_web_form_post.py`, `test_signals.py`, etc.).

## Contrato mínimo (inputs / outputs / responsabilidades)

- Inputs: peticiones HTTP desde el navegador / API, subida de ficheros (imágenes), variables de entorno para configuración.
- Outputs: páginas HTML, archivos estáticos, URLs de imágenes servidas via Cloudinary, correos electrónicos generados por la app.
- Errores comunes: variables de entorno faltantes (SECRET_KEY, CLOUDINARY_*), migraciones pendientes, falta de dependencias instaladas.

## Configuración del entorno (variables importantes)

Se recomienda usar un archivo `.env` en desarrollo (no subido al repositorio). Variables claves:

- `SECRET_KEY` — clave secreta de Django.
- `DEBUG` — True/False en desarrollo/producción.
- Configuración de base de datos:
  - `DATABASE_URL` o `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (según configuración usada localmente).
- Correo (según `settings.py`):
  - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`.
- Cloudinary (obligatorias para manejo de media en producción):
  - `CLOUDINARY_CLOUD_NAME`
  - `CLOUDINARY_API_KEY`
  - `CLOUDINARY_API_SECRET`

Adicionales para Render (ejemplos en `render.yaml`):

- `PYTHON_VERSION` — versión de Python a usar en el servicio.
- `ENVIRONMENT` — p. ej. `production`.

IMPORTANTE: Nunca subir secretos reales al repositorio. Usar variables de entorno en Render y un `.env` local para desarrollo.

## Instalación y ejecución (desarrollo local)

1. Clonar el repositorio:

   git clone <url-del-repo>

2. Crear y activar entorno virtual:

   python -m venv venv
   venv\Scripts\activate

3. Instalar dependencias:

   pip install -r requirements.txt

4. Crear `.env` en la raíz con las variables mínimas (ver sección anterior). Ejemplo mínimo:

   SECRET_KEY=clave_local_de_prueba
   DEBUG=True
   CLOUDINARY_CLOUD_NAME=tu_cloud_name
   CLOUDINARY_API_KEY=tu_api_key
   CLOUDINARY_API_SECRET=tu_api_secret

5. Ejecutar migraciones y crear superusuario:

   python manage.py migrate
   python manage.py createsuperuser

6. Ejecutar servidor en desarrollo:

   python manage.py runserver

7. Pruebas rápidas relacionadas con Cloudinary:

   - Usar `cloudinary_list.py` para listar recursos subidos (requiere variables de entorno).
   - Ejecutar pruebas unitarias con `python -m pytest` o `python manage.py test` (según preferencia; el repositorio incluye tests).

## Manejo de imágenes con Cloudinary

Este proyecto integra Cloudinary para el almacenamiento de archivos `media` y para servir imágenes desde una CDN. Elementos clave:

- Paquetes: `cloudinary` y `django-cloudinary-storage` (ya presentes en `requirements.txt`).
- Variables de entorno: `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`.
- Flujo de trabajo:
  1. El formulario de creación/edición de eventos permite subir imágenes.
  2. Django/`django-cloudinary-storage` sube la imagen a Cloudinary y guarda la `public_id`/URL en el modelo.
  3. En plantillas se usan las URLs proporcionadas por Cloudinary para mostrar imágenes. Esto evita depender del sistema de archivos local en producción.

Scripts de utilidad:

- `cloudinary_list.py` — lista recursos bajo el prefijo `imagenes_eventos/` en Cloudinary. Útil para auditoría y mantenimiento de recursos.
- `cleanup_images.py` — (si existe) puede contener rutinas para limpieza/normalización de rutas de imágenes.

Buenas prácticas:

- En producción no almacenar archivos media en el disco del servidor (Render borra volúmenes efímeros). Usar Cloudinary o similar.
- Configurar en Render las variables `CLOUDINARY_*` con valores de la cuenta Cloudinary.

## Despliegue en Render

Este proyecto incluye un `render.yaml` y `Procfile` con las instrucciones recomendadas para desplegar en Render.

Pasos generales para desplegar en Render:

1. Crear un nuevo Web Service en Render y conectar el repositorio.
2. En la configuración del servicio (Environment), agregar las variables de entorno necesarias: al menos `SECRET_KEY`, `DEBUG=False`, `CLOUDINARY_*`, `DATABASE_URL` (si usa Postgres) y las credenciales de correo si se requiere envío de correos.
3. El `render.yaml` y/o `Procfile` define los comandos de build y start. Ejemplos encontrados en este repositorio:

   - `buildCommand`: instala dependencias, aplica migraciones y ejecuta `collectstatic`.
   - `startCommand`: `gunicorn wsgi:application --bind 0.0.0.0:$PORT --timeout 120`.

4. Render puede ejecutar un `release` command (en `Procfile`) que corre migraciones y `collectstatic` antes de iniciar el servicio.

5. Verificar logs (Render Dashboard) ante errores de migración o de conectividad con Cloudinary.

Notas específicas encontradas en el repo:

- `Procfile` contiene una línea `release: python manage.py migrate --noinput && python manage.py collectstatic --noinput` y un `web:` con `gunicorn`.
- `render.yaml` incluye ejemplos de `buildCommand` y `startCommand`, y muestra variables de ejemplo (`PYTHON_VERSION`, `ENVIRONMENT`). También aparece una sección de `databases` con un nombre `adso-db` (esto sugiere que la configuración prevista es Postgres gestionado por Render, pero la conexión final depende de la variable `DATABASE_URL` o credenciales proporcionadas en el servicio).

## Pruebas y validación

- Hay múltiples archivos de pruebas en la raíz y dentro de las apps (`test_cloudinary.py`, `test_upload.py`, `test_signals.py`, etc.). Ejecutar:

  python manage.py test

  o con pytest si se prefiere.

## Mantenimiento y utilidades administrativas

- Scripts de creación/reset de usuarios (`create_superadmin.py`, `reset_superadmin.py`) facilitan la inicialización de cuentas administrativas.
- Mantener `requirements.txt` actualizado; al adicionar paquetes relacionados con Cloudinary o correo, actualizar allí y probar localmente.

## Seguridad y buenas prácticas

- No commitear archivos `.env` ni credenciales.
- Usar `DEBUG=False` en producción y revisar `ALLOWED_HOSTS` en `settings.py`.
- Rotar claves de Cloudinary y otros secretos si se filtran.

## Archivos importantes a revisar al contribuir

- `settings.py` — revisar cambios en el pipeline de configuración (bases de datos, storage, correo).
- `eventos/models.py` — cambios en el esquema de eventos / imágenes.
- `usuarios/models.py` y `usuarios/backends.py` — cambios en autenticación/roles.


