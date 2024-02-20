import scenecut_extractor
import json
from moviepy.editor import *
import moviepy.video.fx.all as vfx
from os import listdir
from pytube import YouTube
from os import remove,listdir
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, ImageSequenceClip
import numpy as np
import os
from datetime import timedelta, datetime
from glob import glob
from tqdm import tqdm
import shutil
import random
import string

from natsort import natsorted
from moviepy.editor import *



def video_operations(video_name,how_many_clips):

    scext = scenecut_extractor._scenecut_extractor.ScenecutExtractor(video_name)
    scext.calculate_scenecuts(0.2)
    scenes = json.loads(scext.get_as_json())
    
    with open("scenes.json","w") as scene_file:
        scene_file.write((scext.get_as_json()))

    first_element = True
    
    v_clip = VideoFileClip(video_name)
    v_clip.audio.write_audiofile("sounds/audio_of_video.mp3")
    s_clip = AudioFileClip("sounds/audio_of_video.mp3")
    a = 0
    counter = 0
    
    if how_many_clips == "*":
        clip_quantity = len(scenes)
    else:
        clip_quantity = how_many_clips

    for i in range(clip_quantity):
        try:
            if first_element:

                v_clip = v_clip.subclip(0, float(scenes[0]["pts_time"]))
                s_clip = s_clip.subclip(0,float(scenes[0]["pts_time"]))
                v_clip = v_clip.set_audio(s_clip)
                v_clip.write_videofile("videos/clip000.mp4", audio_codec="aac")
                s_clip.write_audiofile("sounds/clip000.mp3")
                first_element = False
                counter+=1

            else:
                
                if (float(scenes[i]["pts_time"])-float(scenes[i-1]["pts_time"])) < 2:
                    a+=1
                    continue

                else:

                    v_clip = VideoFileClip(video_name)
                    v_clip.audio.write_audiofile("sounds/audio_of_video.mp3")
                    s_clip = AudioFileClip("sounds/audio_of_video.mp3")

                    v_clip = v_clip.subclip(float(scenes[i-1-a]["pts_time"]), float(scenes[i]["pts_time"]))
                    s_clip = s_clip.subclip(float(scenes[i-1-a]["pts_time"]), float(scenes[i]["pts_time"]))
                    v_clip = v_clip.set_audio(s_clip)
                    v_clip.write_videofile(f"videos/clip{i:03d}.mp4", audio_codec="aac")
                    s_clip.write_audiofile(f"sounds/clip{i:03d}.mp3")
                    a = 0
                    counter+=1
        
        except Exception as e:
            print(e)
    return counter

def import_clip(name):
    return VideoFileClip(name)


def add_sound_to_video(sound_name,video_name):
    v_clip = VideoFileClip(f"videos/{video_name}")
    s_clip = AudioFileClip(f"sounds/{sound_name}")
    v_clip = v_clip.set_audio(s_clip)
    return v_clip


def merge_videos(v1,v2):
    final = concatenate_videoclips([v1,v2])
    return final


def resize_video(video,name="",x=0,y=0):
    croped_clip = vfx.crop(video, x1=300, y1=0, width=680, height=720)#1280*720
    clip_with_borders = croped_clip.margin(top=360,bottom=200,right=20,left=20,color=(255,255,255))

    return clip_with_borders
    """
    1280 720          //16:9

    680     720             
     v +40   v +560  ->   top=360 bottom=200
    720     1280     //9:16
    """
    #system(f"ffmpeg -i {video}  -vf scale={x}:{y} -preset slow -crf 18 final_videos/resized_{name}.mp4")

def create_list_of_clips(path):
    a = list()
    for files in listdir(path):
        files = str(files)

        try:
            temp = files[:-7]
            if temp == "clip":
                a.append(files)
        except RuntimeError as e:
            print(e)

    a.sort()
    return a


def add_logo_to_video(video):
    logo = (ImageClip("logo_new.png")
            .set_duration(video.duration)
            .resize(height=100) # if you need to resize...
            .margin(left=0, top=10, opacity=0) # (optional) logo-border padding
            .set_pos(("left","top")))

    final = CompositeVideoClip([video, logo])

    return final

def add_image_to_video(video):
    image = (ImageClip("watch.png")
            .set_duration(video.duration)
            .resize(height=250) # if you need to resize...
            .margin(left=0, top=100, opacity=0) # (optional) logo-border padding
            .set_pos(("top")))

    final = CompositeVideoClip([video, image])

    return final

def download_video(link):
    youtubeObject = YouTube(link,use_oauth=True,allow_oauth_cache=True)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        youtubeObject.download(filename="videos/downloaded_youtube_video.mp4")
    except:
        print("An error has occurred")
    print("Download is completed successfully")

def delete_videos(path):
    try:
            
        for files in listdir(path):
            remove(f"{path}/{files}")
            print(f"{files} removed")

    except Exception as e:
         print(e)

def reverse_audio(filename):
    original = AudioSegment.from_mp3(filename)
    reversed = original.reverse()

    filename, _ = filename.split(".")

    reversed.export(filename+"_reversed.mp3")


SAVING_FRAMES_PER_SECOND = 30

def format_timedelta(td):
    """Utility function to format timedelta objects in a cool way (e.g 00:00:20.05) 
    omitting microseconds and retaining milliseconds"""
    result = str(td)
    #print(result)
    try:
        result, ms = result.split(".")
        #print(result)
    except ValueError:
        return result + ".00".replace(":", "-")
    ms = int(ms)
    ms = round(ms / 1e4)
    return f"{result}.{ms:02}".replace(":", "-")
    

def extract_frames(video_file, verbose=1):
    # load the video clip
    video_clip = VideoFileClip(video_file)
    # make a folder by the name of the video file
    
    filename, _ = os.path.splitext(video_file)
    
    if not os.path.isdir(filename):
        os.mkdir(filename)
    # if the SAVING_FRAMES_PER_SECOND is above video FPS, then set it to FPS (as maximum)
    saving_frames_per_second = min(video_clip.fps, SAVING_FRAMES_PER_SECOND)
    # if SAVING_FRAMES_PER_SECOND is set to 0, step is 1/fps, else 1/SAVING_FRAMES_PER_SECOND
    step = 1 / video_clip.fps if saving_frames_per_second == 0 else 1 / saving_frames_per_second
    iteration = np.arange(0, video_clip.duration, step)
    if verbose:
        iteration = tqdm(iteration, desc="Extracting video frames")
    # iterate over each possible frame
    for current_duration in iteration:
        # format the file name and save it
        frame_duration_formatted = format_timedelta(timedelta(seconds=current_duration)).replace(":", "-")
        frame_filename = os.path.join(filename, f"frame{frame_duration_formatted}.jpg")
        # save the frame with the current duration
        video_clip.save_frame(frame_filename, current_duration)
    return filename, video_clip.fps

def reverse_video(frames_path, video_fps, remove_extracted_frames=True):
    frame_files = glob(os.path.join(frames_path, "*"))
    # sort by duration in descending order
    frame_files = sorted(frame_files, key=lambda d: datetime.strptime(d.split("frame")[1], "%H-%M-%S.%f.jpg"), reverse=True)
    
    # calculate the FPS, getting the minimum between the original FPS and the parameter we set
    saving_frames_per_second = min(video_fps, SAVING_FRAMES_PER_SECOND)
    if saving_frames_per_second == 0:
        # if the parameter is set to 0, automatically set it to the original video fps
        saving_frames_per_second = video_fps
    print("Saving the video with FPS:", saving_frames_per_second)
    # load the frames into a image sequence clip (MoviePy)
    image_sequence_clip = ImageSequenceClip(frame_files, fps=saving_frames_per_second)
    # write the video file to disk
    output_filename = f"{frames_path}-inverted.mp4"
    image_sequence_clip.write_videofile(output_filename)
    if remove_extracted_frames:
        # if set to True, then remove the folder that contain the extracted frames
        shutil.rmtree(frames_path)



def reverse_video_main(video_file):
    frames_folder_path, video_fps = extract_frames(video_file)
    reverse_video(frames_folder_path, video_fps=video_fps)

def frames_to_video():
    fps = 24

    file_list = glob.glob('*.png')  # Get all the pngs in the current directory
    file_list_sorted = natsorted(file_list,reverse=False)  # Sort the images

    clips = [ImageClip(m).set_duration(0.035)
            for m in file_list_sorted]

    concat_clip = concatenate_videoclips(clips, method="compose")
    concat_clip.write_videofile("test4.mp4", fps=fps,)

def add_transition(pos,video):#(420,0)
    transition = VideoFileClip(r"FFF.mov",has_mask=True,target_resolution=(1280,720))
    transition = transition.set_position(pos)
    transition = transition.set_start(float(video.duration)/2)

    final_video = CompositeVideoClip([video,transition])
    return final_video

def add_sound_effect(v_clip):
    s_clip = VideoFileClip(r"reverse_card.mp4")
    s_clip = s_clip.audio
    s_clip = s_clip.set_start(float(v_clip.duration)/2)
    
    fn_audio = CompositeAudioClip([v_clip.audio,s_clip])
    v_clip.audio = fn_audio

    return v_clip

def create_name():
    name = "ika_"
    for _ in range(11):
        name += str(random.choice(string.ascii_letters + string.digits)) 
    
    return name



