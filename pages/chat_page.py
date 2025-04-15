import requests
import streamlit as st

from models.chat_model import get_chat_model


def chat_page():

    """
        Chat Page for the application.
        This page is only accessible after logging in.
        It displays the chat interface and allows users to send messages.
        
    """

    st.title("Chat Page")


    if "is_logged" not in st.session_state:
      st.session_state["is_logged"]=False
      

    if st.session_state["is_logged"]:

   
       

        # Fetch current user data

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


        # Sidebar info 


            ## Get user vacations data

        response=requests.get("https://api-dev.hrstudium.pt/vacations",
            headers={
                "company":"dev",
                "Authorization":"Bearer "+st.session_state["access_token"]
            }
        )

        if response.status_code == 200:
            user_data=response.json()
            st.session_state.vacations=user_data
        else:
            st.error("Failed to fetch user vacations data.")



        with st.sidebar:
            st.header("Olá, "+st.session_state.user["primeiro_nome"]+"!")
            st.write("Saldo de férias: "+str(int(st.session_state.vacations["horas_por_marcar"]/8)))
            st.write("Dias Totais: "+str(int(st.session_state.vacations["horas_totais"]/8)))
            st.write("Dias Aprovados: "+str(int(st.session_state.vacations["horas_aprovadas"]/8)))
            st.write("Dias Pendentes: "+str(int(st.session_state.vacations["horas_pendentes"]/8)))
            
            st.markdown("##")
            st.markdown("##")

            uploaded_files= st.file_uploader(
                "Escolha um documento", accept_multiple_files=True
            )






        # Initialize message history

        if "messages" not in st.session_state:
            st.session_state.messages = []


        for msg in st.session_state.messages:
            
            st.chat_message(msg.type).write(msg.content)

        if user_input:=st.chat_input("Escreva a sua mensagem..."):

            st.chat_message("human").write(user_input)

            response_text=get_chat_model(
                st.session_state["access_token"],
                user_input,
                uploaded_files
            )

            st.chat_message("ai").write(response_text)
        
        
    

        


            
    
            















    else:
        st.warning("You need to log in first.")
        