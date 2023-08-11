import numpy as np
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
import faiss
import requests
from dotenv import load_dotenv
import os
from youtube_transcript_api import YouTubeTranscriptApi
import nltk 
import re
import neuralcoref
import spacy 
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('stopwords')
nltk.download('punkt')
load_dotenv()
hf_token=os.environ.get("hf_token")

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

def remove_punctuation(text):
    text_without_punct = re.sub(r'[^\w\s]', '', text)
    return text_without_punct

def remove_stopwords(query):
    lemmatizer=WordNetLemmatizer()
    query=remove_punctuation(query)
    tokens=word_tokenize(query)
    stop_words=set(stopwords.words("english"))
    normalized_tokens = [token for token in tokens if token not in stop_words]
    normalized_tokens=[lemmatizer.lemmatize(token) for token in normalized_tokens]
    # Join the tokens back into a sentence
    normalized_query = ' '.join(normalized_tokens)
    return normalized_query


def fill_context(text):
    document=text.lower().replace("\n","")
    document=neural_coreference(document)
    sentences=sent_tokenize(document)
    sentences1=[]
    for i in sentences:
        sentences1.append(remove_stopwords(i))
    vectorizer = TfidfVectorizer()
    context=vectorizer.fit_transform(sentences1).toarray()
    index = faiss.IndexFlatL2(context.shape[1])
    index.add(context)
    return index,sentences,vectorizer

def similarity_search(index,q,sentences,vectorizer,offset,p=None):
    
    if p is None:
        q=q.lower()
        q=remove_stopwords(q)
        p=vectorizer.transform([q]).toarray() 
    i=1
    while i<len(sentences):
        distances, indices = index.search(p, i)
        i+=1
        if distances.std()>0.07:
            break
    
    nearest_sentences = []
    similar_indices=indices[0][distances[0]<1.5]
    #print(distances)
    most_similar=similar_indices[0]
    similar_indices=list(similar_indices)
    similar_indices.sort()
    
    for i in similar_indices:
        nearest_sentences.append(sentences[i])
        
    ind=similar_indices.index(most_similar)
    nearest_sentences=["<b style='color:#ff4b4b'>"+nearest_sentences[i].strip().capitalize()+" </b>" for i in range(len(nearest_sentences))]
    nearest_sentences[ind]="<i>"+nearest_sentences[ind]+"   </i>"
    similar_indices=[similar_indices[i] for i in range(len(similar_indices)) if nearest_sentences[i]]
    
    for i in range(len(similar_indices)):
        para=""
        
        for j in range(similar_indices[i]-offset,similar_indices[i]):
            if j>=0:
                try:
                    para+=sentences[j].strip().capitalize()+" "
                except:
                    pass 
        nearest_sentences[i]=para+nearest_sentences[i]
        para=""
        for j in range(similar_indices[i]+1,similar_indices[i]+offset+1):
            try:
                para+=sentences[j].strip().capitalize()+" "
            except:
                pass 
        nearest_sentences[i]+=para
    return nearest_sentences,p

        
def summary(text):
    
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {hf_token}"}

    def query(payload,headers,api_url):
        response = requests.post(api_url, headers=headers, json=payload)
        return response.json()
    while True:
        output = query({
            "inputs":text,
            "options":{"wait_for_model":True}
        },headers=headers,api_url=API_URL)
        try:
            return output[0]["summary_text"]
        except:
            continue

def one_line(text,q):

    def query(payload):
        API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
        headers = {"Authorization": f"Bearer {hf_token}"}
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    while True:
        output = query({
            "inputs": {
                "question": q,
                "context": text
            },
            "options":{"wait_for_model":True},})
        if output.get("error") is None:
            break
    print(output)
    return output.get("answer")

def title_generator(text):

    API_URL = "https://api-inference.huggingface.co/models/czearing/article-title-generator"
    headers = {"Authorization": "Bearer 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"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    while True:
        output = query({
            "inputs": text,
            "options":{"wait_for_model":True}
        })
        if "error" not in output:
            break
    print(output)
    return output[0]["generated_text"]


def punctuate(text):
    API_URL = "https://api-inference.huggingface.co/models/oliverguhr/fullstop-punctuation-multilang-large"
    headers = {"Authorization": f"Bearer {hf_token}"}
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    while True:
        output = query({
            "inputs": text,
        })
        if "error" not in output:
            break
    punctuated_text=""
    for i in output:
        punctuated_text=punctuated_text+i["word"]+i["entity_group"]+" "
    return punctuated_text.replace("0","")

def neural_coreference(text):
    nlp = spacy.load("en_core_web_sm")
    coref = neuralcoref.NeuralCoref(nlp.vocab)
    nlp.add_pipe(coref, name='neuralcoref')
    doc = nlp(text)
    return doc._.coref_resolved

def get_transcript(url):
    try:
        a=url.index("v=")
        try:
            b=url.rindex("&t")
        except:
            b=len(url)
        video_id=url[a+2:b]
        transcript=YouTubeTranscriptApi.get_transcript(video_id=video_id)
        text=""
        for item in transcript:
            text=text+item["text"]+" "
            text=text.replace("\n"," ")
        space_index=[]
        for i in range(len(text)):
            if text[i]==" ":
                space_index.append(i)
        k=0
        space_index.insert(0,0)
        n=len(space_index)
        corrected_text=""
        while k+250<n:
            corrected_text+=punctuate(text[space_index[k]:space_index[k+250]])
            k=k+250
        corrected_text+=punctuate(text[space_index[k]:])
        return corrected_text
    except:
        return None
        

                


