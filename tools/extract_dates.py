from langchain_core.tools import tool
from datetime import datetime


@tool
def extract_dates(dates:list) -> dict:
    """
    Extract dates with weekday from a list of dates.
    Only use this tool if the user request any dates or anything that mentions dates.
    Only use this if you don't have the weekdays for certain dates.
    If you don't need to get any dates from the user don't use this.

    Args:
        dates (list): A list of date strings in the format YYYY-MM-DD.
    Returns:
        dict: A dictionary with the date strings as keys and their corresponding day of the week as values.
    """

    extracted_dates = {}

    for date in dates:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")

            extracted_dates[date] = parsed_date.strftime("%A")
        except ValueError:
            # If parsing fails, skip the date
            continue
    
    
    return extracted_dates



