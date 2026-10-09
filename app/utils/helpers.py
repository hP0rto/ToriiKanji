"""
Helper utilities for ToriiKanji.
Thread management, image handling, and platform-specific utilities.
"""

import os

from PyQt6.QtCore import QThread
from PyQt6.QtGui import QPixmap

from utils.paths import NO_IMG


def run_in_thread(worker, on_finished=None, on_error=None):
    """
    Run a QObject worker in a background QThread.
    
    Args:
        worker: QObject with a 'run' slot, 'finished' and 'error' signals
        on_finished: Callback for successful completion
        on_error: Callback for error handling
        
    Returns:
        QThread instance (keep a reference to prevent garbage collection)
    """
    _thread = QThread()

    worker.moveToThread(_thread)
    _thread.started.connect(worker.run)

    if on_finished:
        worker.finished.connect(on_finished)
    if on_error:
        worker.error.connect(on_error)

    worker.finished.connect(_thread.quit)
    worker.finished.connect(worker.deleteLater)
    _thread.finished.connect(_thread.deleteLater)

    _thread.start()
    return _thread


def pixmap_null_handler(pixmap: QPixmap):
    """Return a placeholder image if the pixmap is null."""
    return QPixmap(str(NO_IMG)).scaled(200, 200) if pixmap.isNull() else pixmap


import win32api
import win32gui
import win32process


def get_app_name():
    """
    Get the name of the currently focused application.
    Tries to get the friendly FileDescription first, falls back to executable name.
    
    Returns:
        str or None: Application name, or None if detection fails
    """
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        h_process = win32api.OpenProcess(0x1000, False, pid)
        exe_path = win32process.GetModuleFileNameEx(h_process, 0)

        # Try to get the friendly name (FileDescription)
        try:
            info = win32api.GetFileVersionInfo(
                exe_path, "\\StringFileInfo\\040904b0\\FileDescription"
            )
            if info:
                return info
        except Exception:
            pass

        # Fallback: use the executable filename without extension
        if exe_path:
            base_name = os.path.basename(exe_path)
            friendly_name = os.path.splitext(base_name)[0]
            return friendly_name

    except Exception as e:
        print(f"Error getting app name: {e}")
        return None
