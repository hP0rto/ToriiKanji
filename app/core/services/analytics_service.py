"""
Analytics service for ToriiKanji.
Provides aggregated data for the analytics dashboard.
"""

from db.repositories.capture_repository import CaptureRepository


class AnalyticsService:
    def __init__(self):
        self.capture_repo = CaptureRepository()

    def get_captures_with_dates(self, order='ASC'):
        """Get all captures with their timestamps for trend analysis."""
        return self.capture_repo.list_captures_with_dates(order=order)

    def count_by_media(self):
        """Get capture counts grouped by media source."""
        return self.capture_repo.count_by_media()
