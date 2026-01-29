import datetime as dt

def is_bookable_day(date: dt.date) -> bool:
    # Sunday = 6
    if date.weekday() == 6:
        return False
    return True

def filter_bookable_dates(dates: list[str]) -> list[str]:
    valid = []
    for d in dates:
        date = dt.date.fromisoformat(d)
        if is_bookable_day(date):
            valid.append(d)
    return valid
