# -*- coding: utf-8 -*-
"""
Funcionalidades adicionales y herramientas extras

Este módulo contiene funcionalidades adicionales como búsqueda,
conversión de formatos, y herramientas de mantenimiento.

Autor: YouTube Downloader
Fecha: 2025
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import threading
import time

from .config import DOWNLOADS_DIR, LOGS_DIR
from .downloader import YouTubeDownloader
from ..utils.helpers import format_file_size, get_folder_size


class SearchManager:
    """Manejador de búsquedas en YouTube"""
    
    def __init__(self, downloader: YouTubeDownloader):
        self.downloader = downloader
        
    def search_videos(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Buscar videos en YouTube
        
        Args:
            query (str): Término de búsqueda
            max_results (int): Número máximo de resultados
            
        Returns:
            List[Dict]: Lista de videos encontrados
        """
        return self.downloader.search_videos(query, max_results)
        
    def get_trending_videos(self, region: str = 'US') -> List[Dict]:
        """
        Obtener videos en tendencia
        
        Args:
            region (str): Código de región (US, ES, MX, etc.)
            
        Returns:
            List[Dict]: Lista de videos en tendencia
        """
        # Esta funcionalidad requiere implementación adicional con la API de YouTube
        return []


class FileManager:
    """Manejador de archivos y limpieza"""
    
    def __init__(self, base_path: Path = DOWNLOADS_DIR):
        self.base_path = Path(base_path)
        
    def get_storage_info(self) -> Dict:
        """
        Obtener información de almacenamiento
        
        Returns:
            Dict: Información de espacio usado
        """
        total_size = get_folder_size(self.base_path)
        file_count = len(list(self.base_path.rglob('*')))
        
        # Contar por tipo de archivo
        extensions = {}
        for file_path in self.base_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                extensions[ext] = extensions.get(ext, 0) + 1
                
        return {
            'total_size': total_size,
            'total_size_formatted': format_file_size(total_size),
            'file_count': file_count,
            'extensions': extensions,
            'folder_count': len([p for p in self.base_path.rglob('*') if p.is_dir()])
        }
        
    def clean_temp_files(self) -> int:
        """
        Limpiar archivos temporales
        
        Returns:
            int: Número de archivos eliminados
        """
        temp_extensions = ['.part', '.tmp', '.temp', '.ytdl']
        deleted_count = 0
        
        for ext in temp_extensions:
            for file_path in self.base_path.rglob(f'*{ext}'):
                try:
                    file_path.unlink()
                    deleted_count += 1
                except (OSError, PermissionError):
                    continue
                    
        return deleted_count
        
    def clean_empty_folders(self) -> int:
        """
        Eliminar carpetas vacías
        
        Returns:
            int: Número de carpetas eliminadas
        """
        deleted_count = 0
        
        # Ordenar por profundidad descendente para eliminar desde las más profundas
        folders = sorted(self.base_path.rglob('*'), key=lambda p: len(p.parts), reverse=True)
        
        for folder in folders:
            if folder.is_dir() and folder != self.base_path:
                try:
                    if not any(folder.iterdir()):  # Carpeta vacía
                        folder.rmdir()
                        deleted_count += 1
                except (OSError, PermissionError):
                    continue
                    
        return deleted_count
        
    def organize_by_date(self) -> int:
        """
        Organizar archivos por fecha de descarga
        
        Returns:
            int: Número de archivos organizados
        """
        organized_count = 0
        
        for file_path in self.base_path.rglob('*.info.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                upload_date = data.get('upload_date', '')
                if upload_date and len(upload_date) >= 8:
                    year = upload_date[:4]
                    month = upload_date[4:6]
                    
                    # Crear estructura de carpetas por año/mes
                    date_folder = self.base_path / year / month
                    date_folder.mkdir(parents=True, exist_ok=True)
                    
                    # Mover archivos relacionados
                    file_base = file_path.stem
                    for related_file in file_path.parent.glob(f'{file_base}.*'):
                        if related_file.suffix != '.info.json':
                            new_path = date_folder / related_file.name
                            if not new_path.exists():
                                shutil.move(str(related_file), str(new_path))
                                organized_count += 1
                                
                    # Mover el archivo info.json
                    new_info_path = date_folder / file_path.name
                    if not new_info_path.exists():
                        shutil.move(str(file_path), str(new_info_path))
                        
            except (json.JSONDecodeError, KeyError, OSError):
                continue
                
        return organized_count


class BatchDownloader:
    """Descargador de lotes con múltiples URLs"""
    
    def __init__(self, downloader: YouTubeDownloader):
        self.downloader = downloader
        self.is_running = False
        self.current_index = 0
        self.total_urls = 0
        self.results = []
        
    def download_from_list(self, urls: List[str], 
                          output_format: str = 'mp3',
                          quality: str = '192',
                          output_path: str = None,
                          progress_callback: Optional[callable] = None) -> List[Dict]:
        """
        Descargar múltiples URLs
        
        Args:
            urls (List[str]): Lista de URLs
            output_format (str): Formato de salida
            quality (str): Calidad
            output_path (str): Ruta de destino
            progress_callback (callable): Callback de progreso
            
        Returns:
            List[Dict]: Resultados de cada descarga
        """
        self.is_running = True
        self.total_urls = len(urls)
        self.current_index = 0
        self.results = []
        
        for i, url in enumerate(urls):
            if not self.is_running:
                break
                
            self.current_index = i + 1
            
            if progress_callback:
                progress_callback({
                    'current': self.current_index,
                    'total': self.total_urls,
                    'url': url,
                    'status': 'starting'
                })
            
            try:
                # Detectar tipo de contenido
                info = self.downloader.get_video_info(url)
                if not info:
                    self.results.append({
                        'url': url,
                        'success': False,
                        'error': 'No se pudo obtener información'
                    })
                    continue
                
                # Descargar según el tipo
                if 'entries' in info:
                    success = self.downloader.download_playlist(
                        url, output_format, quality, output_path
                    )
                else:
                    success = self.downloader.download_single_video(
                        url, output_format, quality, output_path
                    )
                
                self.results.append({
                    'url': url,
                    'success': success,
                    'title': info.get('title', 'Sin título'),
                    'type': 'playlist' if 'entries' in info else 'video'
                })
                
                if progress_callback:
                    progress_callback({
                        'current': self.current_index,
                        'total': self.total_urls,
                        'url': url,
                        'status': 'completed' if success else 'failed'
                    })
                    
            except Exception as e:
                self.results.append({
                    'url': url,
                    'success': False,
                    'error': str(e)
                })
                
        self.is_running = False
        return self.results
        
    def stop(self):
        """Detener descarga de lotes"""
        self.is_running = False
        self.downloader.cancel_current_download()


class QualityAnalyzer:
    """Analizador de calidad de archivos descargados"""
    
    def __init__(self, base_path: Path = DOWNLOADS_DIR):
        self.base_path = Path(base_path)
        
    def analyze_audio_quality(self, file_path: Path) -> Dict:
        """
        Analizar calidad de archivo de audio
        
        Args:
            file_path (Path): Ruta del archivo
            
        Returns:
            Dict: Información de calidad
        """
        try:
            import mutagen
            from mutagen import File
            
            audio_file = File(str(file_path))
            if audio_file is None:
                return {'error': 'Archivo no soportado'}
            
            info = {
                'duration': getattr(audio_file.info, 'length', 0),
                'bitrate': getattr(audio_file.info, 'bitrate', 0),
                'sample_rate': getattr(audio_file.info, 'sample_rate', 0),
                'channels': getattr(audio_file.info, 'channels', 0),
                'file_size': file_path.stat().st_size
            }
            
            return info
            
        except ImportError:
            return {'error': 'mutagen no instalado'}
        except Exception as e:
            return {'error': str(e)}
            
    def get_quality_report(self) -> Dict:
        """
        Generar reporte de calidad de todos los archivos
        
        Returns:
            Dict: Reporte completo
        """
        audio_extensions = ['.mp3', '.flac', '.wav', '.m4a', '.ogg']
        files_analyzed = 0
        total_duration = 0
        quality_distribution = {}
        
        for file_path in self.base_path.rglob('*'):
            if file_path.suffix.lower() in audio_extensions:
                analysis = self.analyze_audio_quality(file_path)
                
                if 'error' not in analysis:
                    files_analyzed += 1
                    total_duration += analysis.get('duration', 0)
                    
                    # Clasificar por bitrate
                    bitrate = analysis.get('bitrate', 0)
                    if bitrate > 0:
                        if bitrate >= 320:
                            quality = 'Muy Alta (320+ kbps)'
                        elif bitrate >= 256:
                            quality = 'Alta (256+ kbps)'
                        elif bitrate >= 192:
                            quality = 'Buena (192+ kbps)'
                        elif bitrate >= 128:
                            quality = 'Estándar (128+ kbps)'
                        else:
                            quality = 'Baja (<128 kbps)'
                            
                        quality_distribution[quality] = quality_distribution.get(quality, 0) + 1
        
        return {
            'files_analyzed': files_analyzed,
            'total_duration': total_duration,
            'total_duration_formatted': f"{total_duration // 3600:.0f}h {(total_duration % 3600) // 60:.0f}m",
            'quality_distribution': quality_distribution,
            'average_bitrate': sum(int(k.split('(')[1].split('+')[0]) * v for k, v in quality_distribution.items() if '(' in k) / max(files_analyzed, 1)
        }


class MaintenanceManager:
    """Manejador de mantenimiento y limpieza"""
    
    def __init__(self):
        self.file_manager = FileManager()
        self.quality_analyzer = QualityAnalyzer()
        
    def run_full_maintenance(self, progress_callback: Optional[callable] = None) -> Dict:
        """
        Ejecutar mantenimiento completo
        
        Args:
            progress_callback (callable): Callback de progreso
            
        Returns:
            Dict: Resultados del mantenimiento
        """
        results = {}
        
        if progress_callback:
            progress_callback("Limpiando archivos temporales...")
        results['temp_files_deleted'] = self.file_manager.clean_temp_files()
        
        if progress_callback:
            progress_callback("Eliminando carpetas vacías...")
        results['empty_folders_deleted'] = self.file_manager.clean_empty_folders()
        
        if progress_callback:
            progress_callback("Analizando calidad de archivos...")
        results['quality_report'] = self.quality_analyzer.get_quality_report()
        
        if progress_callback:
            progress_callback("Obteniendo información de almacenamiento...")
        results['storage_info'] = self.file_manager.get_storage_info()
        
        if progress_callback:
            progress_callback("Mantenimiento completado")
        
        return results
        
    def cleanup_logs(self, days_old: int = 30) -> int:
        """
        Limpiar logs antiguos
        
        Args:
            days_old (int): Días de antigüedad
            
        Returns:
            int: Archivos eliminados
        """
        deleted_count = 0
        cutoff_time = time.time() - (days_old * 24 * 3600)
        
        for log_file in LOGS_DIR.glob('*.log'):
            try:
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    deleted_count += 1
            except (OSError, PermissionError):
                continue
                
        return deleted_count