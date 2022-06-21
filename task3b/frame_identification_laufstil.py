""" 
How to use this model:


"""

import cv2
import mediapipe as mp
import pandas as pd
import os

#------------------------------------- variables ---------------------------------------
dir_seite = "../../data/seite_todo"
dir_csv = "../../data/csv"
dir_tread_frames = "../../data/tread_frames_laufstil"

mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils

#--------------------------------------- functions --------------------------------

def display_img(img):
    # display frame/image
    #resized_img = cv2.resize(img, (675, 1200))   # big screen 
    resized_img = cv2.resize(img, (475, 900))    # small screen
    cv2.imshow("Image", resized_img)
    cv2.waitKey(1) 

def identify_tread(filepath, filename):
    cap = cv2.VideoCapture(filepath)

    csv_filepath = os.path.join(dir_csv, str(filename[:-4]) + '.csv')
    df = pd.read_csv(csv_filepath, index_col=0)

    # filter for the top 100 highest values of '32z' (left foot)
    canidat_df_left = df.nlargest(n=100, columns=['32z'], keep='all')
    canidat_frames_at_time_of_tread_left = canidat_df_left.index.array
    print(canidat_frames_at_time_of_tread_left)

    # filter for the top 100 highest values of '31z' (right foot)
    canidat_df_right = df.nlargest(n=100, columns=['31z'], keep='all')
    canidat_frames_at_time_of_tread_right = canidat_df_right.index.array
    print(canidat_frames_at_time_of_tread_right)

    data = dict( left = [], right = [] )
    frame_count = 0
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

            if frame_count in canidat_frames_at_time_of_tread_left:
                print("--------------")
                key = cv2.waitKey(-1)  # wait until any key is pressed
                if key == ord('s'):  # save frame
                    data["left"].append(frame_count)
                if key == ord('p'):   # save previous frame
                    data["left"].append(previous_canidat_frame)
                # if any other key is pressed no frame gets saved
                previous_canidat_frame = frame_count
                print(data)

            if frame_count in canidat_frames_at_time_of_tread_right:
                print("--------------")
                key = cv2.waitKey(-1)  # wait until any key is pressed
                if key == ord('s'):  # save frame
                    data["right"].append(frame_count)
                if key == ord('p'):   # save previous frame
                    data["right"].append(previous_canidat_frame)
                # if any other key is pressed no frame gets saved
                previous_canidat_frame = frame_count
                print(data)
            frame_count+=1
                
    print(data)
    new_df = pd.DataFrame({k:pd.Series(v) for k,v in data.items()}, dtype=pd.Int64Dtype())
    print(new_df)
    tread_frames_filepath = os.path.join(dir_tread_frames, str(filename[:-4])+ "_tread_frames_laufstil.csv")
    new_df.to_csv(tread_frames_filepath)

#--------------------------------- main loop ----------------------------------

# loop through all videos with perspective "seite"
for filename in os.listdir(dir_seite):
    filepath = os.path.join(dir_seite, filename)
    print(filename)
    identify_tread(filepath, filename)