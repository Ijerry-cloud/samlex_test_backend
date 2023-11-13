from datetime import datetime, time


def start_end_datetime(startDate, endDate):
    start_date = datetime.strptime(startDate, '%Y-%m-%d') if startDate else None
    end_date = datetime.strptime(endDate, '%Y-%m-%d') if endDate else None
    start_date = datetime.combine(start_date, time.min) if start_date else datetime.now()
    end_date = datetime.combine(end_date, time.max) if end_date else datetime.now()

    return start_date, end_date