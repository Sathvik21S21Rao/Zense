import requests
from pydub import AudioSegment
import os
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip

load_dotenv()
hf_token=os.environ.get("hf_token")

def video_to_audio(input_video_path, output_audio_path):
    video_clip = VideoFileClip(input_video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(output_audio_path)
    audio_clip.close()
    video_clip.close()


def mp3_to_wav(input_file, output_file):
    audio = AudioSegment.from_mp3(input_file)
    audio.export(output_file, format="wav")
    os.remove(f"{input_file}")

def query(filename,API_URL,headers):

    with open(filename, "rb") as f:
        data=f.read()
        response = requests.post(API_URL, headers=headers, data=data,json={"options":{"wait_for_model":True}})

    return response.json()

def chunks(filename):
    sound_file = AudioSegment.from_wav(filename)
    sound_file = sound_file.split_to_mono()[0]

    chunk_size = 10000*3 # milliseconds
    audio_chunks = [sound_file[i:i+chunk_size] for i in range(0, len(sound_file), chunk_size)]
    ctr=0

    for i, chunk in enumerate(audio_chunks):
        out_file = f"./audios/chunk{i}.wav"
        # print(f"exporting {out_file}")
        chunk.export(out_file, format="wav")
        ctr=i
    
    return ctr

def audio_to_text(filename):

    mp3_to_wav(f"./audios/{filename}",f"./audios/{filename.split('.')[0]}.wav")
    API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v2"
    headers = {"Authorization": f"Bearer {hf_token}"}

    ctr=chunks(f"./audios/{filename.split('.')[0]}.wav")
    text=""
    
    for i in range(ctr+1):
        output = query(f"./audios/chunk{i}.wav",API_URL,headers)
        print(output)
        text+=output.get("text","")
    files=os.listdir("./audios")
    for i in files:
        if i.endswith(".wav"):
            os.remove(f"./audios/{i}")
    return text