from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from etl_pipelines.utils.service import ETLService


class Command(BaseCommand):
    """
    Management Command for fetching all summaries
    """

    help = "Extract and save Transaction summaries in DB"

    def add_arguments(self, parser):
        """
        :parser: Parser for adding command line arguments to management command.
        """
        parser.add_argument(
            "-coll",
            "--collection",
            type=str,
            help="Specifies collection to retrieve records from",
        )
        parser.add_argument(
            "-r",
            "--range",
            type=str,
            help="Time categorization for data summarization",
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        db = kwargs.get("collection")
        range = kwargs.get("range")

        if db:
            today = datetime.today()
            today = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
            if range == "daily":
                created = {"$gte": today}
                etl_service = ETLService(db, createdAt=created)
            elif range == "l30":
                l30 = today - timedelta(days=30)
                created = {"$gte": l30, "$lt": today}
                etl_service = ETLService(db, createdAt=created)
            else:
                etl_service = ETLService(db)
            record_count = etl_service.run(type="summary", range=range)
            self.stdout.write(
                self.style.SUCCESS(f"Added a total of {record_count} records.")
            )
