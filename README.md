# File Insite

## About
Upload files and use the chatbot for question answering and summarization.

## Installation
1) Install the python modules required
``` bash
pip install -r requirements.txt
```
2) Download en_core_web_sm from spacy
``` bash
python3 -m spacy download en_core_web_sm
```
3) Install ffmpeg
Linux
``` bash
sudo apt-get install ffmpeg
```
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`hf_token` -  Hugging face api key

`mysql_user`

`mysql_password`

`server_email_user` email id

`server_email_pass` email app password

## Deployment
To run the app:
``` bash
streamlit run app.py
```
