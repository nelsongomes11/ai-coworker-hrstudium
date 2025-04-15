from langchain_core.tools import tool
from datetime import datetime
import requests

@tool
def add_request(dates: list, bearer_token: str, type_leave: str, id_type_absence:int, files: object,  type_day:int, total_hours:int) -> str:
    """
        
        Only use this tool when the user explicitly confirms the dates.
        Makes a request to book the dates in the HR system.

    Args:
        dates (list): List of date strings in YYYY-MM-DD format.
        bearer_token (str): Bearer token for authentication.
        type_leave (str): Type of leave, either "vacation" or "absence".
        id_type_absence (int): ID of the absence type if applicable.
        files (list): List of file objects to be uploaded.
        type_day (int): Type of day, 1 for full day, 2 for half day.
        total_hours (int): Total hours for the leave request.

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

    if type_leave=="absence":
        
        print(files)

        files_to_upload = [('files[]', f) for f in files]

       

        print("Files to upload",files)
        response=requests.post(
            "https://api-dev.hrstudium.pt/vacations/requests-absences",
            headers={"company": "dev", "Authorization": "Bearer " + bearer_token},
            data={
                  "datas": formatted_dates,
                  "id_tipo_ausencia": str(id_type_absence),
            }
           
        )

    
    if response.status_code == 201:
            return "Request successful: " + str(response.json())
    else:
            return f"Request failed with status {response.status_code}: {response.text}"

    




  
    