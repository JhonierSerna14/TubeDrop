# -*- coding: utf-8 -*-
"""
Motor principal de descarga de YouTube

Este módulo contiene la clase principal para manejar descargas
de videos y playlists de YouTube utilizando yt-dlp.

Autor: YouTube Downloader
Fecha: 2025
"""

import yt_dlp
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable, Union
from concurrent.futures import ThreadPoolExecutor
import threading
import time

from .config import DEFAULT_DOWNLOAD_CONFIG, AUDIO_FORMATS, VIDEO_FORMATS, VIDEO_QUALITIES


class ProgressHook:
    """Hook para capturar el progreso de descarga"""
    
    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback
        self.current_file = ""
        self.total_files = 0
        self.completed_files = 0
        
    def __call__(self, d):
        """Método llamado por yt-dlp para reportar progreso"""
        if d['status'] == 'downloading':
            if self.callback:
                progress_data = {
                    'status': 'downloading',
                    'filename': d.get('filename', ''),
                    'percent': d.get('_percent_str', '0%'),
                    'speed': d.get('_speed_str', ''),
                    'eta': d.get('_eta_str', ''),
                    'total_files': self.total_files,
                    'completed_files': self.completed_files
                }
                self.callback(progress_data)
                
        elif d['status'] == 'finished':
            self.completed_files += 1
            if self.callback:
                progress_data = {
                    'status': 'finished',
                    'filename': d.get('filename', ''),
                    'total_files': self.total_files,
                    'completed_files': self.completed_files
                }
                self.callback(progress_data)


class YouTubeDownloader:
    """
    Clase principal para descargar contenido de YouTube
    
    Maneja descargas de videos individuales, playlists completas,
    y proporciona funcionalidades avanzadas como detección de duplicados,
    descarga en paralelo, y diferentes formatos de salida.
    """
    
    def __init__(self, base_path: str = "./descargas"):
        """
        Inicializar el descargador
        
        Args:
            base_path (str): Ruta base donde guardar las descargas
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.logger = logging.getLogger('youtube_downloader.downloader')
        self.progress_hook = None
        self.is_downloading = False
        self.cancel_download = False
        
    def set_progress_callback(self, callback: Callable):
        """
        Establecer callback para recibir actualizaciones de progreso
        
        Args:
            callback (Callable): Función a llamar con datos de progreso
        """
        self.progress_hook = ProgressHook(callback)
        
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Obtener información de un video sin descargarlo
        
        Args:
            url (str): URL del video o playlist
            
        Returns:
            Dict: Información del video/playlist o None si hay error
        """
        try:
            opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            self.logger.error(f"Error obteniendo info: {e}")
            return None
            
    def get_available_formats(self, url: str) -> Optional[List[Dict]]:
        """
        Obtener formatos disponibles para un video
        
        Args:
            url (str): URL del video
            
        Returns:
            List[Dict]: Lista de formatos disponibles
        """
        info = self.get_video_info(url)
        if info and 'formats' in info:
            return info['formats']
        return None
        
    def _get_downloaded_ids(self, folder_path: Path) -> set:
        """
        Obtener IDs de videos ya descargados en una carpeta
        
        Args:
            folder_path (Path): Ruta de la carpeta a verificar
            
        Returns:
            set: Conjunto de IDs ya descargados
        """
        downloaded_ids = set()
        
        if not folder_path.exists():
            return downloaded_ids
            
        for file in folder_path.glob("*.info.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    video_id = data.get('id')
                    if video_id:
                        downloaded_ids.add(video_id)
            except (json.JSONDecodeError, KeyError, FileNotFoundError):
                continue
                
        return downloaded_ids
        
    def _build_download_options(self, 
                              output_format: str = 'mp3',
                              quality: str = '192',
                              output_path: str = None,
                              playlist_mode: bool = False) -> Dict:
        """
        Construir opciones de descarga personalizadas
        
        Args:
            output_format (str): Formato de salida (mp3, mp4, etc.)
            quality (str): Calidad de descarga
            output_path (str): Ruta de salida personalizada
            playlist_mode (bool): Si es modo playlist
            
        Returns:
            Dict: Opciones configuradas para yt-dlp
        """
        options = DEFAULT_DOWNLOAD_CONFIG.copy()
        
        # Configurar ruta de salida
        if output_path:
            if playlist_mode:
                options['outtmpl'] = f'{output_path}/%(playlist_title)s/%(title)s.%(ext)s'
            else:
                options['outtmpl'] = f'{output_path}/%(title)s.%(ext)s'
        
        # Configurar formato de salida
        if output_format in AUDIO_FORMATS:
            # Configuración para audio
            options['format'] = 'bestaudio/best'
            options['postprocessors'][0]['preferredcodec'] = output_format
            options['postprocessors'][0]['preferredquality'] = quality
        elif output_format in VIDEO_FORMATS:
            # Configuración para video
            options['format'] = VIDEO_FORMATS[output_format]
            # Remover procesadores de audio para video
            options['postprocessors'] = [
                {'key': 'EmbedThumbnail'},
                {'key': 'FFmpegMetadata'}
            ]
            
        # Agregar hook de progreso si existe
        if self.progress_hook:
            options['progress_hooks'] = [self.progress_hook]
            
        return options
        
    def download_single_video(self, 
                            url: str,
                            output_format: str = 'mp3',
                            quality: str = '192',
                            output_path: str = None) -> bool:
        """
        Descargar un video individual
        
        Args:
            url (str): URL del video
            output_format (str): Formato de salida
            quality (str): Calidad de descarga
            output_path (str): Ruta de salida personalizada
            
        Returns:
            bool: True si la descarga fue exitosa
        """
        try:
            self.is_downloading = True
            self.cancel_download = False
            
            options = self._build_download_options(
                output_format, quality, output_path or str(self.base_path)
            )
            
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
                
            self.logger.info(f"Descarga completada: {url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error descargando video: {e}")
            return False
        finally:
            self.is_downloading = False
            
    def download_playlist(self,
                         url: str,
                         output_format: str = 'mp3',
                         quality: str = '192',
                         output_path: str = None,
                         skip_existing: bool = True) -> bool:
        """
        Descargar una playlist completa
        
        Args:
            url (str): URL de la playlist
            output_format (str): Formato de salida
            quality (str): Calidad de descarga
            output_path (str): Ruta de salida personalizada
            skip_existing (bool): Saltar archivos ya descargados
            
        Returns:
            bool: True si la descarga fue exitosa
        """
        try:
            self.is_downloading = True
            self.cancel_download = False
            
            # Obtener información de la playlist
            playlist_info = self.get_video_info(url)
            if not playlist_info:
                return False
                
            playlist_title = playlist_info.get('title', 'Playlist')
            safe_title = yt_dlp.utils.sanitize_filename(playlist_title)
            
            # Configurar ruta de salida
            if not output_path:
                output_path = str(self.base_path)
            playlist_folder = Path(output_path) / safe_title
            
            # Actualizar hook de progreso
            if self.progress_hook:
                entries = playlist_info.get('entries', [])
                self.progress_hook.total_files = len([e for e in entries if e])
                self.progress_hook.completed_files = 0
            
            # Verificar archivos existentes si está habilitado
            urls_to_download = []
            downloaded_ids = set()
            
            if skip_existing:
                downloaded_ids = self._get_downloaded_ids(playlist_folder)
                
            for entry in playlist_info.get('entries', []):
                if entry is None:
                    continue
                    
                video_id = entry.get('id')
                if not skip_existing or video_id not in downloaded_ids:
                    urls_to_download.append(f"https://www.youtube.com/watch?v={video_id}")
                else:
                    self.logger.info(f"Saltando archivo existente: {entry.get('title', video_id)}")
                    
            if not urls_to_download:
                self.logger.info("No hay archivos nuevos para descargar")
                return True
                
            # Configurar opciones de descarga
            options = self._build_download_options(
                output_format, quality, output_path, playlist_mode=True
            )
            
            # Descargar archivos
            with yt_dlp.YoutubeDL(options) as ydl:
                for url_to_download in urls_to_download:
                    if self.cancel_download:
                        break
                    ydl.download([url_to_download])
                    
            self.logger.info(f"Descarga de playlist completada: {len(urls_to_download)} archivos")
            return not self.cancel_download
            
        except Exception as e:
            self.logger.error(f"Error descargando playlist: {e}")
            return False
        finally:
            self.is_downloading = False
            
    def cancel_current_download(self):
        """Cancelar la descarga actual"""
        self.cancel_download = True
        self.logger.info("Cancelación de descarga solicitada")
        
    def search_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Buscar videos en YouTube
        
        Args:
            query (str): Término de búsqueda
            max_results (int): Número máximo de resultados
            
        Returns:
            List[Dict]: Lista de videos encontrados
        """
        try:
            search_url = f"ytsearch{max_results}:{query}"
            opts = {'quiet': True, 'extract_flat': True}
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                search_results = ydl.extract_info(search_url, download=False)
                
            return search_results.get('entries', [])
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda: {e}")
            return []
            
    def get_download_history(self) -> List[Dict]:
        """
        Obtener historial de descargas
        
        Returns:
            List[Dict]: Lista de archivos descargados con metadata
        """
        history = []
        
        for info_file in self.base_path.rglob("*.info.json"):
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                history.append({
                    'title': data.get('title', ''),
                    'uploader': data.get('uploader', ''),
                    'duration': data.get('duration', 0),
                    'upload_date': data.get('upload_date', ''),
                    'url': data.get('webpage_url', ''),
                    'file_path': str(info_file.parent),
                    'download_date': time.ctime(info_file.stat().st_mtime)
                })
                
            except (json.JSONDecodeError, KeyError, FileNotFoundError):
                continue
                
        return sorted(history, key=lambda x: x.get('download_date', ''), reverse=True)