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

        with st.sidebar:
            st.header("Olá, "+st.session_state.user["primeiro_nome"]+"!")

        # Initialize message history

        if "messages" not in st.session_state:
            st.session_state.messages = []


        for msg in st.session_state.messages:
            
            st.chat_message(msg.type).write(msg.content)

        if user_input:=st.chat_input("Escreva a sua mensagem..."):

            st.chat_message("human").write(user_input)

            response_text=get_chat_model(
                st.session_state["access_token"],
                user_input
            )

            st.chat_message("ai").write(response_text)



            
    
            















    else:
        st.warning("You need to log in first.")
        