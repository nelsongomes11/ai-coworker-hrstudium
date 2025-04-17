import json
import requests
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

       

        print("Files to upload",files)
        print("Id type absence ",id_type_absence)

        form_data={
            "id_tipo_ausencia": id_type_absence,
            "datas": formatted_dates,
        }
        
        response=requests.post(
            "http://192.168.1.43:3000/vacations/requests-absences",
            headers={"company": "dev", "Authorization": "Bearer " + bearer_token,"Connection":"keep-alive","Accept-Encoding":"gzip, deflate, br","Accept":"*/*"},
            json={
                  
                        "id_tipo_ausencia": id_type_absence,
                        "datas": formatted_dates,
                  ]
            },
            
            
        
        )

    
    if response.status_code == 201:
            return "Request successful: " + str(response.json())
    else:
            return f"Request failed with status {response.status_code}: {response.text}"


res = add_request(
    dates=["2025-07-23", "2025-07-24"],
    bearer_token="f5651bd70280f5ac9bc5bacedf349635c7cfe8216d868a68cf10b121b86fb2a4ab372ec64ca4c90316d86afeba8c2a49aa496f9b89642bfe50ea331c9c997603e5550ddbd9dece0a3e4eae09525bee4ae6a50de1ba1ede90fb076f6476e17269f5eae841a559a15922e40e574d29258ac305a77364990e3b1c6e431f7cdcb3403c12c4b96386f7ba96020cefd612c5b04369adb61abc9ec1c7632dd32164f0e3cebda933ca9724136030de5a6ec61488f4372000b7458bf751d6991677d5bc469be3adaca82153561a25ccd46b6cd588bfcd56ec47366ef78ba5e05e81e6d75a79db4a71db1738337da624dc8abc999dfa0ab9c18e22194b20dd16c16a32526e37092eefb608df9d580f8588f7e5d68ae8088cf7625acc3562e3b2eb1687aa6cd3c7748fc78ed56957092169b402c14f7bb1b583f7d205c82c66a93a477c5fd091995928ee7517d5ce77711423cb89fa",
    type_leave="absence",
    id_type_absence=3,
    files=[],
    type_day=1,
    total_hours=8
)

print(res)