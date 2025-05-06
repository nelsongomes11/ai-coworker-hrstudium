from operator import itemgetter
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json


from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from prompts.system_prompts import coworker_system_approve_prompt

from langchain_community.chat_message_histories import StreamlitChatMessageHistory


import requests
from datetime import datetime


from tools.check_approve_requests import check_requests_to_approve
from tools.request_decision import request_decision






def get_chat_model_approve(bearer_token,user_input):

    
    llm=ChatOpenAI(model="gpt-4.1-mini")
    llm_with_tools=llm.bind_tools([check_requests_to_approve,request_decision])

    history = StreamlitChatMessageHistory(key="messages_approve")

    chat_prompt=ChatPromptTemplate(
        [
            ("system",coworker_system_approve_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human","{input}")
        ]
    )

    

    chain=  {"input": itemgetter("input"),"history": itemgetter("history"),}  | chat_prompt | llm_with_tools

    
    first_response=chain.invoke({
                  "input":user_input,
                  "history": history.messages
                })
    


    history.add_user_message(user_input)
    if first_response.content:
        history.add_ai_message(first_response.content)

    if first_response.tool_calls:
        print("Used tools!")
        for tool_call in first_response.tool_calls:

            tool_name=tool_call["name"]


            if tool_name=="check_requests_to_approve":
                
                tool_args = tool_call["args"]
                tool_args["bearer_token"] = bearer_token
                print(f"Invoking {tool_name} with args: {tool_args}")
                tool_result = check_requests_to_approve.invoke(tool_args)

                print(f"Tool used : {tool_name}; Result: {tool_result}")

                
            

                second_response = chain.invoke({
                        "input": f"Os pedidos para aprovação são: {tool_result}. É importante mostrar os IDs dos pedidos. Se existirem datas, mostra tudo em formato de tabela.",
                        "history": history.messages,
                    
                    })

                history.add_ai_message(second_response.content)
                print(second_response)
                return second_response.content
            
            elif tool_name=="request_decision":
                
                tool_args = tool_call["args"]
                tool_args["bearer_token"] = bearer_token
                print(f"Invoking {tool_name} with args: {tool_args}")
                tool_result = request_decision.invoke(tool_args)

                print(f"Tool used : {tool_name}; Result: {tool_result}")

                
            

                second_response = chain.invoke({
                        "input": f"A mensagem ao submeter pedido foi : {tool_result}.",
                        "history": history.messages,
                    
                    })

                history.add_ai_message(second_response.content)
                print(second_response)
                return second_response.content
            
           
            

            



        return "Não consegui processar os resultados da tool"
           

    else:
        print("Didn't use tools!")
        return first_response.content
    
    

