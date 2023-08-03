import streamlit as st
from audio_recorder_streamlit import audio_recorder
from PyPDF2 import PdfReader
from sim import *
from audio import *
import pickle
import re

def valid_link (link):
    
    youtube_pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?([a-zA-Z0-9_-]+)"
    match = re.match(youtube_pattern, link)
    if match and match.group(1):
        return True
    else:
        return False
def save_uploaded_file(text,uploaded_file):
    with open(f"./{text}/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def login():

    with st.container():
        st.title(":robot_face: - Login")
        st.markdown("<style>[data-testid='stForm']{border-color:coral; display:flex; justify-content:center; flex-direction:column; flex:flex-wrap;}",unsafe_allow_html=True)
        st.markdown("<style>.stTextInput > label { color:#fc0849;}</style> ",unsafe_allow_html=True)
        placeholder = st.empty()
        actual_email = "email"
        actual_password = "password"

        # Insert a form in the container
        with placeholder.form("login"):
            email = st.text_input("## Email :email:")
            password = st.text_input("## Password 🔑", type="password")
            submit = st.form_submit_button("Submit",)
            if submit:
                st.session_state["logged_in"]=True
                st.experimental_rerun()
    


def signup():
    st.title(":robot_face: - Sign up")
    st.markdown("<style>[data-testid='stForm']{border-color:coral; display:flex; justify-content:center; flex-direction:column; flex:flex-wrap;}",unsafe_allow_html=True)
    st.markdown("<style>.stTextInput > label { color:#fc0849;}</style> ",unsafe_allow_html=True)
    placeholder=st.empty()
    with placeholder.form("sign_up"):
        email=st.text_input("## Email :email:","")
        passw=st.text_input("## Password 🔑","",type="password")
        confirm=st.text_input("## Confirm password","",type="password")
        if passw!=confirm:
            st.error("Passwords don't match")
        submit = st.form_submit_button("Submit")
        if submit:
            st.session_state["logged_in"]=True
            return

def main():
    html='''<meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0">'''
    st.set_page_config(
        page_title="AI Chatbot",
        page_icon=":robot_face:",
        layout="wide",
    )
    custom_css = """
        <style>
        .stRadio > div >label {
            margin-bottom: 10%; 
        }
        </style>
        """
    #st.markdown(html,unsafe_allow_html=True)
    st.markdown(custom_css, unsafe_allow_html=True)

    st.markdown('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">', unsafe_allow_html=True)
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"]=False 
    if not st.session_state["logged_in"]:
        selected_option = st.sidebar.radio("#### Go to", ("Login", "Sign Up","About"),index=0)
        if selected_option=="Login":
            login()
        elif selected_option=="Sign Up":
            signup()
    else:
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"]=[]
            st.session_state["context_chat"]=[]
        chat_page()



def chat_page():

    with st.sidebar:
        
        files=st.file_uploader("#### Upload Your Documents:",accept_multiple_files=True,type=["mp3","pdf","txt","mp4"])
        num_inputs = st.number_input("Enter the number of youtube Links:", min_value=0, max_value=5, step=1, value=0)
        inputs = []
        i=0
        while i<num_inputs:
            input_label = f"Enter link {i+1}:"
            text_input = st.text_input(input_label, "")
            inputs.append(text_input)
            i+=1
            

        
        
        if st.button("Compute"):
            with st.spinner("Preparing..."):
                for link in inputs:
                    if not valid_link(link):
                        st.error(f"{link} is not a youtube link")

                        break
                else:
                    text=""
                    j=0
                    for link in inputs:
                        try:
                            text+=get_transcript(link)
                        except:
                            st.error(f"{link} does not have transcript")
                            break
                    else:
                        for i in range(len(files)):
                            print(files[i].type)
                            if files[i].type=="application/pdf":
                                text=text+get_pdf_text(files[i])+"."
                            elif files[i].type=="text/plain":
                                text=text+files[i].read().decode('utf-8')+"."
                            elif files[i].type=="audio/mpeg":
                                save_uploaded_file("audios",files[i])
                                x=audio_to_text(files[i].name)
                                text=text+x+"."
                            else:
                                save_uploaded_file("videos",files[i])
                                path=f"./videos/{files[i].name}"
                                au=video_to_audio(path,(path.replace("videos","audios")).replace("mp4","mp3"))
                                x=audio_to_text(files[i].name)
                                text=text+x+"."
                    
                            index,sentences,vectorizer=fill_context(text)
                            context_file=open("context.bin","ab")
                            d={"title":title_generator(text),"index":index,"text":text,"sentences":sentences,"chat_history":None}
                            # pickle.dump(d,context_file)
                            context_file.close()
                            st.session_state["text"]=text
                            st.session_state["index"]=index
                            st.session_state["sentences"]=sentences
                            st.session_state["vectorizer"]=vectorizer
                            st.session_state["chat_info"]=d
                            st.session_state["computed"]=True
        if st.button("Logout 🚪"):
            st.session_state.clear()
            st.experimental_rerun()
       

    button_container = st.empty()
    cols = button_container.columns([3.9,1])
    with cols[0]:
        st.title("AI Chatbot")
        st.write("Welcome to the AI Chatbot. Upload your documents and get answers!")
        st.session_state["option"]=st.selectbox("Type of answer:",("One Line","Multi Line","Summary"))
        input=""
        if st.session_state["option"]!="Summary":
            input=st.text_input("## Enter query","")
        if st.session_state.get("computed"):
            if st.session_state["option"]=="Summary":
                response=summary(st.session_state["text"])
                st.session_state["chat_history"].append({"question":"Give Summary","response":response.replace("\n","<br><br>")})
            elif input!="" and st.session_state["option"]=="Multi Line":
                p=None
                response,p=similarity_search(st.session_state["index"],input,st.session_state["sentences"],st.session_state["vectorizer"])
                response="\n".join(response)
                if response.strip()=="":
                    response="Could not find anything related"
                st.session_state["chat_history"].append({"question":input,"response":response.replace("\n","<br><br>")})
            elif input!="":
                response=one_line(st.session_state["text"],input)
                st.session_state["chat_history"].append({"question":input,"response":response.replace("\n","<br><br>")})
        
            st.session_state["chat_info"]["chat_history"]=st.session_state["chat_history"]
            for i in st.session_state["chat_history"]:
                with st.chat_message("user",):
                    st.write(i["question"],unsafe_allow_html=True)
                with st.chat_message("assistant"):
                    st.write(i["response"],unsafe_allow_html=True)

                # st.write(user_template.replace("{replace}",i["question"]),unsafe_allow_html=True)
                # st.write(bot_template.replace("{replace}",i["response"]),unsafe_allow_html=True)
    
    with cols[1].container():
        
        if st.button("#### New chat +"):
            pass
    



    pass

main()