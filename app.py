import os
import streamlit as st
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage

from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

st.title("Chat Férias")




groq_api_key=os.getenv("GROQ_API_KEY")
llm=ChatGroq(model="Gemma2-9b-It",groq_api_key=groq_api_key)


coworker_system_prompt= f'''
You are an HR assistant who helps employees schedule vacation and absence days.

The HR software name is HRStudium.
You have access to the HR system to check availability and submit requests.
Always be polite and professional.

When the user requests vacation or absence days off, you must:

    Extract the requested dates.

    Determine whether the request is for vacation or another type of absence.

    If it's an absence, ask for the specific type (e.g., sick leave, personal leave, bereavement).

    Check if the user has available days for the requested type.

    Check if any of the requested days are forbidden.

    If all validations pass, submit the request.

    Inform the user of the outcome.

If there are any issues, clearly explain what’s wrong and provide guidance on possible solutions.

Today is {datetime.now().strftime('%Y-%m-%d')}.

'''


def extract_dates_from_text(text):
    prompt = f"""
    Extract ALL dates in the following text and EXPAND any date ranges into individual dates.
    Return dates in YYYY-MM-DD format as a comma-separated list.
    Current date is {datetime.now().strftime('%Y-%m-%d')}.
    
    Examples:
    - "June 1st to June 5th" → "2024-06-01,2024-06-02,2024-06-03,2024-06-04,2024-06-05"
    - "June 1st and August 6th" → "2024-06-01,2024-08-06"
    
    Return ONLY the comma-separated dates, nothing else.
    
    Text: {text}
    """

    response=llm.invoke(prompt)
    dates = [d.strip() for d in response.content.split(",") if d.strip()]
    return dates


def extract_vacation_or_absence(text):
    prompt = f"""
        Extract if the user wants to request vacation days or absence days.
        Return ONLY one of these exact words: "vacation", "absence", or "" (empty string).
        If he hasn't asked for any of those return the string empty.
        Do not add any extra characters or whitespace.
        
        Text: {text}
    """
    response=llm.invoke(prompt)
    return response.content.strip()


def extract_type_of_absence(text):
    prompt = f"""
    Extract the specific type of absence being requested from the following text.
    Choose ONLY from these valid types: sick leave, personal leave, bereavement, family emergency, medical appointment.
    If no valid type is mentioned, return "unknown".
    
    Text: "{text}"
    
    Return ONLY the absence type as a single phrase or "unknown".
    """
    response = llm.invoke(prompt)
    return response.content.strip()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": coworker_system_prompt},  
        {"role": "coworker", "content": "Hey, how can i help you ?"}  
    ]


if "extracted_info" not in st.session_state:
    st.session_state.extracted_info = {
        "dates": [],
        "type_leave": "",
        "type_absence": ""
    }

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

    if extracted_type_leave == "absence":
        
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

    print(st.session_state.extracted_info)
    
    st.rerun()
    
    
    