from typing import List
from automation.calendar import filter_bookable_dates
from automation.wework_flow import book_desks

def book_wework_desks(
    dates: List[str],
    building: str
) -> str:
    """
    Book WeWork desks for given dates.
    Sundays are skipped automatically.
    """
    filtered = filter_bookable_dates(dates)

    if not filtered:
        return "No bookable dates (all were non-working days)."

    book_desks(
        dates=filtered,
        building_name=building
    )

    skipped = set(dates) - set(filtered)
    msg = f"Booked desks for {filtered} at {building}."
    if skipped:
        msg += f" Skipped non-working days: {sorted(skipped)}."

    return msg
