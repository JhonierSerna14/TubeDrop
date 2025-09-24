# -*- coding: utf-8 -*-
"""
Configuración principal de YouTube Downloader

Este módulo contiene todas las configuraciones y constantes
utilizadas en la aplicación.

Autor: YouTube Downloader
Fecha: 2025
"""

import os
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).parent.parent.parent
DOWNLOADS_DIR = BASE_DIR / "descargas"
ASSETS_DIR = BASE_DIR / "assets"
LOGS_DIR = BASE_DIR / "logs"

# Crear directorios si no existen
DOWNLOADS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Configuración de descarga por defecto
DEFAULT_DOWNLOAD_CONFIG = {
    'outtmpl': str(DOWNLOADS_DIR / '%(uploader)s' / '%(title)s.%(ext)s'),
    'format': 'bestaudio/best',
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        },
        {
            'key': 'EmbedThumbnail',
        },
        {
            'key': 'FFmpegMetadata',
        },
    ],
    'writethumbnail': True,
    'writeinfojson': True,
    'noplaylist': False,
    'ignoreerrors': True,
    'overwrites': False,
}

# Formatos de audio soportados
AUDIO_FORMATS = {
    'mp3': {'codec': 'mp3', 'quality': '192'},
    'flac': {'codec': 'flac', 'quality': 'best'},
    'wav': {'codec': 'wav', 'quality': 'best'},
    'm4a': {'codec': 'm4a', 'quality': '192'},
    'ogg': {'codec': 'ogg', 'quality': '192'}
}

# Formatos de video soportados
VIDEO_FORMATS = {
    'mp4': 'best[ext=mp4]',
    'webm': 'best[ext=webm]',
    'mkv': 'best[ext=mkv]',
    'avi': 'best[ext=avi]'
}

# Calidades de video
VIDEO_QUALITIES = {
    '144p': 'worst[height<=144]',
    '240p': 'best[height<=240]',
    '360p': 'best[height<=360]',
    '480p': 'best[height<=480]',
    '720p': 'best[height<=720]',
    '1080p': 'best[height<=1080]',
    '1440p': 'best[height<=1440]',
    '2160p': 'best[height<=2160]',
    'Mejor': 'best'
}

# Configuración de la interfaz
UI_CONFIG = {
    'window_size': (900, 700),
    'min_size': (600, 500),
    'theme': 'clam',
    'colors': {
        'primary': '#2196F3',
        'secondary': '#FFC107',
        'success': '#4CAF50',
        'error': '#F44336',
        'background': '#FAFAFA'
    }
}

# Configuración de logging
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'simple': {
            'format': '%(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': str(LOGS_DIR / 'youtube_downloader.log'),
            'formatter': 'detailed',
            'level': 'DEBUG'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO'
        }
    },
    'loggers': {
        'youtube_downloader': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}
