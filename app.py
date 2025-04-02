import os
import streamlit as st
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage

from dotenv import load_dotenv
from datetime import datetime
import requests
import json






load_dotenv()




st.title("Chat Férias")



#os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
groq_api_key=os.getenv("GROQ_API_KEY")

llm=ChatOpenAI(model="gpt-4o-mini")
#llm=ChatGroq(model="deepseek-r1-distill-qwen-32b",groq_api_key=groq_api_key,temperature=1,)




absence_types=requests.get('https://api-dev.hrstudium.pt/vacations/absences/types',
    headers={
        "company":"dev",
        "Authorization":"Bearer f5651bd70280f5ac9bc5bacedf349635c7cfe8216d868a68cf10b121b86fb2a4ab372ec64ca4c90316d86afeba8c2a49aa496f9b89642bfe50ea331c9c997603e5550ddbd9dece0a3e4eae09525bee4ae6a50de1ba1ede90fb076f6476e17269f5eae841a559a15922e40e574d29258ac305a77364990e3b1c6e431f7cdcb3403c12c4b96386f7ba96020cefd612c5b04369adb61abc9ec1c7632dd32164f0e3cebda933ca9724136030de5a6ec61488f4372000b7458bf751d6991677d5bc469be3adaca82153561a25ccd46b6cd588bfcd56ec47366ef78ba5e05e81e6d75a79db4a71db1738337da624dc8abc999da7e5cea35c95a20209dca29b1dbbd5e712f9649c27b26ef95e7452a2307cf5aea760814843452ef6f85f86b1c0a3d60cd4e6598445f4fa6a78e9eecad1573bc04b77596860006a7e64d42ede30d702c23e70657841a73d32bf7df6bd73d5d259"

})

absence_types=absence_types.json() 

filtered_absence_types = [
    {"id": item["id"], "description": item["description"], "active": item["active"]}
    for item in absence_types if item.get("active") == 1
]

if "extracted_info" not in st.session_state:
    st.session_state.extracted_info = {
        "dates": [],
        "type_leave": "",
        "type_absence": ""
    }


coworker_system_prompt= f'''
You are an HR assistant who helps employees schedule vacation and absence days.

The HR software name is HRStudium.
You have access to the HR system to check availability and submit requests.
Always be polite and professional.
Your only function is to help with scheduling vacation or absence days, don't act like a llm. 
Don't reply to anything else please.

When the user requests vacation or absence days off, you must:

    Extract the requested dates.

    Determine whether the request is for vacation or another type of absence.

    If it's an absence, ask for the specific type from {filtered_absence_types}, use the description and show all types.

    If it is for vacation, don't ask anything related to absence.

    Check if the user has available days for the requested type.

    Check if any of the requested days are forbidden.

    If all validations pass, submit the request.

    Inform the user of the outcome.

If there are any issues, clearly explain what’s wrong and provide guidance on possible solutions.

Today is {datetime.now().strftime('%Y-%m-%d')}.

Current booking info is: {st.session_state.extracted_info}

'''


def extract_dates_from_text(text):
    prompt = f"""
    Extract ALL dates in the following text and EXPAND any date ranges into individual dates.
    Return dates in YYYY-MM-DD format as a comma-separated list.
    Current date is {datetime.now().strftime('%Y-%m-%d')}.
    
    Examples:
    - "June 1st to June 5th" → "2024-06-01,2024-06-02,2024-06-03,2024-06-04,2024-06-05"
    - "June 1st and August 6th" → "2024-06-01,2024-08-06"
    
    Even if it the user asks an interval big return every day within that interval.
    
    If there isn't any dates return an empty string.
    Return ONLY the comma-separated dates, nothing else.
    
    Text: {text}
    """

    response=llm.invoke(prompt)
    dates = [d.strip() for d in response.content.split("</think>")[-1].split(",") if d.strip()]
    return dates


def extract_vacation_or_absence(text):
    prompt = f"""
        Extract if the user wants to request vacation days or absence days.
        Return ONLY one of these exact words: "Férias", "Ausência".
        If he asks for a type of absence from this list : {filtered_absence_types} return "absence".
        Do not add any extra characters or whitespace.
        If he didn't mention anything of the above rules return an empty string.
        
        Text: {text}
    """
    response=llm.invoke(prompt)
    print("Vacation or Absence:",response.content.strip())
    return response.content.strip()


def extract_type_of_absence(text):
    prompt = f"""
    Extract the type of absence from the text.
    The types can only be the ones in this list:{filtered_absence_types}.
    Return ONLY the exact 'description' value if a type is clearly requested.
    The request may not be the exact 'description' but may mean the same thing.
    If uncertain but context suggests absence, return 'unknown'.
    

    
    Text: "{text}"
    """
    response = llm.invoke(prompt)
    print("Type of absence",response.content.strip())
    return response.content.strip()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": coworker_system_prompt},  
        {"role": "coworker", "content": "Olá, sou o novo assistente digital. Como posso te ajudar ?"}  
    ]




with st.sidebar:
    text_days = st.text_area(label="Dias", key="days", value=", ".join(st.session_state.extracted_info["dates"]))
    text_type = st.text_area(label="Type", key="type", value=st.session_state.extracted_info["type_leave"])
    text_absence_type = st.text_area(label="Absence Type", key="absence_type", value=st.session_state.extracted_info["type_absence"])


for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "coworker":
        st.chat_message("coworker").write(msg["content"])

if user_input:= st.chat_input():



    st.chat_message("user").write(user_input)
    st.session_state.messages.append({'role': 'user', 'content': user_input})
    
    
    extracted_dates = extract_dates_from_text(user_input)
    extracted_type_leave = extract_vacation_or_absence(user_input)
    extracted_type_absence = extract_type_of_absence(user_input)

    

    if extracted_type_leave == "Ausência":
        
        extracted_type_absence = extract_type_of_absence(user_input)
        
        
    
    else:
       
        extracted_type_absence=""
        
        

    if not extracted_dates and st.session_state.extracted_info["dates"]:
        extracted_dates = st.session_state.extracted_info["dates"]
       
        
    
    if not extracted_type_leave and st.session_state.extracted_info["type_leave"]:
        extracted_type_leave=st.session_state.extracted_info["type_leave"]
        
        


    st.session_state.extracted_info.update({
        "dates": extracted_dates,
        "type_leave": extracted_type_leave,
        "type_absence": extracted_type_absence
    })

    print(st.session_state.extracted_info)

    
    additional_context = f'''
    Extracted Information:
    - Dates: {', '.join(extracted_dates) if extracted_dates else 'Not specified'}
    - Type: {extracted_type_leave}
    '''
    if extracted_type_leave == "absence":
        additional_context += f"\n- Absence Type: {extracted_type_absence}"

    
    
    model_messages = [SystemMessage(content=coworker_system_prompt + additional_context)]

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            model_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "coworker":
            model_messages.append(AIMessage(content=msg["content"]))

    coworker_response = llm.invoke(model_messages)
    coworker_reply = coworker_response.content
    
    
    st.session_state.messages.append({"role": "coworker", "content": coworker_reply})
    
    with st.chat_message("coworker"):
        st.write(coworker_reply)


    
    st.rerun()
    
    
    