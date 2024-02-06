import uuid
import moviepy.editor as mp
from pytube import YouTube
import assemblyai as aai
from gtts import gTTS
import google.generativeai as genai
import cv2
from PIL import Image
import os

os.environ["GOOGLE_API_KEY"] = ""
os.environ["AAI_API_KEY"] = ""


AUDIO_DIR_NAME = "audio"
VIDEO_DIR_NAME = "video"
IMAGE_DIR_NAME = "images"
[os.makedirs(dn,exist_ok=True) for dn in [AUDIO_DIR_NAME,VIDEO_DIR_NAME,IMAGE_DIR_NAME]]
gen_ai_api_key = os.environ["GOOGLE_API_KEY"]
aai_api_key = os.environ["AAI_API_KEY"]
genai.configure(api_key=gen_ai_api_key)
model = genai.GenerativeModel("gemini-pro")
multi_model = genai.GenerativeModel("gemini-pro-vision")
chat = model.start_chat(history=[])


def get_image_content(img_file_path):
    
    out=multi_model.generate_content(("extract all content and infomation   ",
                            Image.open(img_file_path) ))
    
    return out
    
    
def get_visual_content(video_path):
    final_content = ""
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))*3
    counter = 1
    while True:
        suc,frame = cap.read()
        if not suc:break
        if counter%fps == 0:
            img_path = os.path.join(IMAGE_DIR_NAME,f"{uuid.uuid1()}.jpg")
            cv2.imwrite(img_path,frame)
            
            img_con = get_image_content(img_path)
            try:
                for chunk in img_con:
                    final_content+=chunk.text
            except:
                print("================================================")
                print([i for i in img_con])
                print("================================================")
        counter+=1
    return final_content
            

def text_to_speech(text, language='en', output_file='output.mp3'):
    """
    Converts the given text to speech and saves it as an audio file.

    Parameters:
        text (str): The text to be converted to speech.
        language (str): The language of the text (default is 'en' for English).
        output_file (str): The filename for the output audio file (default is 'output.mp3').
    """
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(output_file)


def resize_video(input_video_path, output_video_path,frame_width=600,frame_height=600):
    print(f"{input_video_path=}")
    cap = cv2.VideoCapture(input_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    # writer = cv2.VideoWriter(output_video_path,cv2.VideoWriter_fourcc(*"H264"),fps,(frame_width,frame_height))
    fourcc = 0x00000021 
    writer = cv2.VideoWriter(output_video_path,fourcc,fps,(frame_width,frame_height))
    
    while True:
        suc,frame = cap.read()
        if not suc: break
        writer.write(cv2.resize(frame,(frame_width,frame_height)))
        
    writer.release()
    cap.release()

def convert_video_to_audio(video_file_path:str, audio_file_path:str)->bool:
    
    try:
        
        if not os.path.isfile(audio_file_path):
        
            clip = mp.VideoFileClip(video_file_path)
            clip.audio.write_audiofile(audio_file_path)
        return True
    
    except Exception as e:
        
        print(f"ERROR: {e}")
        return False


def file_downloader(bytes_data,file_path):
    
    try:
        with open(file_path,"wb") as f:
            f.write(bytes_data)
        return True
    except Exception as e:
        print(f"ERROR : TO WRITE A FILE ")
        return False

def download_youtube_video(video_url,audio_or_video="audio"):
    
    try:
    
        yt = YouTube(video_url)
        file_path = None
        if audio_or_video=="audio":
            audio = yt.streams.filter(only_audio = True).first()

            file_path = audio.download(AUDIO_DIR_NAME)
        else:
            video = yt.streams.filter(only_video = True).first()

            file_path = video.download(VIDEO_DIR_NAME)
        
        return file_path
    except Exception as e:
        return False

def get_content(audio_path:str):

    os.environ["AAI_API_KEY"] 
    aai.settings.api_key = aai_api_key
    transcriber = aai.Transcriber()

    transcript = transcriber.transcribe(audio_path)
    
    return transcript.text


def get_generated_response(ques):
    response = chat.send_message(ques,stream=True)
    return response
