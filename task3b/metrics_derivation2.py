""" 
How to use this script:


"""

""" 
https://www.youtube.com/watch?v=-Iwy6vME5jQ&ab_channel=CodewithHZ
Probleme:
welcher winkel wird berechnet? winkel zu welcher geraden? senkrechte oder waagerechte? 
kann sein das er manchmal so manchmal so macht?...

"""

import cv2
import mediapipe as mp
import time
import pandas as pd
import os
import math


#------------------------------------- variables ---------------------------------------
dir_hinten = "../../data/hinten"
dir_seite = "../../data/seite"
dir_csv = "../../data/csv"
dir_tread_frames = "../../data/tread_frames"

columns = ["pronation_winkel", "laufstiel_winkel"]

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

def write_metrics(filepath, filename):
    cap = cv2.VideoCapture(filepath)

    # read csv file containing the coordinates of all keypoints from task2
    csv_filepath = os.path.join(dir_csv, str(filename[:-4]) + '.csv')
    df = pd.read_csv(csv_filepath, index_col=0)

    # read csv file containing the frames at time of tread (nur Laufstiel)
    tread_frames_filepath = os.path.join(dir_tread_frames, str(filename[:-4]) + '_tread_frames.csv')
    tread_frames_df = pd.read_csv(tread_frames_filepath, index_col=0)
    frames_at_time_of_tread = tread_frames_df["frame_at_time_of_tread"].to_numpy()
    print(frames_at_time_of_tread)

    data = []
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

            if frame_count in frames_at_time_of_tread:
                print("--------------")
                row = culculate_metric(df, frame_count, img)
                data.append(row)
                print(data)
                cv2.waitKey(-1)  # wait until any key is pressed

            frame_count+=1
                
    print(data)
    new_df = pd.DataFrame(data, index=range(len(data)), columns=[columns])
    print(new_df)
    new_df.to_csv(str(filename[:-4])+ "_metrics" + ".csv")

def calculate_angle(x1, x2, y1, y2):
    print(x1, y1)
    print(x2, y2)
    delta_y = ((y2) - (y1)) ** 2
    delta_x = ((x2) - (x1)) ** 2
    radian = math.atan2(delta_y, delta_x)
    degrees = radian * (180 / math.pi)
    return degrees

def culculate_metric(df, frame, img):
    foot_index_x, foot_index_y = df.iloc[frame]["32z"], df.iloc[frame]["32y"]
    heel_x, heel_y = df.iloc[frame]["30z"], df.iloc[frame]["30y"]
    angle = calculate_angle(foot_index_x, heel_x, foot_index_y, heel_y)

    """ 
    # adjust coordinates to screen resolution
    # use only this block OR the block above
    h, w, c = img.shape
    foot_index_x_adjusted, foot_index_y_adjusted = int(foot_index_x*w), int(foot_index_y*h)
    heel_x_adjusted, heel_y_adjusted = int(heel_x*w), int(heel_y*h)
    angle = calculate_angle(foot_index_x_adjusted, heel_x_adjusted, foot_index_y_adjusted, heel_y_adjusted) 
    """

    print(angle)
    row = ['', angle] 
    return row

#--------------------------------- main loop ----------------------------------

# loop through all videos with perspective "seite"
for filename in os.listdir(dir_seite):
    filepath = os.path.join(dir_seite, filename)
    print(filename)
    write_metrics(filepath, filename)