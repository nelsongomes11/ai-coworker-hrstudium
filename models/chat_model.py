from operator import itemgetter
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json


from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from prompts.system_prompts import coworker_system_prompt

from langchain_community.chat_message_histories import StreamlitChatMessageHistory


import requests
from datetime import datetime


from tools.extract_dates import extract_dates


def get_chat_model(bearer_token,user_input):

    absence_types=requests.get('https://api-dev.hrstudium.pt/vacations/absences/types',
            headers={
                "company":"dev",
                "Authorization":"Bearer "+bearer_token

        })

    absence_types=absence_types.json() 

    filtered_absence_types = [
            {"id": item["id"], "description": item["description"], "active": item["active"]}
            for item in absence_types if item.get("active") == 1
        ]
    
    llm=ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools=llm.bind_tools([extract_dates])

    history = StreamlitChatMessageHistory(key="messages")

    chat_prompt=ChatPromptTemplate(
        [
            ("system",coworker_system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human","{input}")
        ]
    )

    

    chain=  {"input": itemgetter("input"),"filtered_absence_types":itemgetter("filtered_absence_types"),"date": itemgetter("date"),"history": itemgetter("history"),}  | chat_prompt | llm_with_tools

    
    first_response=chain.invoke({"input":user_input,
                  "filtered_absence_types": f"{filtered_absence_types}",
                  "date": f"{datetime.now().strftime('%Y-%m-%d')}, {datetime.now().strftime('%A')}",
                  "history": history.messages
                })
    


    history.add_user_message(user_input)
    history.add_ai_message(first_response.content)

    if first_response.tool_calls:
        print("Used tools!")
        for tool_call in first_response.tool_calls:
            tool_name=tool_call["name"]

            if tool_name=="extract_dates":
                
                tool_result=extract_dates.invoke(tool_call["args"])

                print(f"Tool used : {tool_name}; Result: {tool_result}")

            

                second_response = chain.invoke({
                        "input": f"Aqui estão os dados extraídos: {tool_result} com a tool {tool_name}",
                        "filtered_absence_types": f"{filtered_absence_types}",
                        "date": f"{datetime.now().strftime('%Y-%m-%d')}, {datetime.now().strftime('%A')}",
                        "history": history.messages,
                    
                    })

                history.add_ai_message(second_response.content)
                print(second_response.content)
                return second_response.content

        return "Não consegui processar os resultados da tool"
           

    else:
        print("Didn't use tools!")
        return first_response.content
    
    

