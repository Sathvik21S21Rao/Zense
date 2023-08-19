import streamlit as st
from sim import *
from audio import *
import pickle,json
from streamlit_option_menu import option_menu
import time
from database import *
from streamlit_lottie import st_lottie

def load_robot_lottie():
    with open("./style_files/robot.json") as fh:
        return json.load(fh)
def new_chat(user_id):
    timestamp = int(time.time())
    chat_id = f"chat_{user_id}_{timestamp}"
    return chat_id

def store_chat():
    if "chat_info" in st.session_state:
        with open("chats.bin","rb") as fh:
            try:
                chats=pickle.load(fh)
            except:
                chats={}
            if st.session_state["chat_info"]:
                chats.update({st.session_state["chat_id"]:st.session_state["chat_info"]})
        with open("chats.bin","wb") as fh:

            pickle.dump(chats,fh)
        st.session_state["loaded"]=False
        # st.session_state["chat_info"]={}
        # st.session_state["chat_id"]=new_chat(st.session_state["user"])
        # st.session_state["computed"]=False
        #print(st.session_state["chat_id"])
        
def clear():
    st.session_state["query"]=""
    

def chat_page():
    
    button_container = st.empty()
    cols = button_container.columns([1],gap="large")
    custom_style = """
            <style>
            .stselectbox {
                background-color: #f7f7f7;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            </style>
            """
    st.markdown(custom_style, unsafe_allow_html=True)
    if not st.session_state["loaded"]:
        st.session_state["previous_chats"]=[]
        st.session_state["previous_titles"]=[]
        st.session_state["chat_ids"]=[]
        with open("chats.bin","rb") as fh:
            try:
                d=pickle.load(fh)
            except:
                d={}
            for i in d:
                ctr=1
                if st.session_state["user"] in i:
                    if d[i].get("title") is not None:
                        st.session_state["chat_ids"].append(i)
                        st.session_state["previous_chats"].append(d[i])
                        if d[i]["title"] not in st.session_state["previous_titles"]:
                            st.session_state["previous_titles"].append(d[i]["title"])
                        else:
                            st.session_state["previous_titles"].append(d[i]["title"]+str(ctr))
                            ctr+=1
                            
            st.session_state["loaded"]=True

    
            
           


    with cols[0]:
        with st.expander("#### Menu"):
            main_menu=option_menu(menu_title=None,options=["Home","Reset Password","Delete","Logout"],icons=["house","person-fill-lock","trash-fill","power",],orientation="horizontal",key="main_menu")
    
        if main_menu=="Home":
            with st.sidebar:
                    
                    selected=option_menu(menu_title="Previous Chats",options=["New Chat"]+st.session_state["previous_titles"][::-1],icons=["plus-circle-fill"],key="selected")
                    
                    st.divider()
                    if st.session_state.get("menu_option")!=selected:
                        st.session_state["menu_option"]=selected
                        st.session_state["computed"]=False
                        if "chat_info" in st.session_state:
                            with open("chats.bin","rb") as fh:
                                try:
                                    chats=pickle.load(fh)
                                except:
                                    chats={}
                                chats.update({st.session_state["chat_id"]:st.session_state["chat_info"]})
                            with open("chats.bin","wb") as fh:
                                if chats[st.session_state["chat_id"]]:
                                    pickle.dump(chats,fh)
                            
                        
                    if st.session_state["menu_option"]=="New Chat":
                        st.session_state["computed"]=False
                        columns=st.columns((2,5,5))
                        robot=load_robot_lottie()
                        
                        files=st.file_uploader("#### Upload Your Documents:",accept_multiple_files=True,type=["mp3","pdf","txt","mp4"])
                        num_inputs = st.number_input("Enter the number of youtube Links:", min_value=0, max_value=5, step=1, value=0)
                        inputs = []
                        i=0
                        while i<num_inputs:
                            input_label = f"Enter link {i+1}:"
                            text_input = st.text_input(input_label, "",)
                            inputs.append(text_input)
                            i+=1
                            
                        if st.button("**Compute**",type="primary"):
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
                                            
                                            if files[i].type=="application/pdf":
                                                text=text+get_pdf_text(files[i])+"."
                                            elif files[i].type=="text/plain":
                                                text=text+files[i].read().decode('utf-8')+"."
                                            elif "audio" in files[i].type:
                                                save_uploaded_file("audios",files[i])
                                                x=audio_to_text(files[i].name)
                                                text=text+x+"."
                                            else:
                                                save_uploaded_file("videos",files[i])
                                                path=f"./videos/{files[i].name}"
                                                au=video_to_audio(path,f"./audios/{files[i].name}".replace("mp4","mp3"))
                                                x=audio_to_text(f"{files[i].name}".replace("mp4","mp3"))
                                                text=text+x+"."
                                    
                                        index,sentences=fill_context(text)
                                        d={"title":title_generator(text),"index":index,"text":text,"sentences":sentences,"chat_history":[]}
                                        st.session_state["chat_info"]=d
                                        st.session_state["chat_id"]=new_chat(st.session_state["user"])
                                        st.session_state["computed"]=True
                                        st.success("Computed")
                                        store_chat()
                                        st.session_state.menu_option="None"
                                        #selected=option_menu()
                                        st.experimental_rerun()
                                            
                    elif not st.session_state.computed:

                        i=st.session_state["previous_titles"].index(selected)
                        st.session_state["chat_id"]=st.session_state["chat_ids"][i]
                        st.session_state["chat_info"]=st.session_state["previous_chats"][i]
                        st.session_state["computed"]=True
                    if selected!="New Chat":
                        columns=st.columns([2.3,5])
                        with columns[1]:
                            st.info(f"You have selected {selected}. You can continue chatting",icon="ℹ️")
                        with columns[0]:
                            robot=load_robot_lottie()
                            st_lottie(robot,loop=True,speed=1)



            st.session_state["option"]=st.selectbox("Type of answer:",("One Line","Multi Line","Summary"))
            input=""
            if st.session_state["option"]=="Multi Line":
                columns=st.columns([5,2,2,1])
                with columns[0]:
                    input=st.text_input("## Enter query","",key="query")
                with columns[3]:
                    st.write("<br>",unsafe_allow_html=True)
                    run=st.button("**➤**",type="primary",help="Click to run",use_container_width=True)
                with columns[1]:
                    offset=st.number_input("Enter offset",min_value=0,max_value=3,)
                with columns[2]:
                    threshold=st.number_input("Enter threshold",min_value=1,max_value=10)

                
            elif st.session_state["option"]!="Summary":
                columns=st.columns([3,1])
                with columns[0]:
                    input=st.text_input("## Enter query","",key="query")
                with columns[1]:
                    st.write("<br>",unsafe_allow_html=True)
                    run=st.button("**➤**",type="primary",)
            st.divider()
            if st.session_state.get("computed"):
                if st.session_state["option"]=="Summary":
                    response=summary(st.session_state["chat_info"]["text"])
                    st.session_state["chat_info"]["chat_history"].append({"question":"Give Summary","response":response.replace("\n","<br><br>")})
                elif input!="" and st.session_state["option"]=="Multi Line" and run:
                    p=None
                    response,p=similarity_search(st.session_state["chat_info"]["index"],input,st.session_state["chat_info"]["sentences"],offset,threshold)
                    
                    response="\n".join(response)
                    if response.strip()=="":
                        response="Could not find anything related"
                    
                    st.session_state["chat_info"]["chat_history"].append({"question":input+"- Multi Line","response":response.replace("\n","<br><br>")})
                elif input!="" and run:
                    response=one_line(st.session_state["chat_info"]["text"],input)
                    if response is not None:
                        st.session_state["chat_info"]["chat_history"].append({"question":input+" -One Line","response":response.replace("\n","<br><br>")})
                    else:
                        st.error("Sorry some error occured. Please try again later")
                    
                if "chat_history" in st.session_state["chat_info"]:
                    # print(st.session_state["chat_info"]["sentences"])
                    for i in st.session_state["chat_info"]["chat_history"][::-1]:
                        with st.chat_message("user",):
                            st.write(i["question"],unsafe_allow_html=True)
                        with st.chat_message("assistant",):
                            st.write(i["response"],unsafe_allow_html=True)
        elif main_menu=="Reset Password":
            with st.form("reset"):
                old_password=st.text_input("Current password",type="password")
                new_password=st.text_input("New password",type="password")
                confirm_new_pass=st.text_input("Confirm password",type="password")
                if st.form_submit_button("Submit"):
                    if new_password!=confirm_new_pass:
                        st.error("Passwords don't match")
                    else:
                        if reset_password(st.session_state["user"],old_password,new_password):
                            st.success("Password changed")
                        else:
                            st.error("Incorrect current password")
        elif main_menu=="Delete":
            columns=st.columns(2,)
            with columns[0]:
                robot=load_robot_lottie()
                st_lottie(robot,loop=True,height=250,width=350)
            with columns[1]:
                st.markdown("<style></style>",unsafe_allow_html=True)
                st.warning("Doing this will permanently delete your account. Are you Sure?")
                if st.button("Yes",type="primary"):
                    delete(st.session_state["user"])
                    st.session_state.clear()
                    st.experimental_rerun()          


        elif main_menu=="Logout":
            if "chat_info" in st.session_state:
                with open("chats.bin","rb") as fh:
                    try:
                        chats=pickle.load(fh)
                    except:
                        chats={}
                    chats.update({st.session_state["chat_id"]:st.session_state["chat_info"]})
                with open("chats.bin","wb") as fh:
                    pickle.dump(chats,fh)
            st.session_state.clear()
            st.experimental_rerun()
            
