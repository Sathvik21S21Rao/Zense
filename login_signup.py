import streamlit as st
from database import *
import json 
from streamlit_lottie import st_lottie
import re
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os,time

def send_email(recipient_email):
    load_dotenv()
    sender_email=os.environ.get("server_email_user")
    sender_password=os.environ.get("server_email_pass")
    subject = "Forgot Password"
    new_password=generate_password()
    change_forgot_password(recipient_email,new_password)
    message = f"Your new password is {new_password}. If you want to change the password, login and reset the password"
    msg = MIMEMultipart()

    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  

    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()

def forgot_password():
    st.title(":robot_face: Forgot Password")
    with st.form("Forgot Password"):
        email=st.text_input(label="Enter email")
        if st.form_submit_button("Submit"):
            if check_user(email):
                
                with st.spinner("Sending email"):
                    send_email(email)
                    time.sleep(2)
                    st.success("Email has been sent")
                    time.sleep(2)
                
                st.session_state.forgot=False
                st.experimental_rerun()

            else:
                st.error("Email does not exist")

def load_robot_lottie():
    with open("./style_files/robot.json") as fh:
        return json.load(fh)
    
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return True
    else:
        return False
def login():

    with st.container():
        st.title(":robot_face: - Login",)
        
        st.write('''<style> .container{
            color:coral;
        }</style>''',unsafe_allow_html=True)
        
        columns=st.columns(1)
        
        with columns[0]:
            # st_lottie(load_robot_lottie(),loop=True,)
            pass
        with columns[0]:
            with st.form("Login"):
                st.markdown('<div class="container"><i class="fa-solid fa-user"></i> Email</div>',unsafe_allow_html=True)
                email = st.text_input("email",label_visibility="collapsed")
                st.markdown('<div class="container"><i class="fa-solid fa-lock"></i> Password</div>',unsafe_allow_html=True)
                password = st.text_input("pass",type="password",label_visibility="collapsed")
                
                submit = st.form_submit_button("Submit",type="primary")
                
                if submit:
                    check=validate_login(email=email,password=password)
                    if check==False:
                        st.error("Password is incorrect")
                        
                    elif check is None:
                        st.error("Email does not exist.")
                    else:
                        st.session_state["user"]=check
                        st.session_state["logged_in"]=True
                        st.experimental_rerun()
            forget_password=st.button("Forgot password")
            if forget_password:
                st.session_state["forgot"]=True
                st.experimental_rerun()
            
    


def signup():
    st.title(":robot_face: - Sign up")
    st.markdown("<style>[data-testid='stForm']{border-color:#FC523D; display:flex; justify-content:center; flex-direction:column; flex:flex-wrap;}",unsafe_allow_html=True)
    st.markdown("<style>.stTextInput > label { color:coral;}</style> ",unsafe_allow_html=True)
    placeholder=st.empty()
    with placeholder.form("sign_up"):
        st.markdown('<div class="container"><i class="fa-solid fa-user"></i> Email</div>',unsafe_allow_html=True)
        email = st.text_input("email",label_visibility="collapsed")
        st.markdown('<div class="container"><i class="fa-solid fa-lock"></i> Password</div>',unsafe_allow_html=True)
        passw = st.text_input("pass",type="password",label_visibility="collapsed")
        st.markdown("<div class='container'>Confirm password</div>",unsafe_allow_html=True)
        confirm=st.text_input("## Confirm password","",type="password",label_visibility="collapsed")
        
        submit = st.form_submit_button("Submit")
        if submit:
            if not is_valid_email(email):
                st.error("Not a valid email")
            if passw!=confirm:
                st.error("Passwords don't match")
            else:
                user_id=create_user(email=email,password=passw)
                if user_id is None:
                    st.error("Email already exists")
                else:
                    st.session_state["user"]=user_id
                    st.session_state["logged_in"]=True
                    st.experimental_rerun()
def about():
    columns=st.columns(2)
    st.markdown("""<style>
        .header {
            background-color: #FF4B4B;
            text-align: center;
            padding: 2rem;
            color: white;
            border-radius: 10px;
        }
        .container1 {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background-color: #262730;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 10px;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        p {
            font-size: 1.1rem;
            line-height: 1.5;
            margin-bottom: 1.5rem;
        }
        h2 {
            color: #FF4B4B;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        ul {
            list-style-type: disc;
            padding-left: 1.5rem;
        }
        li {
            font-size: 1.1rem;
            line-height: 1.5;
        }
        </style>""",unsafe_allow_html=True)
    with columns[1]:
        st.markdown(
        """
        <div class="header">
        <h1>Welcome to File Insite</h1>
        <h3>Your Ultimate File Analysis and Question-Answering App</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    with columns[0]:
        st_lottie(json.load(open("./style_files/document.json")),loop=True,)
    st.markdown("""<div class="container1">
    <h2>About Us</h2>
    <p>
      File Insite is an innovative app designed to empower users with the ability to upload, analyze, and interact with various file types such as audio, video, PDFs, text files and youtube videos. Our mission is to provide you with powerful tools to extract insights from your files, answer questions, and gain valuable knowledge effortlessly.
    </p>
    <h2>Features</h2>
    <ul>
      <li>Upload a wide range of file types, including audio, video, PDFs, and text files.You can Upload youtube links as well </li>
      <li>Ask questions related to your uploaded files and receive answers in various formats.</li>
      <li>Retrieve answers in One-Line, Multi-Line, and Summary formats.</li>
      <li>Utilize the Offset feature in Multi-Line mode to explore context around each sentence.</li>
    </ul>
    <h2>Get Started</h2>
    <p>Experience the power of File Insite today by signing up and uploading your first set of files. Gain insights and answers in just a few clicks!</p>
  </div>""",unsafe_allow_html=True)