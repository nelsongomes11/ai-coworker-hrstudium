import json
from langchain_core.tools import tool
from datetime import datetime, timedelta
import requests
from typing_extensions import TypedDict,Annotated


@tool
def check_requests_to_approve(bearer_token: str):
    """

    Check the status of requests to approve in the HR system.
    Only use this when the user SPECIFICALLY asks to see the vacation requests they have to approve.
    

    Args:
        bearer_token (str): Bearer token for authentication.
    
    Returns:
        list: List of vacation requests to approve.

    

    """

    

    ## Fetch requests to approve
    response = requests.get(
        "https://api-dev.hrstudium.pt/vacations/requests-to-approve",
        headers={"company": "dev", "Authorization": "Bearer " + bearer_token}
    )
    if response.status_code == 200:
        data= response.json()

        filtered_requests=[
            {
                "id:": item["id"],
                "nome_completo":item["criador"]["nome_completo"],
                "datas": [
                        {
                            "data": d["data"],
                            "hora_inicio": d["hora_inicio"],
                            "hora_fim": d["hora_fim"]
                        }
                        for d in item["datas"]
                ],

            }
            for item in data
        ]

        return "Requests",filtered_requests
    
    else:
        print("Failed to fetch requests to approve:", response.status_code)
        return("No requests to approve")