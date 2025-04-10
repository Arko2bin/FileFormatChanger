import shutil
from io import BytesIO
from rembg import remove
from moviepy.video.fx.speedx import speedx
import streamlit as st
from moviepy.editor import *
from proglog import ProgressBarLogger
from zipfile import ZipFile
from PIL import Image
from gtts import gTTS
import pytesseract
import subprocess
import os

class MyBarLogger(ProgressBarLogger):
    def callback(self, **changes):
        # Every time the logger message is updated, this function is called with
        # the `changes` dictionary of the form `parameter: new value`.
        for (parameter, value) in changes.items():
            print('Parameter %s is now %s' % (parameter, value))

    def bars_callback(self, bar, attr, value, old_value=None):
        # Every time the logger progress is updated, this function is called
        percentage = (value / self.bars[bar]['total']) * 100
        status.progress(int(percentage))

st.set_page_config(page_title='File Converter App',layout="wide",page_icon="https://cdn.movavi.io/pages/0012/67/f97f4053080a1d1ecc3e23c4095de7e73522ea17.png")
logger = MyBarLogger()
hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                header {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
set_background = """
                <style>
                .stApp {
                     background-image: url("https://i.pinimg.com/originals/13/83/07/138307c749c670d6d5ebffcbf15fe025.jpg");
                     background-size: cover;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
#st.markdown(set_background, unsafe_allow_html=True)

def getEnv():
    if 'mount' in os.getcwd():
        env = "Production"
    else:
        env = "Local"
    return env


def video_filesize(video):
    if(round(video.filesize / (1024*1024*1024),2) > 1):
        return str(round(video.filesize / (1024 * 1024 * 1024),2)) + "GB"
    elif(round(video.filesize / (1024*1024),2) > 1):
        return str(round(video.filesize / (1024 * 1024), 2)) + "MB"
    else:
        return str(round(video.filesize / (1024), 2)) + "KB"

def video2audio(video):
    output = "audio_file.wav"
    video = VideoFileClip(video)
    audio = video.audio
    audio.write_audiofile(output, logger=logger)
    st.success("Successful Conversion!")
    st.audio(output)
    audio.close()
    video.close()
    os.remove(output)

def mix_vid(video,audio):
    result = False
    Video = VideoFileClip(video)
    Audio = AudioFileClip(audio)
    print(Video.size)
    orientation = st.selectbox("Choose output video orientation",["--select--","Landscape","Potrait"])
    if(orientation != '--select--'):
        if (orientation == "Landscape"):
            if (Video.size[0] > Video.size[1]):
                Video = Video.resize(Video.size)
            else:
                Video = Video.resize((Video.size[1], Video.size[0]))
        elif (orientation == "Potrait"):
            if (Video.size[0] < Video.size[1]):
                Video = Video.resize(Video.size)
            else:
                Video = Video.resize((Video.size[1], Video.size[0]))
        vid_duration = Video.duration
        audio_duration = Audio.duration
        output = 'final_video.mp4'
        final_clip = None
        if (vid_duration < audio_duration or vid_duration > audio_duration):
            conv_type = ['--Select--', 'Merge files anyway', 'Cut the extra portion and merge']
            select_type = st.selectbox("Your video and audio length are not similar choose the below action: ",conv_type)
            if(select_type != "--Select--"):
                if(select_type == 'Merge files anyway'):
                    Video = Video.fx(speedx, vid_duration / audio_duration)
                    final_clip = Video.set_audio(Audio)
                elif(select_type == 'Cut the extra portion and merge'):
                    if(vid_duration > audio_duration):
                        Video = Video.subclip(0,Audio.duration)
                        final_clip = Video.set_audio(Audio)
                    elif(audio_duration > vid_duration):
                        Audio = Audio.subclip(0,Video.duration)
                        final_clip = Video.set_audio(Audio)
        else:
            final_clip = Video.set_audio(Audio)
        if(final_clip):
            final_clip.write_videofile(output, logger=logger)
            st.success("Successfull conversion")
            st.video(output)  # shows the video
            os.remove(output)
            Video.close()
            Audio.close()
            result = True
    return result

def Cut_Videos(video,start_time,end_time):
    video = VideoFileClip(video)
    if (start_time.isnumeric() and end_time.isnumeric()):
        if(float(start_time) > float(end_time)):
            st.error("Start time can not be greater than end time")
        elif(float(end_time) > video.duration):
            st.error("End time can not be greater than entire video duration")
        else:
            video = video.subclip(float(start_time), float(end_time))
            video.write_videofile("cutted file.mp4", logger=logger)
            st.success("Cutting successfull")
            st.video("cutted file.mp4")
            os.remove("cutted file.mp4")
            video.close()
            return True
def run_yt_dlp(command):

    # Start the subprocess and capture the output
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    t = st.empty()
    # Read the output in real-time and print it
    for line in iter(process.stdout.readline, ''):
        print(line, end='')  # Print the line from the process
        t.write(line)

    # Handle any errors
    for line in iter(process.stderr.readline, ''):
        print(f"ERROR: {line}", end='')  # Print any error messages
        t.write(f"ERROR: {line}")

    for file in os.listdir():
        if('.webm' in file or '.mp4' in file):
            st.video(file)
            os.remove(file)
        if('.mp3' in file or '.wav' in file or '.opus' in file):
            st.audio(file)
            os.remove(file)

    process.stdout.close()
    process.stderr.close()
    process.wait()
def yt_dlp(stream,url):
    cwd = os.getcwd()
    # Assuming yt-dlp is in the current directory, or provide the full path to the yt-dlp executable
    yt_dlp_path = os.path.join(cwd, "yt-dlp.exe")
    scripts = {
        'Audio Only':f'{yt_dlp_path} -x {url}',
        'Video only Best quality availabe': f'{yt_dlp_path} -f "bestvideo[height<=1080]" {url}',
        'Video & Audio': f'{yt_dlp_path} -f "best[height<=1080]" {url}',
    }
    run_yt_dlp(command=scripts[stream])

with st.container():
    st.success("Use our desktop app for downloading Youtube Videos")
    st.title("Format Changer App")
    st.header("Hi I am your app to change the format of your files: ")
    st.write("---")


with st.container():
    st.header("Choose the service: ")
    left,right = st.columns(2)
    with left:
        st.subheader("Convert video files to audio files: ")
        video_file = st.file_uploader("Choose a video file", type=['mp4', 'avi'])
        if(video_file):
            video = video_file.name
            with open(video,"wb") as f:
                f.write(video_file.read())
            status = st.progress(0)
            video2audio(video)
            os.remove(video_file.name)

        st.subheader("Combine images to a video")
        images = st.file_uploader("Choose the image files: ",type = ['png','jpeg','jpg'],accept_multiple_files=True)
        clips = []
        if(images):
            for image in images:
                with open(image.name,'wb') as source:
                    source.write(image.read())
                image = Image.open(image.name)
                image.resize((1280,720))
                image.save('temp_image.png')
                clips.append(ImageClip('temp_image.png').set_duration(5))
                os.remove('temp_image.png')
            status = st.progress(0)
            concat_clip = concatenate_videoclips(clips, method="compose")
            concat_clip.write_videofile("output.mp4", codec="libx264" ,fps=24,logger=logger)
            st.video('output.mp4')
            os.remove('output.mp4')
            for image in images:
                os.remove(image.name)
    with right:
        st.subheader("Combine audio and video files: ")
        video_file = st.file_uploader("Choose your video file: ",type=['mp4','avi'])
        audio_file = st.file_uploader("Choose your audio file: ",type=['mp3','wav'])
        if('video.mp4' not in os.listdir()):
            if (video_file):
                video = "video.mp4"
                with open('video.mp4', "wb") as f:
                    f.write(video_file.read())
        if('audio.wav' not in os.listdir()):
            if (audio_file):
                audio = "audio.wav"
                with open('audio.wav', "wb") as f:
                    f.write(audio_file.read())

        if('video.mp4' in os.listdir()  and 'audio.wav' in os.listdir()):
            st.success("Successfully got the files now processing for results...")
            status = st.progress(0)
            video = 'video.mp4'
            audio = 'audio.wav'
            result = mix_vid(video,audio)
            if(result):
                os.remove(video)
                os.remove(audio)

with st.container():
    left,right = st.columns(2)
    with left:
        st.subheader("Join Videos:")
        videos = st.file_uploader(label="Upload the video files",type=['mp4','avi'],accept_multiple_files=True)
        if(videos):
            clips = []
            counter = 0
            for video in videos:
                with open("subclip"+str(counter)+".mp4",'wb') as f:
                    f.write(video.read())
                clips.append(VideoFileClip("subclip"+str(counter)+".mp4"))
                counter += 1
            output = "subclip"+str(counter)+"_joined.mp4"
            final = concatenate_videoclips(clips, method='compose')
            status = st.progress(0)
            final.write_videofile(output, logger=logger)
            st.video(output)
            os.remove(output)
            counter = 0
            for video in videos:
                os.remove("subclip"+str(counter)+".mp4")
                counter += 1

    with right:
        st.subheader("Cut videos:")
        result = ""
        start_time = ""
        end_time = ""
        offline_file = st.file_uploader(label="Upload your video file",type=['mp4','avi'])
        if(offline_file and "cutter.mp4" not in os.listdir()):
            video = "cutter.mp4"
            with open(video, "wb") as f:
                f.write(offline_file.read())
            st.video("cutter.mp4")
        if("cutter.mp4" in os.listdir()):
            start_time = st.text_input("Enter start time(s)")
            end_time = st.text_input("Enter end time(s)")
        if("cutter.mp4" in os.listdir() and start_time and end_time):
            status = st.progress(0)
            result = Cut_Videos("cutter.mp4",start_time,end_time)
        if (result == True):
            os.remove("cutter.mp4")

with st.container():
    st.header("AI Tools: ")
    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Convert Image to text:")
        Image_file = st.file_uploader("Upload your image file here", type=['png', 'jpeg', 'jpg'])
        if (Image_file):
            lang = st.selectbox("Choose your image language",['--select--','English','Bengali','Hindi'])
            if(lang != "--select--"):
                if(lang == 'English'):
                    lang = 'eng'
                    vlang = 'en'
                elif(lang == 'Bengali'):
                    lang = 'ben'
                    vlang = 'bn'
                elif (lang == 'Hindi'):
                    lang = 'hin'
                    vlang = 'hi'
                if (getEnv() == 'Local'):  # offline mode
                    image = Image.open(BytesIO(Image_file.read()))
                    pytesseract_zip = st.file_uploader("Upload your pytesseract file", type=['zip'])
                    if (pytesseract_zip):
                        with open(pytesseract_zip.name, 'wb') as pytz:
                            pytz.write(pytesseract_zip.read())
                        with ZipFile(pytesseract_zip, 'r') as zipFile:
                            zipFile.extractall(os.getcwd() + "\\" + pytesseract_zip.name.replace(".zip", ''))
                            os.remove(pytesseract_zip.name)
                        pytesseract.pytesseract.tesseract_cmd = os.getcwd() + "\\" + pytesseract_zip.name.replace(".zip",
                                                                                                                  '') + "\\tesseract.exe"
                        txt = pytesseract.image_to_string(image, lang=lang)
                        st.success("Conversion successfull")
                        st.code(txt)
                        if(st.button("Read Out:loud_sound:")):
                            context = gTTS(text=txt,slow=False,lang=vlang)
                            context.save('t2v.mp3')
                            st.audio('t2v.mp3')
                            os.remove('t2v.mp3')
                        shutil.rmtree(os.getcwd() + "\\" + pytesseract_zip.name.replace(".zip", ''))
                else:
                    image = Image.open(BytesIO(Image_file.read()))
                    txt = pytesseract.image_to_string(image, lang=lang)
                    st.success("Conversion successfull")
                    st.code(txt)
                    if (st.button("Read Out:loud_sound:")):
                        context = gTTS(text=txt, slow=False, lang=vlang)
                        context.save('t2v.mp3')
                        st.audio('t2v.mp3')
                        os.remove('t2v.mp3')
                image.close()
    with col2:
        st.subheader("Image Background remover")
        image_file = st.file_uploader("Upload the image file",type=['jpg','jpeg','png'])
        if(image_file):
            image = Image.open(BytesIO(image_file.read()))
            output = remove(image)
            st.image(output)
            st.success("Success!")

#with st.container():
 #   st.header("Youtube Video Downloader")
  #  link = st.text_input("Enter Youtube Url and hit enter")
   # if(link):
    #    streams = ['--Choose Stream--','Audio Only','Video & Audio','Video only Best quality availabe']
     #   stream = st.selectbox("Choose Video Stream: ",streams)
      #  if(stream != '--Choose Stream--'):
       #     yt_dlp(stream=stream,url=link)

with st.container():
    st.write("---")
    left,middle,right_middle,right = st.columns(4)
    with left:
        st.subheader("Developer Contact: ")
        st.write("Contact us: cosmosbeta99@gmail.com")
    with middle:
        st.subheader("Explore our channel")
        st.write("[Check out here>](https://www.youtube.com/c/robin2bin)")
    with right_middle:
        st.subheader("Issue on the website?")
        st.write("Try our desktop app version: ")
        st.write("[Download from here](https://drive.google.com/file/d/1DG7a5b1qiz3MBpWHjUBfey8HhywIiWd6/view?usp=sharing)")
    with right:
        st.image("https://yt3.ggpht.com/ytc/AMLnZu-iZi_tq1cWBc90QKMCe3WSRXDn7L_ny9i57CSj=s900-c-k-c0x00ffffff-no-rj",width=200)
