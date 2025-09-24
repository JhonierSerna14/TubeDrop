# -*- coding: utf-8 -*-
"""
Interfaz gráfica principal de YouTube Downloader - Versión Simplificada

Interfaz básica y funcional para el descargador de YouTube.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import logging
import os
from pathlib import Path
from typing import Dict, Any

from ..core.downloader import YouTubeDownloader
from ..core.config import AUDIO_FORMATS, VIDEO_FORMATS, VIDEO_QUALITIES
from ..utils.helpers import (
    is_valid_youtube_url, select_folder, format_duration,
    SettingsManager
)


class ModernProgressBar(ttk.Frame):
    """Barra de progreso moderna con información detallada"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Barra de progreso principal
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self, 
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(fill='x', pady=(0, 5))
        
        # Información de progreso
        self.info_frame = ttk.Frame(self)
        self.info_frame.pack(fill='x')
        
        self.file_label = ttk.Label(self.info_frame, text="Preparando descarga...")
        self.file_label.pack(side='left')
        
        self.stats_label = ttk.Label(self.info_frame, text="")
        self.stats_label.pack(side='right')
        
    def update_progress(self, data: Dict[str, Any]):
        """Actualizar información de progreso"""
        if data['status'] == 'downloading':
            # Extraer porcentaje del string (ej: "45.2%")
            percent_str = data.get('percent', '0%').replace('%', '')
            try:
                percent = float(percent_str)
                self.progress_var.set(percent)
            except ValueError:
                pass
                
            # Actualizar labels
            filename = Path(data.get('filename', '')).name
            if len(filename) > 50:
                filename = filename[:47] + "..."
            self.file_label.config(text=f"Descargando: {filename}")
            
            speed = data.get('speed', '')
            eta = data.get('eta', '')
            files_info = f"{data.get('completed_files', 0)}/{data.get('total_files', 0)}"
            
            stats_text = f"Velocidad: {speed} | ETA: {eta} | Archivos: {files_info}"
            self.stats_label.config(text=stats_text)
            
        elif data['status'] == 'finished':
            files_info = f"{data.get('completed_files', 0)}/{data.get('total_files', 0)}"
            self.file_label.config(text="Descarga completada")
            self.stats_label.config(text=f"Archivos completados: {files_info}")
            
            if data.get('completed_files', 0) >= data.get('total_files', 1):
                self.progress_var.set(100)
    
    def reset(self):
        """Resetear barra de progreso"""
        self.progress_var.set(0)
        self.file_label.config(text="Esperando...")
        self.stats_label.config(text="")


class YouTubeDownloaderGUI:
    """Interfaz gráfica principal de YouTube Downloader"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.downloader = YouTubeDownloader()
        self.settings = SettingsManager(Path.home() / '.youtube_downloader' / 'settings.json')
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('youtube_downloader.gui')
        
        # Variables de interfaz
        self.url_var = tk.StringVar()
        self.format_var = tk.StringVar(value=self.settings.get('default_format'))
        self.quality_var = tk.StringVar(value=self.settings.get('default_quality'))
        self.output_path_var = tk.StringVar(value=self.settings.get('download_path'))
        
        # Estado de descarga
        self.is_downloading = False
        
        self._setup_gui()
        self._setup_callbacks()
        
    def _setup_gui(self):
        """Configurar interfaz gráfica"""
        # Configuración de ventana principal
        self.root.title("YouTube Downloader - Descargador Profesional")
        self.root.geometry("900x700")
        self.root.minsize(600, 500)
        
        # Configurar tema
        style = ttk.Style()
        style.theme_use('clam')
        
        # Crear frame principal
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill='both', expand=True)
        
        self._create_menu()
        self._create_header()
        self._create_url_section()
        self._create_options_section()
        self._create_progress_section()
        self._create_log_section()
        self._create_control_buttons()
        
    def _create_menu(self):
        """Crear barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Configuraciones", command=self._show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Historial", command=self._show_history)
        tools_menu.add_command(label="Abrir carpeta de descargas", command=self._open_downloads_folder)
        tools_menu.add_separator()
        tools_menu.add_command(label="Limpiar logs", command=self._clear_logs)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self._show_about)
        
    def _create_header(self):
        """Crear sección de encabezado"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Título principal
        title_label = ttk.Label(header_frame, text="🎵 YouTube Downloader", 
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Descarga videos y playlists de YouTube en alta calidad")
        subtitle_label.pack()
        
    def _create_url_section(self):
        """Crear sección de URL"""
        url_frame = ttk.LabelFrame(self.main_frame, text="URL de YouTube", padding="10")
        url_frame.pack(fill='x', pady=(0, 10))
        
        # Campo de URL
        url_entry_frame = ttk.Frame(url_frame)
        url_entry_frame.pack(fill='x')
        
        self.url_entry = ttk.Entry(url_entry_frame, textvariable=self.url_var, font=('TkDefaultFont', 10))
        self.url_entry.pack(side='left', fill='x', expand=True)
        
        # Botón de pegar
        paste_button = ttk.Button(url_entry_frame, text="Pegar", command=self._paste_url)
        paste_button.pack(side='right', padx=(5, 0))
        
        # Botón de obtener info
        info_button = ttk.Button(url_entry_frame, text="Info", command=self._get_video_info)
        info_button.pack(side='right', padx=(5, 0))
        
        # Etiqueta de ayuda
        help_label = ttk.Label(url_frame, text="Pega aquí la URL del video o playlist de YouTube", 
                              font=('TkDefaultFont', 8))
        help_label.pack(pady=(5, 0))
        
    def _create_options_section(self):
        """Crear sección de opciones"""
        options_frame = ttk.LabelFrame(self.main_frame, text="Opciones de Descarga", padding="10")
        options_frame.pack(fill='x', pady=(0, 10))
        
        # Primera fila: Formato y Calidad
        row1_frame = ttk.Frame(options_frame)
        row1_frame.pack(fill='x', pady=(0, 10))
        
        # Formato
        ttk.Label(row1_frame, text="Formato:").pack(side='left')
        format_combo = ttk.Combobox(row1_frame, textvariable=self.format_var, state='readonly', width=10)
        format_combo['values'] = list(AUDIO_FORMATS.keys()) + list(VIDEO_FORMATS.keys())
        format_combo.pack(side='left', padx=(5, 20))
        
        # Calidad
        ttk.Label(row1_frame, text="Calidad:").pack(side='left')
        quality_combo = ttk.Combobox(row1_frame, textvariable=self.quality_var, state='readonly', width=10)
        quality_combo['values'] = ['128', '192', '256', '320'] + list(VIDEO_QUALITIES.keys())
        quality_combo.pack(side='left', padx=(5, 0))
        
        # Segunda fila: Carpeta de destino
        row2_frame = ttk.Frame(options_frame)
        row2_frame.pack(fill='x')
        
        ttk.Label(row2_frame, text="Guardar en:").pack(side='left')
        
        path_entry = ttk.Entry(row2_frame, textvariable=self.output_path_var, state='readonly')
        path_entry.pack(side='left', fill='x', expand=True, padx=(5, 5))
        
        browse_button = ttk.Button(row2_frame, text="📁", command=self._browse_folder, width=3)
        browse_button.pack(side='right')
        
    def _create_progress_section(self):
        """Crear sección de progreso"""
        progress_frame = ttk.LabelFrame(self.main_frame, text="Progreso", padding="10")
        progress_frame.pack(fill='x', pady=(0, 10))
        
        self.progress_bar = ModernProgressBar(progress_frame)
        self.progress_bar.pack(fill='x')
        
    def _create_log_section(self):
        """Crear sección de logs"""
        log_frame = ttk.LabelFrame(self.main_frame, text="Registro de Actividad", padding="10")
        log_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state='disabled')
        self.log_text.pack(fill='both', expand=True)
        
    def _create_control_buttons(self):
        """Crear botones de control"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill='x')
        
        # Botón principal de descarga
        self.download_button = ttk.Button(button_frame, text="🔽 Descargar", 
                                         command=self._start_download)
        self.download_button.pack(side='left', padx=(0, 5))
        
        # Botón de cancelar
        self.cancel_button = ttk.Button(button_frame, text="❌ Cancelar", 
                                       command=self._cancel_download, state='disabled')
        self.cancel_button.pack(side='left', padx=(0, 20))
        
        # Botones adicionales
        ttk.Button(button_frame, text="📁 Abrir Carpeta", 
                  command=self._open_downloads_folder).pack(side='right')
        
        ttk.Button(button_frame, text="🔍 Buscar", 
                  command=self._show_search).pack(side='right', padx=(0, 5))
        
    def _setup_callbacks(self):
        """Configurar callbacks y eventos"""
        # Callback de progreso
        self.downloader.set_progress_callback(self._update_progress)
        
        # Eventos de teclado
        self.url_entry.bind('<Return>', lambda e: self._start_download())
        self.root.bind('<Control-v>', lambda e: self._paste_url())
        
        # Evento de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _paste_url(self):
        """Pegar URL desde el portapapeles"""
        try:
            clipboard_content = self.root.clipboard_get()
            if is_valid_youtube_url(clipboard_content):
                self.url_var.set(clipboard_content)
                self._log_message("✅ URL pegada desde el portapapeles")
            else:
                self._log_message("⚠️ El contenido del portapapeles no es una URL válida de YouTube")
        except tk.TclError:
            self._log_message("❌ No se pudo acceder al portapapeles")
            
    def _get_video_info(self):
        """Obtener información del video"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Advertencia", "Ingresa una URL")
            return
            
        if not is_valid_youtube_url(url):
            messagebox.showerror("Error", "URL no válida")
            return
            
        def get_info():
            info = self.downloader.get_video_info(url)
            if info:
                self.root.after(0, lambda: self._show_video_info(info))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "No se pudo obtener información"))
                
        threading.Thread(target=get_info, daemon=True).start()
        
    def _show_video_info(self, info: Dict):
        """Mostrar información del video en una ventana"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Información del Video")
        info_window.geometry("600x400")
        info_window.transient(self.root)
        
        frame = ttk.Frame(info_window, padding="10")
        frame.pack(fill='both', expand=True)
        
        # Información básica
        title = info.get('title', 'N/A')
        uploader = info.get('uploader', 'N/A')
        duration = format_duration(info.get('duration', 0))
        view_count = info.get('view_count', 0)
        
        ttk.Label(frame, text=f"Título: {title}", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w')
        ttk.Label(frame, text=f"Canal: {uploader}").pack(anchor='w')
        ttk.Label(frame, text=f"Duración: {duration}").pack(anchor='w')
        ttk.Label(frame, text=f"Visualizaciones: {view_count:,}").pack(anchor='w')
        
        if 'entries' in info:
            ttk.Label(frame, text=f"Playlist con {len(info['entries'])} videos").pack(anchor='w')
        
        ttk.Button(frame, text="Cerrar", command=info_window.destroy).pack(pady=(10, 0))
        
    def _browse_folder(self):
        """Seleccionar carpeta de destino"""
        folder = select_folder()
        if folder:
            self.output_path_var.set(folder)
            self._log_message(f"📁 Carpeta seleccionada: {folder}")
            
    def _start_download(self):
        """Iniciar descarga"""
        if self.is_downloading:
            return
            
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Advertencia", "Ingresa una URL")
            return
            
        if not is_valid_youtube_url(url):
            messagebox.showerror("Error", "URL no válida de YouTube")
            return
            
        output_path = self.output_path_var.get()
        if not output_path or not Path(output_path).exists():
            messagebox.showerror("Error", "Selecciona una carpeta válida")
            return
            
        # Cambiar estado de interfaz
        self.is_downloading = True
        self.download_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        
        # Resetear barra de progreso
        self.progress_bar.reset()
        
        # Iniciar descarga en hilo separado
        download_thread = threading.Thread(
            target=self._download_worker,
            args=(url, output_path),
            daemon=True
        )
        download_thread.start()
        
        self._log_message(f"🔽 Iniciando descarga: {url}")
        
    def _download_worker(self, url: str, output_path: str):
        """Worker para descarga en hilo separado"""
        try:
            format_type = self.format_var.get()
            quality = self.quality_var.get()
            
            # Detectar si es playlist
            info = self.downloader.get_video_info(url)
            is_playlist = info and 'entries' in info
            
            if is_playlist:
                success = self.downloader.download_playlist(
                    url, format_type, quality, output_path
                )
            else:
                success = self.downloader.download_single_video(
                    url, format_type, quality, output_path
                )
                
            # Actualizar interfaz en hilo principal
            self.root.after(0, lambda: self._download_finished(success))
            
        except Exception as e:
            self.logger.error(f"Error en descarga: {e}")
            self.root.after(0, lambda: self._download_finished(False, str(e)))
            
    def _download_finished(self, success: bool, error: str = None):
        """Callback cuando termina la descarga"""
        self.is_downloading = False
        self.download_button.config(state='normal')
        self.cancel_button.config(state='disabled')
        
        if success:
            self._log_message("✅ Descarga completada exitosamente")
            messagebox.showinfo("Éxito", "Descarga completada")
        else:
            error_msg = f"❌ Error en descarga: {error}" if error else "❌ Error en descarga"
            self._log_message(error_msg)
            messagebox.showerror("Error", "La descarga falló")
            
    def _cancel_download(self):
        """Cancelar descarga actual"""
        if self.is_downloading:
            self.downloader.cancel_current_download()
            self._log_message("⏹️ Cancelando descarga...")
            
    def _update_progress(self, data: Dict[str, Any]):
        """Actualizar barra de progreso"""
        self.root.after(0, lambda: self.progress_bar.update_progress(data))
        
    def _log_message(self, message: str):
        """Agregar mensaje al log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
    def _clear_logs(self):
        """Limpiar área de logs"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
    def _show_settings(self):
        """Mostrar ventana de configuraciones"""
        messagebox.showinfo("Configuraciones", "Función de configuraciones en desarrollo")
        
    def _show_history(self):
        """Mostrar ventana de historial"""
        messagebox.showinfo("Historial", "Función de historial en desarrollo")
        
    def _show_search(self):
        """Mostrar ventana de búsqueda"""
        messagebox.showinfo("Próximamente", "Función de búsqueda en desarrollo")
        
    def _open_downloads_folder(self):
        """Abrir carpeta de descargas"""
        path = self.output_path_var.get()
        if path and Path(path).exists():
            os.startfile(path)  # Windows
        else:
            messagebox.showerror("Error", "Carpeta no encontrada")
            
    def _show_about(self):
        """Mostrar información sobre la aplicación"""
        about_text = """
YouTube Downloader v2.0

Un descargador profesional para videos y playlists de YouTube.

Características:
• Descarga de videos individuales y playlists
• Múltiples formatos de audio y video
• Interfaz moderna e intuitiva
• Detección de duplicados
• Historial de descargas
• Configuración personalizable

Desarrollado con Python y tkinter
© 2025 YouTube Downloader"""
        
        messagebox.showinfo("Acerca de", about_text)
        
    def _on_closing(self):
        """Manejar cierre de aplicación"""
        if self.is_downloading:
            if messagebox.askyesno("Confirmar", "Hay una descarga en progreso. ¿Salir de todas formas?"):
                self.downloader.cancel_current_download()
                self.root.destroy()
        else:
            self.root.destroy()
            
    def run(self):
        """Ejecutar la aplicación"""
        self._log_message("🚀 YouTube Downloader iniciado")
        self._log_message("📝 Pega una URL de YouTube para comenzar")
        self.root.mainloop()


def main():
    """Función principal"""
    app = YouTubeDownloaderGUI()
    app.run()


if __name__ == "__main__":
    main()