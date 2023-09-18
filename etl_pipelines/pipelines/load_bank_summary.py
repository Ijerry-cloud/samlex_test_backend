from etl_pipelines.models import Bank, BankSummary
from etl_pipelines.utils.connections import EFTEngineManager


class BankSummaryManager(EFTEngineManager):
    def __init__(self, collection=None, *args, **kwargs):
        super().__init__(collection)

        if "createdAt" in kwargs:
            self.set_created_at(**{k: kwargs[k] for k in ["createdAt"]})

    def set_summary(self, range: str):
        if range == "l30":
            self._group = {
                "_id": {"bankName": "$bankName", "bankCode": "$bankCode"},
                "txn_vol_l30": {"$sum": "$transactionCount"},
                "txn_val_l30": {"$sum": "$totalAmount"},
                "txn_val_success_l30": {
                    "$sum": {
                        "$cond": [{"$eq": ["$statusCode", "00"]}, "$totalAmount", 0]
                    }
                },
                "txn_vol_success_l30": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$statusCode", "00"]},
                            "$transactionCount",
                            0,
                        ]
                    }
                },
            }
            self._project = {
                "_id": 0,
                "bankName": "$_id.bankName",
                "bankCode": "$_id.bankCode",
                "txn_val_l30": 1,
                "txn_vol_l30": 1,
                "txn_val_success_l30": 1,
                "txn_vol_success_l30": 1,
            }
        elif range == "daily":
            self._group = {
                "_id": {"bankName": "$bankName", "bankCode": "$bankCode"},
                "today_vol": {"$sum": "$transactionCount"},
                "today_val": {"$sum": "$totalAmount"},
                "today_val_success": {
                    "$sum": {
                        "$cond": [{"$eq": ["$statusCode", "00"]}, "$totalAmount", 0]
                    }
                },
                "today_vol_success": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$statusCode", "00"]},
                            "$transactionCount",
                            0,
                        ]
                    }
                },
            }
            self._project = {
                "_id": 0,
                "bankName": "$_id.bankName",
                "bankCode": "$_id.bankCode",
                "today_val": 1,
                "today_vol": 1,
                "today_val_success": 1,
                "today_vol_success": 1,
            }
        else:
            self._group = {
                "_id": {"bankName": "$bankName", "bankCode": "$bankCode"},
                "txn_vol_alltime": {"$sum": "$transactionCount"},
                "txn_val_alltime": {"$sum": "$totalAmount"},
                "txn_val_success_alltime": {
                    "$sum": {
                        "$cond": [{"$eq": ["$statusCode", "00"]}, "$totalAmount", 0]
                    }
                },
                "txn_vol_success_alltime": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$statusCode", "00"]},
                            "$transactionCount",
                            0,
                        ]
                    }
                },
            }
            self._project = {
                "_id": 0,
                "bankName": "$_id.bankName",
                "bankCode": "$_id.bankCode",
                "txn_val_alltime": 1,
                "txn_vol_alltime": 1,
                "txn_val_success_alltime": 1,
                "txn_vol_success_alltime": 1,
            }

    def get_timebound_summary(self, range: str) -> list:
        self.set_summary(range)
        self._pipeline = [
            {"$match": self._match},
            {"$group": self._group},
            {"$project": self._project},
        ]
        return self.fetch_records

    def get_alltime_summary(self, range: str) -> list:
        self.set_summary(range)
        self._pipeline = [{"$group": self._group}, {"$project": self._project}]
        return self.fetch_records

    def save_summary(self, data: list, range: str) -> None:
        if range == "alltime":
            fields = [
                "txn_vol_alltime",
                "txn_val_alltime",
                "txn_vol_success_alltime",
                "txn_val_success_alltime",
                "txn_vol_failed_alltime",
                "txn_val_failed_alltime",
            ]
        elif range == "daily":
            fields = [
                "today_vol",
                "today_val",
                "today_vol_success",
                "today_val_success",
                "today_vol_failed",
                "today_val_failed",
            ]
        if range == "l30":
            fields = [
                "txn_vol_l30",
                "txn_val_l30",
                "txn_vol_success_l30",
                "txn_val_success_l30",
                "txn_vol_failed_l30",
                "txn_val_failed_l30",
            ]

        with BankSummary.objects.bulk_update_or_create_context(
            fields, match_field=["bank"]
        ) as bulkit:
            for item in data:
                name = item.pop("bankName")
                code = item.pop("bankCode")
                bank, _ = Bank.objects.get_or_create(name=name, code=code)
                bulkit.queue(BankSummary(bank=bank, **item))
