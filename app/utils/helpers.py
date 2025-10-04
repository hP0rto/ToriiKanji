from PyQt6.QtCore import  QThread
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QPixmap

from core.workers.db_worker import DbWorker
from core.workers.ocr_worker import OcrWorker

from utils.paths import NO_IMG
        
def run_in_thread(worker: OcrWorker | DbWorker, on_finished=None, on_error=None):
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
    return QPixmap(str(NO_IMG)).scaled(200,200) if pixmap.isNull() else pixmap

import win32process, win32gui, win32api

def get_app_name():
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    h_process = win32api.OpenProcess(0x1000, False, pid)
    exe_path = win32process.GetModuleFileNameEx(h_process, 0)
    print("Nome exe:", exe_path)
    info = win32api.GetFileVersionInfo(exe_path, "\\StringFileInfo\\040904b0\\FileDescription")
    print("Nome amigável:", info)