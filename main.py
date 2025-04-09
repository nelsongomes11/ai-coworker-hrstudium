import streamlit as st
from pages.login_page import login_page
from pages.chat_page import chat_page

pg=st.navigation(
    [
        st.Page(login_page, title="Login", icon="🌐"),
        st.Page(chat_page, title="Chat", icon="🗨️"),
    ]
)

pg.run()