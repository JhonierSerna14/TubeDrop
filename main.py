#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Downloader - Aplicación Principal

Un descargador profesional de videos y playlists de YouTube con interfaz gráfica moderna.
Incluye funcionalidades avanzadas como detección de duplicados, múltiples formatos,
configuración personalizable y gestión de descargas.

Funcionalidades principales:
- Descarga de videos individuales y playlists completas
- Múltiples formatos de audio (MP3, FLAC, WAV, M4A, OGG)
- Múltiples formatos de video (MP4, WebM, MKV, AVI)
- Diferentes calidades de descarga
- Interfaz gráfica intuitiva y moderna
- Detección automática de archivos duplicados
- Configuración personalizable
- Historial de descargas
- Barra de progreso detallada
- Logs de actividad en tiempo real

Autor: YouTube Downloader Team
Versión: 2.0.0
Fecha: 2025
Licencia: MIT

Dependencias principales:
- yt-dlp: Motor de descarga de YouTube
- tkinter: Interfaz gráfica (incluida en Python)
- pathlib: Manejo de rutas (incluida en Python)
- threading: Operaciones asíncronas (incluida en Python)
- json: Manejo de configuraciones (incluida en Python)

Uso:
    python main.py                    # Ejecutar con interfaz gráfica
    python main.py --cli <URL>        # Ejecutar en modo línea de comandos
    python main.py --help            # Mostrar ayuda
"""

import sys
import argparse
import logging
from pathlib import Path

# Configurar la ruta para imports locales
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.gui.main_window import YouTubeDownloaderGUI
    from src.core.downloader import YouTubeDownloader
    from src.core.config import LOGGING_CONFIG
    from src.utils.helpers import is_valid_youtube_url
    import logging.config
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("📋 Asegúrate de que todas las dependencias estén instaladas:")
    print("   pip install yt-dlp")
    print("   pip install -r requirements.txt")
    sys.exit(1)


def setup_logging():
    """Configurar sistema de logging"""
    try:
        logging.config.dictConfig(LOGGING_CONFIG)
    except Exception:
        # Configuración básica si falla la configuración avanzada
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s - %(message)s'
        )


def run_cli_mode(url: str, output_format: str = 'mp3', quality: str = '192', output_path: str = None):
    """
    Ejecutar descarga en modo línea de comandos
    
    Args:
        url (str): URL del video o playlist
        output_format (str): Formato de salida
        quality (str): Calidad de descarga
        output_path (str): Ruta de salida
    """
    print("🎵 YouTube Downloader - Modo Línea de Comandos")
    print("=" * 50)
    
    # Validar URL
    if not is_valid_youtube_url(url):
        print("❌ Error: URL no válida de YouTube")
        return False
    
    # Crear instancia del descargador
    downloader = YouTubeDownloader(output_path or "./descargas")
    
    # Configurar callback de progreso simple
    def progress_callback(data):
        if data['status'] == 'downloading':
            print(f"\r📥 Descargando: {data.get('percent', '0%')} - {data.get('speed', '')}", end='', flush=True)
        elif data['status'] == 'finished':
            print(f"\n✅ Completado: {Path(data.get('filename', '')).name}")
    
    downloader.set_progress_callback(progress_callback)
    
    # Obtener información del contenido
    print(f"📋 Obteniendo información: {url}")
    info = downloader.get_video_info(url)
    
    if not info:
        print("❌ No se pudo obtener información del contenido")
        return False
    
    # Mostrar información
    if 'entries' in info:
        print(f"📂 Playlist detectada: {info.get('title', 'Sin título')}")
        print(f"📊 Videos encontrados: {len(info['entries'])}")
        
        # Descargar playlist
        success = downloader.download_playlist(url, output_format, quality, output_path)
    else:
        print(f"🎬 Video detectado: {info.get('title', 'Sin título')}")
        print(f"👤 Canal: {info.get('uploader', 'Desconocido')}")
        
        # Descargar video individual
        success = downloader.download_single_video(url, output_format, quality, output_path)
    
    if success:
        print("\n🎉 ¡Descarga completada exitosamente!")
        return True
    else:
        print("\n❌ Error durante la descarga")
        return False


def main():
    """Función principal de la aplicación"""
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description='YouTube Downloader - Descargador profesional de videos y playlists',
        epilog='Ejemplos de uso:\n'
               '  python main.py\n'
               '  python main.py --cli "https://youtube.com/watch?v=VIDEO_ID"\n'
               '  python main.py --cli "PLAYLIST_URL" --format mp4 --quality 720p',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--cli', metavar='URL', 
                       help='Ejecutar en modo línea de comandos con la URL especificada')
    parser.add_argument('--format', default='mp3', 
                       help='Formato de salida (mp3, flac, wav, mp4, etc.) [default: mp3]')
    parser.add_argument('--quality', default='192', 
                       help='Calidad de descarga (128, 192, 256, 320, 720p, 1080p, etc.) [default: 192]')
    parser.add_argument('--output', metavar='PATH', 
                       help='Carpeta de destino para las descargas [default: ./descargas]')
    parser.add_argument('--version', action='version', version='YouTube Downloader 2.0.0')
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging()
    logger = logging.getLogger('youtube_downloader.main')
    
    try:
        if args.cli:
            # Modo línea de comandos
            logger.info("Iniciando en modo línea de comandos")
            success = run_cli_mode(args.cli, args.format, args.quality, args.output)
            sys.exit(0 if success else 1)
        else:
            # Modo interfaz gráfica
            logger.info("Iniciando interfaz gráfica")
            print("🚀 Iniciando YouTube Downloader...")
            print("💡 Consejo: Usa --help para ver opciones de línea de comandos")
            
            app = YouTubeDownloaderGUI()
            app.run()
            
    except KeyboardInterrupt:
        print("\n⏹️  Operación cancelada por el usuario")
        logger.info("Aplicación cancelada por el usuario")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        logger.error(f"Error inesperado: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
