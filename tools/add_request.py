from langchain_core.tools import tool
from datetime import datetime
import requests

@tool
def add_request(dates: list, bearer_token: str, type_leave: str, type_absence:int) -> str:
    """
        
        Only use this tool when the user explicitly confirms the dates.
        Makes a request to book the dates in the HR system.

    Args:
        dates (list): List of date strings in YYYY-MM-DD format.
        bearer_token (str): Bearer token for authentication.
        type_leave (str): Type of leave, either "vacation" or "absence".
        type_absence (int): ID of the absence type if applicable.

    Returns:
        str: Response from the HR system.

    """


    formatted_dates = [
    {
        "data": date,
        "todo_dia": 1,
        "total_horas": 8,
        "hora_inicio": "09:00:00",
        "hora_fim": "18:00:00"
    }
    for date in dates
]
    

    if type_leave=="vacation":
        type_absence=None

        response=requests.post(
            "https://api-dev.hrstudium.pt/vacations/requests",
            headers={"company": "dev", "Authorization": "Bearer " + bearer_token},
            json={"datas": formatted_dates}

        )

    
    if response.status_code == 201:
            return "Request successful: " + str(response.json())
    else:
            return f"Request failed with status {response.status_code}: {response.text}"

        


  
    return 