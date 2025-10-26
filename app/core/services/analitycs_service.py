from db.repositories.capture_repository import CaptureRepository

class AnalitycsService():
    def __init__(self):
        self.capture_repo = CaptureRepository()

    def get_captures_with_dates(self, order='ASC'):
        return self.capture_repo.list_captures_with_dates(order= order)
    
    def count_by_media(self):
        return self.capture_repo.count_by_media()
    