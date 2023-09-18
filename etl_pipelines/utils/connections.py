from django.conf import settings

from .utils import get_mdb_conn


class EFTEngineManager:
    """
    Manager for EFT Engine DB connection and queries
    """

    def __init__(self, collection=None):
        db = get_mdb_conn(settings.EFT_ENGINE_CONN_URL, settings.EFT_ENGINE)
        self.collection = db[collection or "journals"]
        self._match = {}
        self._pipeline = []

    def set_created_at(self, *args, **kwargs):
        match = self._match
        match.update(kwargs)
        self._match = match
        return self

    @property
    def fetch_records(self) -> list:
        records = self.collection.aggregate(self._pipeline, allowDiskUse=True)
        return list(records)
