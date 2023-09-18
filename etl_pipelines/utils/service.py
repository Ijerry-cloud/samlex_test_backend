from etl_pipelines.pipelines.load_bank_summary import BankSummaryManager
from etl_pipelines.pipelines.load_customer_dim import CustomerManager
from etl_pipelines.pipelines.load_merchant_summary import MerchantManager


class ETLService:
    """
    ETL Service
    """

    def __init__(self, collection, *args, **kwargs):

        if collection == "banksummaries":
            self.query = BankSummaryManager(collection, *args, **kwargs)
        elif collection == "merchantsummaries":
            self.query = MerchantManager(collection, *args, **kwargs)
        elif collection == "journals":
            self.query = CustomerManager(*args, **kwargs)

    def run(self, **kwargs):
        """
        Run fetching and saving services as a pipeline
        """
        type = kwargs["type"]
        range = kwargs["range"]

        if type == "summary":
            if range == "alltime":
                data = self.query.get_alltime_summary(range)
            else:
                data = self.query.get_timebound_summary(range)
            self.query.save_summary(data, range)
        return len(data)
