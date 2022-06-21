""" 
How to use this model:


"""

import cv2
import mediapipe as mp
import pandas as pd
import os

#------------------------------------- variables ---------------------------------------
dir_hinten = "../../data/hinten_todo"
dir_tread_frames = "../../data/tread_frames_pronation"

mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils


#--------------------------------------- functions --------------------------------

def display_img(img):
    # display frame/image
    #resized_img = cv2.resize(img, (675, 1200))   # big screen 
    resized_img = cv2.resize(img, (475, 900))    # small screen
    cv2.imshow("Image", resized_img)

def identify_tread(filepath, filename):
    cap = cv2.VideoCapture(filepath)

    data = dict( left = [], right = [] )
    frame_count = 0
    pause_at_next_frame = False

    # iterate through frames of video
    while True:
        print("frame:", frame_count)
        success, img = cap.read()   # img is one frame/image
        if not success:    # gets triggered when all frames have been iterated
            print("completed")
            break
        
        # calculate and draw pose-landmarks
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        cv2.rectangle(img, (0, 0), (1200, 900), (0, 0, 0), -1)   # anonymization
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            display_img(img)

            if pause_at_next_frame:
                pause_at_next_frame = pause_video(data, frame_count)
                print(data)
                print(len(data["left"]))
                print(len(data["right"]))

            key = cv2.waitKey(1)
            if key == ord('p'):
                pause_at_next_frame = pause_video(data, frame_count)
                print(data)
                print(len(data["left"]))
                print(len(data["right"]))
            frame_count+=1
                
    print(data)
    new_df = pd.DataFrame({k:pd.Series(v) for k,v in data.items()}, dtype=pd.Int64Dtype())
    print(new_df)
    tread_frames_filepath = os.path.join(dir_tread_frames, str(filename[:-4])+ "_tread_frames_pronation.csv")
    new_df.to_csv(tread_frames_filepath)

def pause_video(data, frame_count):
    key = cv2.waitKey(-1) # wait until any key is pressed
    if key == ord('p'):   # pause at next frame
        return True
    if key == ord('s'):   # save frame and pause at next frame
        data["left"].append(frame_count)
        return True
    if key == ord('d'):   # save frame and pause at next frame
        data["right"].append(frame_count)
        return True
    if key == ord('q'):   # delete last entry in "left"
        data["left"].pop()
        return True
    if key == ord('w'):   # delete last entry in "right"
        data["right"].pop()
        return True
    else:                 # continue
        return False

#--------------------------------- main loop ----------------------------------

# loop through all videos with perspective "hinten"
for filename in os.listdir(dir_hinten):
    filepath = os.path.join(dir_hinten, filename)
    print(filename)
    identify_tread(filepath, filename)