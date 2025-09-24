# -*- coding: utf-8 -*-
"""
Utilidades y funciones auxiliares

Este módulo contiene funciones de utilidad para validación,
formateo y operaciones comunes en la aplicación.

Autor: YouTube Downloader
Fecha: 2025
"""

import re
import os
import json
import threading
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import urlparse, parse_qs
import tkinter as tk
from tkinter import filedialog


def is_valid_youtube_url(url: str) -> bool:
    """
    Validar si una URL es válida de YouTube
    
    Args:
        url (str): URL a validar
        
    Returns:
        bool: True si la URL es válida
    """
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
        r'(?:https?://)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/channel/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/c/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/@[\w-]+',
    ]
    
    return any(re.match(pattern, url) for pattern in patterns)


def extract_video_id(url: str) -> Optional[str]:
    """
    Extraer ID de video de una URL de YouTube
    
    Args:
        url (str): URL de YouTube
        
    Returns:
        str: ID del video o None si no se encuentra
    """
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_playlist_id(url: str) -> Optional[str]:
    """
    Extraer ID de playlist de una URL de YouTube
    
    Args:
        url (str): URL de YouTube
        
    Returns:
        str: ID de la playlist o None si no se encuentra
    """
    match = re.search(r'list=([0-9A-Za-z_-]+)', url)
    return match.group(1) if match else None


def format_duration(seconds: int) -> str:
    """
    Formatear duración en segundos a formato HH:MM:SS
    
    Args:
        seconds (int): Duración en segundos
        
    Returns:
        str: Duración formateada
    """
    if not seconds:
        return "00:00"
        
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def format_file_size(size_bytes: int) -> str:
    """
    Formatear tamaño de archivo en bytes a formato legible
    
    Args:
        size_bytes (int): Tamaño en bytes
        
    Returns:
        str: Tamaño formateado
    """
    if size_bytes == 0:
        return "0 B"
        
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
        
    return f"{size_bytes:.1f} {size_names[i]}"


def sanitize_filename(filename: str) -> str:
    """
    Limpiar nombre de archivo de caracteres no válidos
    
    Args:
        filename (str): Nombre de archivo original
        
    Returns:
        str: Nombre de archivo limpio
    """
    # Caracteres no permitidos en nombres de archivo
    invalid_chars = r'<>:"/\\|?*'
    
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limitar longitud
    if len(filename) > 200:
        filename = filename[:200]
        
    return filename.strip()


def get_folder_size(folder_path: Path) -> int:
    """
    Calcular el tamaño total de una carpeta
    
    Args:
        folder_path (Path): Ruta de la carpeta
        
    Returns:
        int: Tamaño total en bytes
    """
    total_size = 0
    
    try:
        for file_path in folder_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
    except (OSError, PermissionError):
        pass
        
    return total_size


def count_files_by_extension(folder_path: Path) -> Dict[str, int]:
    """
    Contar archivos por extensión en una carpeta
    
    Args:
        folder_path (Path): Ruta de la carpeta
        
    Returns:
        Dict[str, int]: Diccionario con conteo por extensión
    """
    extensions = {}
    
    try:
        for file_path in folder_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                extensions[ext] = extensions.get(ext, 0) + 1
    except (OSError, PermissionError):
        pass
        
    return extensions


def select_folder() -> Optional[str]:
    """
    Abrir diálogo para seleccionar carpeta
    
    Returns:
        str: Ruta de la carpeta seleccionada o None
    """
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    folder_path = filedialog.askdirectory(
        title="Seleccionar carpeta de destino"
    )
    
    root.destroy()
    return folder_path if folder_path else None


def select_file(filetypes: List[tuple] = None) -> Optional[str]:
    """
    Abrir diálogo para seleccionar archivo
    
    Args:
        filetypes (List[tuple]): Tipos de archivo permitidos
        
    Returns:
        str: Ruta del archivo seleccionado o None
    """
    root = tk.Tk()
    root.withdraw()
    
    if not filetypes:
        filetypes = [("Todos los archivos", "*.*")]
    
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo",
        filetypes=filetypes
    )
    
    root.destroy()
    return file_path if file_path else None


def create_desktop_shortcut(name: str, target: str, icon: str = None):
    """
    Crear acceso directo en el escritorio (Windows)
    
    Args:
        name (str): Nombre del acceso directo
        target (str): Ruta del archivo objetivo
        icon (str): Ruta del icono (opcional)
    """
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, f"{name}.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        
        if icon:
            shortcut.IconLocation = icon
            
        shortcut.save()
        
    except ImportError:
        pass  # Módulos no disponibles


def load_json_file(file_path: Path) -> Optional[Dict]:
    """
    Cargar archivo JSON de forma segura
    
    Args:
        file_path (Path): Ruta del archivo JSON
        
    Returns:
        Dict: Contenido del archivo o None si hay error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return None


def save_json_file(data: Dict, file_path: Path) -> bool:
    """
    Guardar datos en archivo JSON
    
    Args:
        data (Dict): Datos a guardar
        file_path (Path): Ruta del archivo
        
    Returns:
        bool: True si se guardó correctamente
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (PermissionError, OSError):
        return False


class ThreadSafeCounter:
    """Contador thread-safe para operaciones concurrentes"""
    
    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()
    
    def increment(self) -> int:
        with self._lock:
            self._value += 1
            return self._value
    
    def decrement(self) -> int:
        with self._lock:
            self._value -= 1
            return self._value
    
    @property
    def value(self) -> int:
        with self._lock:
            return self._value
    
    def reset(self):
        with self._lock:
            self._value = 0


class SettingsManager:
    """Manejador de configuraciones de usuario"""
    
    def __init__(self, settings_file: Path):
        self.settings_file = settings_file
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict:
        """Cargar configuraciones desde archivo"""
        default_settings = {
            'download_path': str(Path.home() / 'Downloads' / 'YouTube'),
            'default_format': 'mp3',
            'default_quality': '192',
            'skip_existing': True,
            'create_playlist_folders': True,
            'embed_thumbnails': True,
            'save_metadata': True,
            'max_concurrent_downloads': 3,
            'theme': 'clam'
        }
        
        saved_settings = load_json_file(self.settings_file)
        if saved_settings:
            default_settings.update(saved_settings)
            
        return default_settings
    
    def save_settings(self) -> bool:
        """Guardar configuraciones actuales"""
        return save_json_file(self.settings, self.settings_file)
    
    def get(self, key: str, default=None):
        """Obtener valor de configuración"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Establecer valor de configuración"""
        self.settings[key] = value
    
    def reset_to_defaults(self):
        """Restablecer configuraciones por defecto"""
        self.settings_file.unlink(missing_ok=True)
        self.settings = self._load_settings()