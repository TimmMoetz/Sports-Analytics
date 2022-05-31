""" 
How to use this model:

The part of the model that syncs the frames of the two perspectives will 
return two directories: "hinten" and "seite" with videos 
named like runner1_laufen, runner2_joggen etc.
You can change the variable "dir_hinten" and "dir_seite" to the paths where 
you want to store your videos.
Then just run this file, it will return csv files containing relevant keypoint-coordinates 
of all frames of all the videos.
Running this model will take a while, after it finished you can delete the generated 
csv files, that beginn with "incomplete"
"""

import cv2
import mediapipe as mp
import time
import pandas as pd
import os

#------------------------------------- variables ---------------------------------------
dir_hinten = "../../data/hinten"
dir_seite = "../../data/seite"
columns = ["23x", "23y", "23z", "24x", "24y", "24z", "25x", "25y", "25z", 
    "26x", "26y", "26z","27x", "27y", "27z", "28x", "28y", "28z", "29x", "29y", "29z", 
    "30x", "30y", "30z", "31x", "31y", "31z", "32x", "32y", "32z"]

mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils

#--------------------------------------- functions --------------------------------

def display_img(img):
    # display fps
    pTime = 0
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (50,50), cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0), 3)

    # display frame/image
    #resized_img = cv2.resize(img, (675, 1200))   # big screen 
    resized_img = cv2.resize(img, (475, 900))    # small screen
    cv2.imshow("Image", resized_img)
    cv2.waitKey(1) 

def write_keypoints_hinten(filepath, filename):
    cap = cv2.VideoCapture(filepath)
    data = []

    # iterate through frames of video
    while True:
        print("frame:", len(data))
        success, img = cap.read()   # img is one frame/image
        if not success:
            break

        # calculate and draw pose-landmarks
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        cv2.rectangle(img, (0, 0), (1200, 1200), (0, 0, 0), -1)   # anonymization
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)

            row = ['' for i in range(len(columns))] 
            # get id and coordinates of landmarks
            for id, landmark in enumerate(results.pose_landmarks.landmark):
                # see Blaze Pose Keypoint Topology for meaning of id, e.g. id=32 is "left foot index"
                relevant_ids = [23,24,25,26,27,28,29,30,31,32]
                if id in relevant_ids:
                    # save x
                    row[columns.index(str(id)+'x')] = landmark.x

                    # save y to calculate the average later except for the foot tips, because it's 
                    # difficult to see them from behind
                    if id != 31 and id != 32:
                        row[columns.index(str(id)+'y')] = landmark.y
                
            data.append(row)
            display_img(img)

    df = pd.DataFrame(data, index=range(len(data)), columns=[columns])
    print(df)   
    df.to_csv("incomplete-" + str(filename[:-4])+ ".csv")

def write_keypoints_seite(filepath, filename):
    cap = cv2.VideoCapture(filepath)
    df = pd.read_csv('incomplete-' + str(filename[:-4]) + '.csv', index_col=0)
    print(df)

    frame_count = 0
    # iterate through frames of video
    while True:
        print("frame:", frame_count)
        success, img = cap.read()   # img is one frame/image
        if not success:    # gets triggered when all frames have been iterated
            print("completed")
            # drop rows with missing values, in case the videos of the 
            # two perspectives have different numbers of frames
            df = df.dropna()
            break

        # stop when all frames of the other perspective got iterated
        if frame_count >= len(df.index):
            print("completed with cut")
            print(len(df.index))
            break

        # calculate and draw pose-landmarks
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        cv2.rectangle(img, (0, 0), (1200, 1200), (0, 0, 0), -1)   # anonymization
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)

            row = df.loc[frame_count].values.flatten().tolist()
            # get id and coordinates of landmarks
            for id, landmark in enumerate(results.pose_landmarks.landmark):
                # see Blaze Pose Keypoint Topology for meaning of id, e.g. id=32 is "left foot index"
                relevant_ids = [23,24,25,26,27,28,29,30,31,32]
                if id in relevant_ids:
                    # save x as z of other perspective
                    row[columns.index(str(id)+'z')] = landmark.x
                    
                    # save y for the foot tips, because you can see them best from the side
                    if id == 31 or id == 32:
                        row[columns.index(str(id)+'y')] = landmark.y

                    # for every other keypoint: save the average of y from both perspectives
                    else:
                        y_of_perspective_hinten = df.loc[frame_count][str(id)+"y"]
                        average = (float(y_of_perspective_hinten) + landmark.y) / 2
                        row[columns.index(str(id)+'y')] = average

            df.loc[frame_count] = row
            display_img(img)
            frame_count+=1
                
    print(df)
    df.to_csv(str(filename[:-4])+ ".csv")

#--------------------------------- main loops ----------------------------------

# first loop through all videos with perspective "hinten"
for filename in os.listdir(dir_hinten):
    filepath = os.path.join(dir_hinten, filename)
    print(filename)
    write_keypoints_hinten(filepath, filename)

# then loop through all videos with perspective "seite"
for filename in os.listdir(dir_seite):
    filepath = os.path.join(dir_seite, filename)
    print(filename)
    write_keypoints_seite(filepath, filename)