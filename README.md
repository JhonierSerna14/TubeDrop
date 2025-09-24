# YouTube Downloader 🎵

Un descargador profesional y moderno para videos y playlists de YouTube con interfaz gráfica intuitiva.

## ✨ Características Principales

- **🎯 Descarga Inteligente**: Videos individuales y playlists completas
- **🎵 Múltiples Formatos de Audio**: MP3, FLAC, WAV, M4A, OGG
- **🎬 Múltiples Formatos de Video**: MP4, WebM, MKV, AVI
- **🔧 Calidades Personalizables**: Desde 128kbps hasta 4K
- **🖥️ Interfaz Moderna**: Diseño intuitivo con tema profesional
- **🔄 Detección de Duplicados**: Evita descargas innecesarias
- **📊 Progreso Detallado**: Barra de progreso en tiempo real
- **⚙️ Configuración Avanzada**: Personalización completa
- **📜 Historial de Descargas**: Gestión de archivos descargados
- **💻 Multiplataforma**: Windows, macOS, Linux

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.7 o superior
- pip (incluido con Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone https://github.com/JhonierSerna14/TubeDrop.git
   cd TubeDrop
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**
   ```bash
   python main.py
   ```

## 📖 Uso

### Interfaz Gráfica (Recomendado)
```bash
python main.py
```
- Abre la interfaz gráfica moderna
- Pega la URL de YouTube
- Selecciona formato y calidad
- ¡Descarga!

### Línea de Comandos
```bash
# Descargar un video
python main.py --cli "https://youtube.com/watch?v=VIDEO_ID"

# Descargar playlist en MP4 720p
python main.py --cli "PLAYLIST_URL" --format mp4 --quality 720p

# Especificar carpeta de destino
python main.py --cli "VIDEO_URL" --output "C:/Descargas/Musica"
```

### Opciones de Línea de Comandos
- `--cli URL`: Ejecutar en modo consola
- `--format FORMAT`: mp3, flac, wav, mp4, webm, mkv, avi
- `--quality QUALITY`: 128, 192, 256, 320, 480p, 720p, 1080p, etc.
- `--output PATH`: Carpeta de destino
- `--help`: Mostrar ayuda completa

## 🎛️ Formatos Soportados

### Audio
| Formato | Descripción | Calidades |
|---------|-------------|-----------|
| MP3 | Más compatible | 128, 192, 256, 320 kbps |
| FLAC | Calidad sin pérdida | Mejor disponible |
| WAV | Sin compresión | Mejor disponible |
| M4A | Calidad alta | 128, 192, 256, 320 kbps |
| OGG | Código abierto | 128, 192, 256, 320 kbps |

### Video
| Formato | Descripción | Calidades |
|---------|-------------|-----------|
| MP4 | Más compatible | 144p - 4K |
| WebM | Código abierto | 144p - 4K |
| MKV | Contenedor versátil | 144p - 4K |
| AVI | Clásico compatible | 144p - 1080p |

## 🔧 Configuración Avanzada

La aplicación permite personalizar:

- **Rutas de Descarga**: Carpetas personalizadas
- **Formatos por Defecto**: Tu formato preferido
- **Calidad Predeterminada**: Calidad automática
- **Opciones de Archivos**: Metadatos, miniaturas
- **Comportamiento**: Saltar duplicados, carpetas de playlist

## 📁 Estructura del Proyecto

```
YouTube-Downloader/
├── src/
│   ├── core/           # Motor de descarga
│   │   ├── config.py   # Configuraciones
│   │   └── downloader.py # Lógica principal
│   ├── gui/            # Interfaz gráfica
│   │   └── main_window.py # Ventana principal
│   └── utils/          # Utilidades
│       └── helpers.py  # Funciones auxiliares
├── descargas/          # Carpeta de descargas (auto-creada)
├── logs/              # Registros (auto-creada)
├── main.py            # Archivo principal
├── requirements.txt   # Dependencias
└── README.md         # Este archivo
```

## 🤝 Funcionalidades Avanzadas

### Detección Inteligente
- Detecta automáticamente si es video o playlist
- Identifica archivos ya descargados
- Evita descargas duplicadas

### Gestión de Archivos
- Organización automática por carpetas
- Nombres de archivo seguros
- Metadatos embebidos
- Miniaturas incluidas

### Interfaz Moderna
- Diseño responsivo
- Tema profesional
- Atajos de teclado
- Arrastrar y soltar URLs

## 🛠️ Solución de Problemas

### Error: "No module named 'yt_dlp'"
```bash
pip install yt-dlp
```

### Error: FFmpeg no encontrado
- **Windows**: Descargar desde https://ffmpeg.org/
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### Problema con URLs
- Verifica que la URL sea de YouTube válida
- Asegúrate de que el video/playlist sea público
- Intenta con una URL diferente

### Velocidad Lenta
- Verifica tu conexión a internet
- Prueba con una calidad menor
- Cierra otras aplicaciones que usen internet

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

¿Necesitas ayuda? 

1. **Revisa las preguntas frecuentes** arriba
2. **Verifica los logs** en la carpeta `logs/`
3. **Actualiza yt-dlp**: `pip install --upgrade yt-dlp`
4. **Reporta problemas** en GitHub Issues


<div align="center">

⚡ Desarrollado con Python y ❤️

🌟 ¡Dale una estrella si te gusta el proyecto! ⭐

[⬆️ Volver arriba](#youtube-downloader-)

</div>
