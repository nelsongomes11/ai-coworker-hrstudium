import streamlit as st
from pages.login_page import login_page
from pages.chat_page import chat_page
from pages.approve_chat import approve_page


# Logo and title

st.logo("./assets/logo-hrstudium.png")

st.markdown("""
    <style>
            img[data-testid="stLogo"] {
            height: 5rem;
}
            
    </style>
    """, unsafe_allow_html=True)




pg=st.navigation(
    [
        st.Page(login_page, title="Login", icon="🌐"),
        st.Page(chat_page, title="Marcação de Férias e Ausências", icon="📆"),
        st.Page(approve_page, title="Aprovar Férias e Ausências", icon="🖊️"),
    ]
)

pg.run()