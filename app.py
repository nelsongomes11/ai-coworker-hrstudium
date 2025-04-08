import os
from time import sleep
import streamlit as st
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain.tools import tool

from dotenv import load_dotenv
from datetime import datetime,timedelta,date
import requests
import json


load_dotenv()


def get_dates_and_weekdays_current_year():
    today = date.today()
    year = today.year
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    delta = timedelta(days=1)
    current = start_date
    dates_dict = {}

    while current <= end_date:
        dates_dict[current.isoformat()] = current.strftime("%A")
        current += delta

    return dates_dict

dates_dict = get_dates_and_weekdays_current_year()



if "is_logged" not in st.session_state:
    st.session_state["is_logged"]=False




def chat_page():


   

    if st.session_state["is_logged"]:


                


        # GET USER VACATIONS INFO

        response=requests.get('https://api-dev.hrstudium.pt/vacations',
            headers={
                "company":"dev",
                "Authorization":"Bearer "+st.session_state["access_token"]
            }
        )

        if response.status_code == 200:
                user_vacation_data = response.json()
                st.session_state.user_vacation_data = user_vacation_data

                
        else:
                try:
                    error_data=response.json()
                    error_message=error_data.get("message","Error getting user info about vacations.")
                except ValueError:
                    error_message="Invalid Response from Server"



        # GET USER INFO

        response = requests.get("https://api-dev.hrstudium.pt/users",
            headers={
                "company":"dev",
                "Authorization":"Bearer "+st.session_state["access_token"]
            }

        )

        if response.status_code == 200:
            user_data = response.json()
            st.session_state.user = user_data  

        else:
            st.error("Failed to fetch user data.")



        # GET HOLIDAYS

        response = requests.get("https://api-dev.hrstudium.pt/holidays",
            headers={
                "company":"dev",
                "Authorization":"Bearer "+st.session_state["access_token"]
            }
        )

        if response.status_code == 200:
            holidays_data = response.json()
            st.session_state.holidays = holidays_data
        else:
            st.error("Failed to fetch holidays data.")



        col1, col2, col3,col4 = st.columns([1,1,1,1])


        with col1:
            with st.container(border=True):
                    st.write("""**🕑 Dias Totais**""")
                    st.write(str(int(st.session_state.user_vacation_data["horas_totais"]/8)))

        with col2:
            with st.container(border=True):
                    st.write("""**🕑 Dias Pendentes**""")
                    st.write(str(int(st.session_state.user_vacation_data["horas_pendentes"]/8)))
            
        with col3:
            with st.container(border=True):
                    st.write("""**🕑 Dias Aprovados**""")
                    st.write(str(int(st.session_state.user_vacation_data["horas_aprovadas"]/8)))

        with col4:
            with st.container(border=True):
                    st.write("""**Saldo Disponível**""")
                    st.write(str(int(st.session_state.user_vacation_data["horas_por_marcar"]/8)))

            


    st.title("Chat Férias")



    #os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
    groq_api_key=os.getenv("GROQ_API_KEY")

    llm=ChatOpenAI(model="gpt-4o-mini")
    #llm=ChatGroq(model="gemma2-9b-it",groq_api_key=groq_api_key,temperature=1,)


    if st.session_state["is_logged"]:
        

        absence_types=requests.get('https://api-dev.hrstudium.pt/vacations/absences/types',
            headers={
                "company":"dev",
                "Authorization":"Bearer "+st.session_state["access_token"]

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

            -Extract the requested dates.

            -Determine whether the request is for vacation or another type of absence.

            -If it's an absence, ask for the specific type from {filtered_absence_types}, use the description and show all types.

            -If it is for vacation, don't ask anything related to absence.

            - Saturdays and Sundays can't be requested as vacation days.

            -Remove ALL the Saturdays and Sundays from the request, as the user doesn't work on those days.

            - If the user request multiple dates, and there are multiple weekends, remove all weekends from the request and only mention the week days from the asked dates.

            -If all validations pass, submit the request.

            -Confirm the request with the user.

        - Today's date ({datetime.now().strftime('%Y-%m-%d')}, {datetime.now().strftime('%A')})




        Current booking info is: {st.session_state.extracted_info}

        '''

        

        if "messages" not in st.session_state:
            if st.session_state["is_logged"]:
                coworker_message = "Olá, sou o novo assistente digital. Como posso te ajudar?"
            else:
                coworker_message = "Olá! Por favor faça login para poder marcar as suas férias e ausências!"
            
            st.session_state.messages = [
                {"role": "system", "content": coworker_system_prompt}, 
                {"role": "coworker", "content": coworker_message}
            ]
        
        if "request_confirmed" not in st.session_state:
             st.session_state["request_confirmed"] = False





        with st.sidebar:
            if st.session_state["is_logged"]:
                st.subheader("Olá, "+ st.session_state.user["primeiro_nome"]+"!")
                text_days = st.text_area(label="Dias", key="days", value=", ".join(st.session_state.extracted_info["dates"]))
                text_type = st.text_area(label="Type", key="type", value=st.session_state.extracted_info["type_leave"])
                text_absence_type = st.text_area(label="Absence Type", key="absence_type", value=st.session_state.extracted_info["type_absence"])

                
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            elif msg["role"] == "coworker":
                st.chat_message("coworker").write(msg["content"])

        if user_input:= st.chat_input(disabled=not st.session_state["is_logged"]):



            st.chat_message("user").write(user_input)
            st.session_state.messages.append({'role': 'user', 'content': user_input})
                

            model_messages = [SystemMessage(content=coworker_system_prompt)]
        
            

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


            confirmation_check_prompt = f"""
                Based on the following chat history, did the user **confirm** a vacation or absence request?

                {json.dumps(st.session_state["messages"], indent=2)}

                Reply only with: yes or no
            """

            confirmation_response = llm.invoke([HumanMessage(content=confirmation_check_prompt)])
            if "yes" in confirmation_response.content.lower():
                st.session_state["request_confirmed"] = True


            if st.session_state["request_confirmed"] is True:
                extract_prompt = f"""
                You are an assistant that extracts structured vacation request information 
                from a chat between a user and a HR assistant.

                Only return structured data if the user clearly confirmed their request.
                
                Chat history:
                {json.dumps(st.session_state["messages"], indent=2)}

                Respond only in this JSON format:
                {{
                    "confirmed": true,
                    "dates": ["YYYY-MM-DD", "YYYY-MM-DD"],
                    "type_leave": "vacation" or "absence",
                    "type_absence": "justified absence",  // optional if type_leave is "absence"
                }}
                """
                
                extraction = llm.invoke([HumanMessage(content=extract_prompt)])
                structured_info = json.loads(extraction.content)

                st.session_state["request_confirmed"] = False

                if structured_info.get("confirmed"):
                    st.session_state.extracted_info = {
                        "dates": structured_info["dates"],
                        "type_leave": structured_info["type_leave"],
                        "type_absence": structured_info.get("type_absence", "")
                    }
                




            print(model_messages)

            st.rerun()

            
    
    else:
        st.warning("Please log in to access the chat.")
    




    
def login_page():
    st.title("Login into HRStudium")   

    with st.form("login_form"):
        st.write("Login")
        username=st.text_input("Username",placeholder="user@gmail.com")
        password=st.text_input("Password",placeholder="*********",type="password")

        submitted=st.form_submit_button("Login")

        if submitted:

            response = requests.post(
                'https://api-dev.hrstudium.pt/login',
                headers={"company": "dev"},
                json={"username": username, "password": password}
            )

            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token") 

                if access_token:
                    st.success("Login successful!")
                    st.session_state["access_token"] = access_token  

                    # Reset Session States
                    st.session_state["is_logged"] = True

                    if "messages" in st.session_state:
                        del st.session_state["messages"]
                        
                    
                

                    

                else:
                    st.error("Login failed: No access token received.")
            else:
                try:
                    error_data=response.json()
                    error_message=error_data.get("message","Login Failed.")
                except ValueError:
                    error_message="Invalid Response from Server"

                st.error(error_message)    




pg=st.navigation([
    st.Page(login_page, title="Login", icon="🌐"),
    st.Page(chat_page, title="Chat", icon="🗨️"),
])

pg.run()

