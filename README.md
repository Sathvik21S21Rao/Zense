# File Insite

## About
File Insite is an innovative app designed to empower users with the remarkable ability to seamlessly upload, thoroughly analyze, and dynamically interact with a wide array of file types. From audio and video to PDFs, text files, and even YouTube videos, our mission is clear: to equip you with potent tools that effortlessly extract insights, provide answers, and unlock valuable knowledge.

## Features
1) Summarization
2) One-Line answers
3) Multi Line answers
4) A well maintained chat history

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

## API models Used
| API model  |  Link |
| --------------- |-----------------------------|
| tinyroberta-squad2 | https://api-inference.huggingface.co/models/deepset/tinyroberta-squad2 |
| article-title-generator| https://api-inference.huggingface.co/models/czearing/article-title-generator |
| whisper-large-v2 |https://api-inference.huggingface.co/models/openai/whisper-large-v2 |
| fullstop-punctuation-multilang-large | https://api-inference.huggingface.co/models/oliverguhr/fullstop-punctuation-multilang-large |
   

## Deployment
To run the app:
``` bash
streamlit run app.py
```
## Demo
### Here is a small demo of the project
[!["File Insite"](https://img.youtube.com/vi/yDRwzJC0mfM/0.jpg)](https://www.youtube.com/watch?v=yDRwzJC0mfM "File Insite")
