from PyQt6.QtCore import QObject, pyqtSignal

class DbWorker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, handler, action, *args, **kwargs):
        super().__init__()
        self.handler = handler
        self.action = action
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = getattr(self.handler, self.action)(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))