from etl_pipelines.utils.connections import EFTEngineManager


class CustomerManager(EFTEngineManager):
    def __init__(self, collection=None):
        super().__init__(collection)

    def set_dimension(self) -> None:
        self._sort = {"transactionTime": -1}
        self._group = {
            "_id": "$maskedPan",
            "last_txn_value": {"$last": "$amount"},
            "last_txn_status": {"$last": "$responseCode"},
            "total_val": {"$sum": "$amount"},
            "total_vol": {"$sum": 1},
            "last_txn_date": {"$last": "$transactionTime"},
        }

    def get_dimension(self) -> list:
        self.set_dimension()
        self._pipeline = [{"$sort": self._sort}, {"$group": self._group}]
        return self.fetch_records
