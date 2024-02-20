import making_video


def prepare_videos(youtube_link,a):
    #* Download video from youtube
    #making_video.download_video(youtube_link) # ! downloaded_youtube_video.mp4
    
    #* Creating m4 and mp3 clips. 2nd argument used for limitation of how many clips will create (use '*' for all of them)
    #* It puts videos into videos folder
    #* It puts sounds into sounds folder
    #number_of_clips = making_video.video_operations("videos/downloaded_youtube_video.mp4",a)

    #* Create 2 list for clips  
    list_of_videos = making_video.create_list_of_clips(r"videos")
    list_of_sounds = making_video.create_list_of_clips(r"sounds")

    #* Program will process 1 clip at a time with this loop it is better for optimization. 
    #* i variable will take integer values from 0 but clip names uses {i:03d} for minimum 3 digit for ex.: clip000.mp4
    for i in range(len(list_of_videos)):
        #* Getting the clip name for after
        clip_name , _ = str(list_of_videos[i]).split(".") # ! clip000.mp4

        #* Put the current clip into moviepy video format
        clip = making_video.import_clip("videos/"+str(list_of_videos[i]))

        #* Create reverse audio and video 
        making_video.reverse_video_main(f"videos/{list_of_videos[i]}")    # ! clip000-inverted.mp4
        making_video.reverse_audio(f"sounds/{list_of_sounds[i]}")         # ! clip000_reversed.mp3

        #? After from here functions i created returns moviepy video and audio format

        #* While reversing the video sound doesn't reversing and sound gone missing so we should add reverse sound again
        reversed_video = making_video.add_sound_to_video(f"{clip_name}_reversed.mp3",f"{clip_name}-inverted.mp4")

        #* Merge the clip and reversed video. Video starts with first argument, ends with the second.
        merged_video = making_video.merge_videos(clip,reversed_video)  

        #* Resize the video from 16:9 to 9:16. (short video standarts)
        #* (Doing it cropping the video and putting borders)
        resized_video = making_video.resize_video(merged_video)

        #* Adding the chanel logo
        logo_to_video = making_video.add_logo_to_video(resized_video)

        image_to_video = making_video.add_image_to_video(logo_to_video)

        #* First addîng transition video because i am losing sound while i remove green screen.
        transition_step1 = making_video.add_transition((0,0),image_to_video)
        
        #* Adding sound effect of transition.
        transition_step2 = making_video.add_sound_effect(transition_step1)

        #* Creating final form of video in .mp4 format
        n = making_video.create_name()#i:03d
        transition_step2.write_videofile(f"full_videos/{n}.mp4", audio_codec="aac",fps=30) # ! full_clip000.mp4
        # ? .write_videofile(f"videos/full_{clip_name}.mp4", audio_codec="aac") 


# * Delete the unnecessary files
def clear():
    making_video.delete_videos(r"videos")
    making_video.delete_videos(r"sounds")
    

if __name__ == "__main__":
    import time
    s = time.time()

    prepare_videos('https://www.youtube.com/watch?v=FfnMfp8XbOE','*')# ? link and video count
    clear()
    
    e = time.time()
    print("\n"+str(e-s))