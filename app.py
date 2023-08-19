import streamlit as st
from chat import *
from login_signup import *
def main():

    st.set_page_config(
        page_title="AI Chatbot",
        page_icon=":robot_face:",
        layout="centered",
        initial_sidebar_state="expanded"
        
    )
    # st.markdown(html,unsafe_allow_html=True)
    st.markdown(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    """,
    unsafe_allow_html=True,
)
    st.write('''<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"><style>[data-baseweb='tab']{ width:120%; }footer{ visibility:collapse; }''',unsafe_allow_html=True)
    # st.write('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">', unsafe_allow_html=True)
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"]=False 
    if st.session_state.get("forgot"):
        forgot_password()
        
    elif not st.session_state["logged_in"]:
        tabs=st.tabs(["**About**","**Login**","**Sign up**"],)
        with tabs[0]:
            about()
        with tabs[1]:
            login()
        with tabs[2]:
            signup()
        
    else:
        st.markdown('<meta name="viewport" content="width=device-width, initial-scale=1.0">',unsafe_allow_html=True)
        st.session_state["loaded"]=False
    
        chat_page()
if __name__=="__main__":
    main()