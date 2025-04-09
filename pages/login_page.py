from time import sleep
import streamlit as st
import requests

from pages.chat_page import chat_page

def login_page():

    """
        Login Page for the application.
    """


    st.title("Login Page")

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

                    print(st.session_state["is_logged"])
                    print(st.session_state["access_token"])

                   
                        
                    
                

                    

                else:
                    st.error("Login failed: No access token received.")
            else:
                try:
                    error_data=response.json()
                    error_message=error_data.get("message","Login Failed.")
                except ValueError:
                    error_message="Invalid Response from Server"

                st.error(error_message)    
                
