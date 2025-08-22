# 🤟 Detector de Lenguaje de Señas - Django Web App

## 📋 Instrucciones de Instalación y Ejecución

### 1. Navegar al directorio de Django
```cmd
cd django_app
```

### 2. Instalar dependencias (opcional - ya están en tu .venv)
```cmd
pip install -r requirements.txt
```

### 3. Realizar migraciones de Django
```cmd
python manage.py makemigrations
python manage.py migrate
```

### 4. Ejecutar el servidor de desarrollo
```cmd
python manage.py runserver
```

### 5. Abrir en navegador
- Ve a: http://127.0.0.1:8000
- O: http://localhost:8000

## 🚀 Características de la App Web

✅ **Interfaz web moderna** con gradientes y efectos glassmorphism
✅ **Detección en tiempo real** usando YOLO + MediaPipe
✅ **Streaming de video** directo en el navegador
✅ **Control de cámara** (iniciar/detener) desde la web
✅ **Visualización en vivo** de letra detectada y confianza
✅ **Grid del alfabeto** que resalta la letra actual
✅ **Estadísticas en tiempo real** (FPS, tiempo activo, contadores)
✅ **Diseño responsive** para móvil y desktop
✅ **No requiere OpenCV window** - todo en el navegador

## 🔧 Estructura del Proyecto

```
django_app/
├── manage.py                   # Script principal de Django
├── requirements.txt           # Dependencias
├── sign_language_detector/    # Configuración principal
│   ├── settings.py           # Configuración Django
│   ├── urls.py              # URLs principales
│   └── wsgi.py              # WSGI para producción
└── detector/                 # App de detección
    ├── detector_service.py   # Tu código YOLO+MediaPipe adaptado
    ├── views.py             # Vistas Django (API endpoints)
    ├── urls.py              # URLs de la app
    └── templates/
        └── index.html       # Interfaz web principal
```

## 🎮 Cómo Usar

1. **Abrir la página web** en tu navegador
2. **Clic en "Iniciar Detección"** para activar la cámara
3. **Mostrar señas** con tu mano frente a la cámara
4. **Ver resultados** en tiempo real:
   - Letra detectada (grande)
   - Porcentaje de confianza
   - Grid alfabético resaltado
   - Estadísticas en vivo
5. **Clic en "Detener"** para parar la detección

## 🔧 Personalización

- **Confianza mínima**: Cambiar en `detector_service.py` línea con `conf=0.5`
- **Resolución**: Modificar en `detector_service.py` las líneas `CAP_PROP_FRAME_WIDTH/HEIGHT`
- **Colores/Estilos**: Editar CSS en `templates/index.html`
- **Suavizado**: Ajustar `maxlen` del deque en `detector_service.py`

## ⚠️ Notas Importantes

- Asegúrate de que el modelo esté en: `../runs/detect/train/weights/best.pt`
- La cámara se detecta automáticamente (índice 0)
- El servidor debe ejecutarse desde la carpeta `django_app`
- Usa Ctrl+C para detener el servidor Django

## 🚨 Solución de Problemas

**Error "No module named 'django'":**
```cmd
pip install django
```

**Error de modelo no encontrado:**
- Verifica que `runs/detect/train/weights/best.pt` existe
- Ajusta la ruta en `settings.py` si es necesario

**Cámara no funciona:**
- Verifica permisos de cámara en el navegador
- Revisa que no haya otra app usando la cámara

**Error de puertos:**
```cmd
python manage.py runserver 8001
```
