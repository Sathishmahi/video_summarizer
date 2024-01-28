import streamlit as st
import os
import json
from main import (download_youtube_video, convert_video_to_audio, get_content, 
                  get_generated_response,file_downloader,text_to_speech,get_visual_content,resize_video)


audio_dir_name = "audio"
video_dir_name = "video"
alive_json_fn = "alive.json"
text_con_json = "text.json"
os.makedirs(audio_dir_name,exist_ok=True)
os.makedirs(video_dir_name,exist_ok=True)
local_audio_path = os.path.join(audio_dir_name,"input.mp3")
local_video_path = os.path.join(video_dir_name,"input.mp4")
local_ai_audio_path = os.path.join(audio_dir_name,"ai.mp3")
# text_content = None


if not os.path.isfile(alive_json_fn):
    alive = 0
    with open(alive_json_fn,"w") as f:
        json.dump({"alive":alive},f)
else:
    with open(alive_json_fn,"r") as f:
        alive = int(json.load(f)["alive"])

# Check if "chat_hist" exists in the session state, if not, initialize it as an empty list
if "chat_hist" not in st.session_state:
    st.session_state["chat_hist"] = []
    
    
def write_json(file_path,dict):
    
    with open(file_path,"w") as f:
        json.dump(dict,f)
    
def audio_st(audio_path):
    
    text_content = get_content(audio_path)
    
    return text_content 

# Set Streamlit page configuration
st.set_page_config(page_title="Video Summarizer")
st.header("TubeTalk AI")

source_content = st.radio(
    "Choose The Source : ",
    ["Local Audio Inquiry [chat with audio]","Local Video Inquiry [chat with video(with audio)]","Type Text [chat with text]",
"Youtube Video Inquiry [chat with yt-video]","Visual Inquiry [chat with video(without audio)]"]
)

if source_content=="Local Audio Inquiry [chat with audio]" :
    
    # if os.path.isfile(text_con_json) :os.remove(text_con_json)
    audio_file  = st.text_input("Enter Audio file full Path ... ")
    if audio_file:
        st.write(" Audio Preview:")
        st.audio(audio_file)
        
        if not alive:
            
            text_content = audio_st(audio_file)
            print(text_content)
            with open(alive_json_fn,"w") as f:
                json.dump({"alive":1},f)
            write_json(text_con_json,{"text_content":text_content})
            
elif source_content=="Local Video Inquiry [chat with video(with audio)]":
    
    # if os.path.isfile(text_con_json) :os.remove(text_con_json) 
    video_file  = st.text_input("Enter Video file full Path(with audio) ... ")
    if video_file:
        st.write("Audio Preview:")
        if os.path.isfile(local_audio_path):st.audio(local_audio_path)
        if not alive:
            
            is_exist = convert_video_to_audio(video_file,local_audio_path)
            text_content = audio_st(local_audio_path)
            with open(alive_json_fn,"w") as f:
                json.dump({"alive":1},f)
            write_json(text_con_json,{"text_content":text_content})
    
elif source_content=="Type Text [chat with text]":
    # if os.path.isfile(text_con_json) :os.remove(text_con_json)
    text_content = st.text_input("Type Text ... ")
    with open(alive_json_fn,"w") as f:
            json.dump({"alive":1},f)
    write_json(text_con_json,{"text_content":text_content})
    

# elif source_content=="Youtube Url":

elif source_content=="Youtube Video Inquiry [chat with yt-video]":
    # Input field for YouTube URL
    # if os.path.isfile(text_con_json) :os.remove(text_con_json)
    youtube_url = st.text_input("Enter YouTube URL for Inquiry (with audio): ")
    if youtube_url :
        st.write("Audio Preview:")
        audio_path = download_youtube_video(youtube_url)
        if os.path.isfile(audio_path):st.audio(audio_path)
        if not alive:
            
            text_content = audio_st(audio_path)
            
            with open(alive_json_fn,"w") as f:
                json.dump({"alive":1},f)
            write_json(text_con_json,{"text_content":text_content})
        
else:

    # if os.path.isfile(text_con_json) :os.remove(text_con_json)
    youtube_url = st.text_input("Enter YouTube URL for Inquiry: ")
    video_path = download_youtube_video(youtube_url,audio_or_video="video")
    if video_path:st.video(video_path)
    if youtube_url and not alive:
        
        
            
            print(f"{video_path=}")
            # resize_video(video_path,"demp.mp4")
            
            visual_content = get_visual_content(video_path)
            response = get_generated_response(f"""organize this content  "{visual_content}" """)
            text_content = ""
            for chunk in response:
                text_content+=chunk.text
            
            with open(alive_json_fn,"w") as f:
                json.dump({"alive":1},f)
            write_json(text_con_json,{"text_content":text_content})
        
st.button("Start of Conversation")
if os.path.isfile(text_con_json) and alive:
    with open(text_con_json,"r") as f:
        text_content = json.load(f)["text_content"]
    
    # Input field for asking a question
    question = st.text_input("Ask your Question:", key="input")

    # Button to submit the question
    submit_button = st.button("Get AI Response")

    # Process question and display response
    if question and submit_button:
        response = get_generated_response(f"""{question}  "{text_content}" """)
        st.session_state["chat_hist"].append(("Question", question))
        st.subheader("AI Bot's Response:")
        final_txt = ""
        for chunk in response:
            chunk_text = chunk.text
            final_txt+=chunk_text
        st.write(final_txt)
        st.session_state["chat_hist"].append(("AI Bot", final_txt))
        st.session_state["chat_hist"].append(("sep", "=========="*8))
        text_to_speech(final_txt,language="en",output_file=local_ai_audio_path)
        st.write("Ai Bot Audio Preview:")
        audio_bytes = open(local_ai_audio_path, 'rb').read()
        st.audio(audio_bytes)
        

        # Display chat history
        st.subheader("Chat History:")
        for role, text in st.session_state["chat_hist"]:
            if role != "sep":
                st.write(f" {role} : {text}")
            else:
                st.write(f"{text}")

                
if st.button("End of Conversation"):
    if os.path.isfile(alive_json_fn):os.remove(alive_json_fn)
    if os.path.isfile(text_con_json):os.remove(text_con_json)